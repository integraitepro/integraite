"""
Incident service layer
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case
from sqlalchemy.orm import selectinload
import logging

from app.models.incident import Incident, IncidentTimeline, IncidentStatus, IncidentSeverity
from app.models.user import OrganizationMember
from app.services.servicenow_client import servicenow_service

logger = logging.getLogger(__name__)


class IncidentService:
    """Service for managing incidents"""
    
    def __init__(self):
        pass
    
    async def sync_servicenow_incidents(
        self, 
        organization_id: int,
        db: AsyncSession,
        limit: int = 100
    ) -> List[Incident]:
        """
        Sync incidents from ServiceNow and store/update in database
        """
        try:
            # Fetch incidents from ServiceNow
            servicenow_incidents = await servicenow_service.sync_incidents(limit=limit)
            
            if not servicenow_incidents:
                logger.info("No incidents retrieved from ServiceNow")
                return []
            
            synced_incidents = []
            
            for sn_incident in servicenow_incidents:
                source_alert_id = sn_incident.get('source_alert_id')
                if not source_alert_id:
                    continue
                
                # Check if incident already exists
                result = await db.execute(
                    select(Incident).where(
                        and_(
                            Incident.organization_id == organization_id,
                            Incident.source_alert_id == source_alert_id
                        )
                    )
                )
                existing_incident = result.scalar_one_or_none()
                
                if existing_incident:
                    # Update existing incident
                    updated = await self._update_incident_from_servicenow(
                        existing_incident, sn_incident, db
                    )
                    if updated:
                        synced_incidents.append(existing_incident)
                else:
                    # Create new incident
                    new_incident = await self._create_incident_from_servicenow(
                        organization_id, sn_incident, db
                    )
                    if new_incident:
                        synced_incidents.append(new_incident)
            
            await db.commit()
            logger.info(f"Synced {len(synced_incidents)} incidents from ServiceNow")
            return synced_incidents
            
        except Exception as e:
            logger.error(f"Error syncing ServiceNow incidents: {e}")
            await db.rollback()
            return []
    
    async def _create_incident_from_servicenow(
        self,
        organization_id: int,
        sn_incident: Dict[str, Any],
        db: AsyncSession
    ) -> Optional[Incident]:
        """Create a new incident from ServiceNow data"""
        try:
            incident = Incident(
                organization_id=organization_id,
                title=sn_incident.get('title', 'Unknown Incident'),
                description=sn_incident.get('description', ''),
                short_description=sn_incident.get('short_description', ''),
                severity=sn_incident.get('severity', 'medium'),
                status=sn_incident.get('status', 'investigating'),
                category=sn_incident.get('category', 'Unknown'),
                source_system=sn_incident.get('source_system', 'ServiceNow'),
                source_alert_id=sn_incident.get('source_alert_id'),
                affected_services=sn_incident.get('affected_services', []),
                customer_impact=sn_incident.get('customer_impact', False),
                detection_time=sn_incident.get('detection_time') or datetime.now(timezone.utc),
                resolution_time=sn_incident.get('resolution_time'),
                created_at=datetime.now(timezone.utc),
                updated_at=sn_incident.get('updated_at') or datetime.now(timezone.utc)
            )
            
            db.add(incident)
            await db.flush()  # Get incident.id
            
            # Create initial timeline entry
            timeline_entry = IncidentTimeline(
                incident_id=incident.id,
                entry_type="servicenow_sync",
                title="Incident Synchronized from ServiceNow",
                description=f"Incident {sn_incident.get('source_alert_id')} synchronized from ServiceNow",
                source="ServiceNow",
                source_id=sn_incident.get('source_alert_id'),
                occurred_at=incident.detection_time,
                entry_metadata=sn_incident.get('servicenow_data', {})
            )
            db.add(timeline_entry)
            
            logger.info(f"Created new incident from ServiceNow: {sn_incident.get('source_alert_id')}")
            return incident
            
        except Exception as e:
            logger.error(f"Error creating incident from ServiceNow data: {e}")
            return None
    
    async def _update_incident_from_servicenow(
        self,
        incident: Incident,
        sn_incident: Dict[str, Any],
        db: AsyncSession
    ) -> bool:
        """Update existing incident with ServiceNow data"""
        try:
            updated = False
            
            # Check if any fields need updating
            fields_to_update = {
                'title': sn_incident.get('title'),
                'description': sn_incident.get('description'),
                'short_description': sn_incident.get('short_description'),
                'severity': sn_incident.get('severity'),
                'status': sn_incident.get('status'),
                'category': sn_incident.get('category'),
                'affected_services': sn_incident.get('affected_services'),
                'customer_impact': sn_incident.get('customer_impact'),
                'resolution_time': sn_incident.get('resolution_time'),
                'updated_at': sn_incident.get('updated_at') or datetime.now(timezone.utc)
            }
            
            for field, new_value in fields_to_update.items():
                if new_value is not None and getattr(incident, field) != new_value:
                    setattr(incident, field, new_value)
                    updated = True
            
            if updated:
                # Create timeline entry for update
                timeline_entry = IncidentTimeline(
                    incident_id=incident.id,
                    entry_type="servicenow_update",
                    title="Incident Updated from ServiceNow",
                    description=f"Incident {sn_incident.get('source_alert_id')} updated from ServiceNow",
                    source="ServiceNow",
                    source_id=sn_incident.get('source_alert_id'),
                    occurred_at=datetime.now(timezone.utc),
                    entry_metadata=sn_incident.get('servicenow_data', {})
                )
                db.add(timeline_entry)
                
                logger.info(f"Updated incident from ServiceNow: {sn_incident.get('source_alert_id')}")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error updating incident from ServiceNow data: {e}")
            return False
    
    async def get_incidents_for_organization(
        self,
        organization_id: int,
        db: AsyncSession,
        sync_from_servicenow: bool = True,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Incident]:
        """
        Get incidents for organization, optionally syncing from ServiceNow first
        """
        try:
            # Sync from ServiceNow if requested and available
            if sync_from_servicenow:
                try:
                    synced_count = len(await self.sync_servicenow_incidents(organization_id, db, limit=100))
                    logger.info(f"Synced {synced_count} incidents from ServiceNow")
                except Exception as e:
                    logger.warning(f"ServiceNow sync failed, proceeding with database incidents: {e}")
            
            # Build query filters
            filters = [Incident.organization_id == organization_id]
            
            if severity:
                filters.append(Incident.severity == severity)
            
            if status:
                # Map frontend status to backend status
                status_mapping = {
                    "investigating": "investigating",
                    "remediating": "resolving",
                    "resolved": "resolved",
                    "closed": "closed"
                }
                backend_status = status_mapping.get(status, status)
                if backend_status == "resolving":
                    filters.append(or_(Incident.status == "resolving", Incident.status == "remediating"))
                else:
                    filters.append(Incident.status == backend_status)
            
            if search:
                search_filter = or_(
                    Incident.title.ilike(f"%{search}%"),
                    Incident.description.ilike(f"%{search}%"),
                    Incident.source_alert_id.ilike(f"%{search}%")
                )
                filters.append(search_filter)
            
            # Get incidents with related data
            result = await db.execute(
                select(Incident)
                .options(
                    selectinload(Incident.timeline),
                    selectinload(Incident.agent_executions)
                )
                .where(and_(*filters))
                .order_by(Incident.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            
            incidents = result.scalars().all()
            return incidents
            
        except Exception as e:
            logger.error(f"Error getting incidents for organization: {e}")
            return []
    
    async def get_incident_stats(
        self,
        organization_id: int,
        db: AsyncSession,
        sync_from_servicenow: bool = True
    ) -> Dict[str, int]:
        """
        Get incident statistics for organization
        """
        try:
            # Sync from ServiceNow if requested and available
            if sync_from_servicenow:
                try:
                    synced_count = len(await self.sync_servicenow_incidents(organization_id, db, limit=100))
                    logger.info(f"Synced {synced_count} incidents for stats")
                except Exception as e:
                    logger.warning(f"ServiceNow sync failed for stats, proceeding with database data: {e}")
            
            # Get incident counts
            result = await db.execute(
                select(
                    func.count(Incident.id).label("total"),
                    func.sum(case((Incident.severity == "critical", 1), else_=0)).label("critical"),
                    func.sum(case((Incident.status == "investigating", 1), else_=0)).label("investigating"),
                    func.sum(case((Incident.status.in_(["resolving", "remediating"]), 1), else_=0)).label("remediating"),
                    func.sum(case((Incident.status == "resolved", 1), else_=0)).label("resolved"),
                )
                .where(Incident.organization_id == organization_id)
            )
            
            stats = result.first()
            
            return {
                'total': stats.total or 0,
                'critical': stats.critical or 0,
                'investigating': stats.investigating or 0,
                'remediating': stats.remediating or 0,
                'resolved': stats.resolved or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting incident stats: {e}")
            return {'total': 0, 'critical': 0, 'investigating': 0, 'remediating': 0, 'resolved': 0}
    
    async def get_incident_detail(
        self,
        incident_id: int,
        organization_id: int,
        db: AsyncSession
    ) -> Optional[Incident]:
        """Get detailed incident information"""
        try:
            result = await db.execute(
                select(Incident)
                .options(
                    selectinload(Incident.timeline),
                    selectinload(Incident.agent_executions),
                    selectinload(Incident.infrastructure_components),
                    selectinload(Incident.verification_gates),
                    selectinload(Incident.executions)
                )
                .where(
                    and_(
                        Incident.id == incident_id,
                        Incident.organization_id == organization_id
                    )
                )
            )
            
            incident = result.scalar_one_or_none()
            return incident
            
        except Exception as e:
            logger.error(f"Error getting incident detail: {e}")
            return None


# Global service instance
incident_service = IncidentService()