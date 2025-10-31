"""
Incident management API endpoints
"""
from typing import List, Dict, Any, Optional
import json
import random
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload
from datetime import datetime
import random
import logging

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, OrganizationMember
from app.models.incident import (
    Incident, IncidentTimeline, IncidentHypothesis, IncidentSeverity, IncidentStatus
)
from app.models.agent import AgentExecution
from app.models.incident_extended import (
    InfrastructureComponent, VerificationGate, IncidentExecution, PreExecutionCheck
)
from app.schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentDetailResponse, IncidentListResponse,
    IncidentStatsResponse, IncidentListQuery, TimelineEntry, AgentExecutionResponse,
    InfrastructureComponentResponse, VerificationGateResponse, IncidentExecutionResponse
)
from app.schemas.sre_execution import SREExecutionSummary
from app.core.database import get_db
from app.services.servicenow_client import ServiceNowService
from app.services.sre_execution_service import SREExecutionService

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for demo incidents (will be replaced with real data)
demo_incidents = {}


def generate_incident_id(year: int, month: int, sequence: int) -> str:
    """Generate incident ID like INC-2024-001"""
    return f"INC-{year}-{sequence:03d}"


def calculate_impact(customer_impact: bool, affected_services_count: int) -> str:
    """Calculate impact level based on customer impact and affected services"""
    if customer_impact:
        if affected_services_count >= 3:
            return "Service Outage"
        else:
            return "Customer Impact"
    elif affected_services_count >= 2:
        return "Service Degradation"
    elif affected_services_count == 1:
        return "Performance Impact"
    else:
        return "No Impact"


async def seed_demo_data(org_id: int, db: AsyncSession):
    """Seed demo incident data for the organization"""
    if org_id in demo_incidents:
        return  # Already seeded
    
    # Create demo incidents
    demo_data = [
        {
            "title": "High Memory Usage on Production API Server",
            "description": "Memory consumption spiked to 95% on api-prod-01, causing slow response times",
            "severity": "high",
            "status": "investigating",
            "category": "Performance",
            "affected_services": ["API Gateway", "User Service", "Authentication"],
            "customer_impact": True,
            "estimated_affected_users": 1500,
        },
        {
            "title": "Database Connection Pool Exhausted",
            "description": "PostgreSQL connection pool reached maximum capacity, new connections failing",
            "severity": "critical",
            "status": "remediating",
            "category": "Database",
            "affected_services": ["Order Service", "Inventory", "Payments"],
            "customer_impact": True,
            "estimated_affected_users": 2500,
        },
        {
            "title": "SSL Certificate Expiring Soon",
            "description": "SSL certificate for api.integraite.pro expires in 7 days",
            "severity": "medium",
            "status": "resolved",
            "category": "Security",
            "affected_services": ["API Gateway"],
            "customer_impact": False,
            "estimated_affected_users": 0,
        },
        {
            "title": "Unusual Network Traffic Pattern Detected",
            "description": "Abnormal spike in outbound traffic detected from eu-west-1 region",
            "severity": "medium",
            "status": "investigating",
            "category": "Network",
            "affected_services": ["CDN", "Load Balancer"],
            "customer_impact": False,
            "estimated_affected_users": 0,
        },
        {
            "title": "Redis Cache Performance Degradation",
            "description": "Cache hit ratio dropped to 45%, causing increased database load",
            "severity": "high",
            "status": "remediating",
            "category": "Performance",
            "affected_services": ["Session Store", "Content Cache"],
            "customer_impact": True,
            "estimated_affected_users": 800,
        }
    ]
    
    created_incidents = []
    current_year = datetime.now().year
    
    for i, data in enumerate(demo_data, 1):
        # Create incident
        incident = Incident(
            organization_id=org_id,
            title=data["title"],
            description=data["description"],
            severity=data["severity"],
            status=data["status"],
            category=data["category"],
            affected_services=data["affected_services"],
            customer_impact=data["customer_impact"],
            estimated_affected_users=data["estimated_affected_users"],
            detection_time=datetime.now(),
            response_time=datetime.now(),
        )
        
        db.add(incident)
        await db.flush()  # Get incident.id
        
        # Generate incident ID
        incident_id = generate_incident_id(current_year, 1, i)
        
        # Create sample timeline entries
        timeline_entries = [
            {
                "entry_type": "detection",
                "title": "Incident Detection",
                "description": f"Automated monitoring detected {data['title'].lower()}",
                "occurred_at": datetime.now(),
            },
            {
                "entry_type": "analysis",
                "title": "Initial Analysis",
                "description": "Started automated analysis and root cause investigation",
                "occurred_at": datetime.now(),
            }
        ]
        
        for entry_data in timeline_entries:
            timeline_entry = IncidentTimeline(
                incident_id=incident.id,
                **entry_data
            )
            db.add(timeline_entry)
        
        # Create sample agent executions
        if data["status"] in ["investigating", "remediating"]:
            agent_configs = [
                {
                    "agent_name": "Memory Optimizer",
                    "agent_type": "Application Performance",
                    "role": "Lead Investigator",
                    "current_action": "Analyzing memory usage patterns",
                    "progress": 75,
                    "confidence": 89,
                    "findings": [
                        "Identified gradual memory increase over 2 hours",
                        "Memory leak detected in session management module",
                        "Thread pool analysis shows blocked cleanup threads"
                    ],
                    "recommendations": [
                        "Implement immediate garbage collection cycle",
                        "Restart affected service with memory leak patch"
                    ]
                },
                {
                    "agent_name": "Performance Monitor",
                    "agent_type": "Infrastructure Monitoring",
                    "role": "Supporting Analyst",
                    "current_action": "Monitoring system metrics and resource utilization",
                    "progress": 90,
                    "confidence": 95,
                    "findings": [
                        "CPU usage remains stable at 45%",
                        "Network latency increased by 12%"
                    ],
                    "recommendations": [
                        "Scale out additional server instances"
                    ]
                }
            ]
            
            for agent_config in agent_configs:
                agent_execution = AgentExecution(
                    incident_id=incident.id,
                    agent_external_id=f"agent-{agent_config['agent_name'].lower().replace(' ', '-')}",
                    status="in_progress",
                    started_at=datetime.now(),
                    agent_name=agent_config['agent_name'],
                    agent_type=agent_config['agent_type'],
                    role=agent_config['role'],
                    current_action=agent_config['current_action'],
                    progress=agent_config['progress'],
                    confidence=agent_config['confidence'],
                    findings=agent_config['findings'],
                    recommendations=agent_config['recommendations']
                )
                db.add(agent_execution)
        
        # Create sample infrastructure components
        infra_components = [
            {
                "name": "api-prod-01",
                "component_type": "EC2 Instance",
                "layer": "Application",
                "status": "degraded",
                "metrics": {
                    "memory": {"current": 95, "normal": 65, "unit": "%"},
                    "cpu": {"current": 45, "normal": 35, "unit": "%"},
                    "disk": {"current": 23, "normal": 20, "unit": "%"}
                },
                "agent_actions": ["Memory analysis", "Performance monitoring"]
            },
            {
                "name": "session-cache",
                "component_type": "Redis Cluster",
                "layer": "Data",
                "status": "degraded",
                "metrics": {
                    "memory": {"current": 78, "normal": 45, "unit": "%"},
                    "connections": {"current": 890, "normal": 650, "unit": "conn"}
                },
                "agent_actions": ["Cache optimization", "Memory cleanup"]
            }
        ]
        
        for comp_data in infra_components:
            component = InfrastructureComponent(
                incident_id=incident.id,
                **comp_data
            )
            db.add(component)
        
        # Create sample verification gates
        verification_gates = [
            {
                "name": "Memory Usage Reduction",
                "description": "Memory usage should drop below 75%",
                "target_value": "< 75%",
                "current_value": "87%",
                "status": "in_progress",
                "progress": 45,
                "time_remaining": "8 minutes"
            },
            {
                "name": "Response Time Recovery",
                "description": "API response times return to baseline",
                "target_value": "< 200ms",
                "current_value": "450ms",
                "status": "pending",
                "progress": 0,
                "time_remaining": "15 minutes"
            }
        ]
        
        for gate_data in verification_gates:
            gate = VerificationGate(
                incident_id=incident.id,
                **gate_data
            )
            db.add(gate)
        
        # Create sample execution plan
        execution = IncidentExecution(
            incident_id=incident.id,
            plan_id="plan-001",
            plan_name="Memory Leak Remediation",
            description="Multi-step plan to resolve memory leak and restore service",
            status="executing",
            progress=65,
            estimated_duration_minutes=15,
            root_cause="Memory leak in user session management module"
        )
        db.add(execution)
        
        created_incidents.append((incident, incident_id))
    
    await db.commit()
    
    # Store incident mappings
    demo_incidents[org_id] = {
        incident_id: incident for incident, incident_id in created_incidents
    }


@router.get("/stats")
async def get_incident_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> IncidentStatsResponse:
    """Get incident statistics from ServiceNow"""
    
    # Get user's organization
    org_member_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = org_member_result.scalar_one_or_none()
    
    if not org_member:
        return IncidentStatsResponse(
            total=0, critical=0, investigating=0, remediating=0, resolved=0
        )
    
    # Fetch incidents from ServiceNow
    try:
        servicenow_service = ServiceNowService()
        servicenow_incidents = await servicenow_service.sync_incidents(limit=100)
        
        if not servicenow_incidents:
            # Fallback to demo data if ServiceNow is not available
            logger.warning("ServiceNow data not available for stats, falling back to demo data")
            await seed_demo_data(org_member.organization_id, db)
            
            result = await db.execute(
                select(
                    func.count(Incident.id).label("total"),
                    func.sum(case((Incident.severity == "critical", 1), else_=0)).label("critical"),
                    func.sum(case((Incident.status == "investigating", 1), else_=0)).label("investigating"),
                    func.sum(case((Incident.status.in_(["resolving", "remediating"]), 1), else_=0)).label("remediating"),
                    func.sum(case((Incident.status == "resolved", 1), else_=0)).label("resolved"),
                )
                .where(Incident.organization_id == org_member.organization_id)
            )
            
            stats = result.first()
            
            return IncidentStatsResponse(
                total=stats.total or 0,
                critical=stats.critical or 0,
                investigating=stats.investigating or 0,
                remediating=stats.remediating or 0,
                resolved=stats.resolved or 0,
            )
        
        # Calculate stats from ServiceNow incidents
        total = len(servicenow_incidents)
        critical = sum(1 for inc in servicenow_incidents if inc.get("severity") == "critical")
        investigating = sum(1 for inc in servicenow_incidents if inc.get("status") == "investigating")
        remediating = sum(1 for inc in servicenow_incidents if inc.get("status") in ["resolving", "remediating"])
        resolved = sum(1 for inc in servicenow_incidents if inc.get("status") == "resolved")
        
        return IncidentStatsResponse(
            total=total,
            critical=critical,
            investigating=investigating,
            remediating=remediating,
            resolved=resolved,
        )
        
    except Exception as e:
        logger.error(f"Error fetching incident stats: {e}")
        # Fallback to demo data on any error
        await seed_demo_data(org_member.organization_id, db)
        return IncidentStatsResponse(
            total=5, critical=1, investigating=2, remediating=1, resolved=1
        )


@router.get("/")
async def list_incidents(
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(None, pattern="^(open|investigating|resolving|resolved|closed)$"),
    search: Optional[str] = Query(None, max_length=255),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, List[IncidentListResponse]]:
    """List incidents for the current organization from ServiceNow"""
    
    # Get user's organization
    org_member_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = org_member_result.scalar_one_or_none()
    
    if not org_member:
        return {"incidents": []}
    
    # Fetch incidents from ServiceNow
    try:
        servicenow_service = ServiceNowService()
        servicenow_incidents = await servicenow_service.sync_incidents(limit=limit)
        
        logger.info(f"Fetched {len(servicenow_incidents)} incidents from ServiceNow")
        
        if not servicenow_incidents:
            # Fallback to demo data if ServiceNow is not available
            logger.warning("ServiceNow data not available, falling back to demo data")
            await seed_demo_data(org_member.organization_id, db)
            
            # Continue with existing database query for demo data
            filters = [Incident.organization_id == org_member.organization_id]
            
            if severity:
                filters.append(Incident.severity == severity)
            
            if status:
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
                )
                filters.append(search_filter)
            
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
            
            # Convert database incidents to response format
            incident_responses = []
            for incident in incidents:
                incident_id = generate_incident_id(incident.created_at.year, 1, incident.id)
                agents_involved = len(incident.agent_executions)
                assigned_agent = incident.agent_executions[0].agent_name if incident.agent_executions else None
                avg_confidence = sum(ae.confidence or 0 for ae in incident.agent_executions) / max(agents_involved, 1)
                impact = calculate_impact(incident.customer_impact, len(incident.affected_services or []))
                
                recent_actions = []
                for entry in incident.timeline[-2:]:
                    action_type = entry.entry_type
                    recent_actions.append({
                        "type": action_type,
                        "description": entry.description or entry.title,
                        "time": "5 min ago"
                    })
                
                frontend_status = incident.status
                if incident.status == "resolving":
                    frontend_status = "remediating"
                
                incident_response = IncidentListResponse(
                    id=incident.id,
                    incident_id=incident_id,
                    title=incident.title,
                    description=incident.description,
                    severity=incident.severity,
                    status=frontend_status,
                    category=incident.category or "Unknown",
                    impact=impact,
                    assigned_agent=assigned_agent,
                    agents_involved=agents_involved,
                    confidence=avg_confidence,
                    estimated_resolution="25 minutes",
                    start_time=incident.created_at,
                    last_update=incident.updated_at or incident.created_at,
                    affected_services=incident.affected_services or [],
                    actions=recent_actions,
                    sre_execution_summary=await SREExecutionService.get_sre_execution_summary(
                        incident_id, db
                    )
                )
                
                incident_responses.append(incident_response)
            
            return {"incidents": incident_responses}
        
        # Convert ServiceNow incidents to response format
        incident_responses = []
        for i, sn_incident in enumerate(servicenow_incidents):
            try:
                # Apply filters
                if severity and sn_incident.get("severity", "").lower() != severity.lower():
                    continue
                    
                if status:
                    sn_status = sn_incident.get("status", "").lower()
                    status_mapping = {
                        "investigating": ["investigating", "new", "in progress"],
                        "remediating": ["resolving", "remediating", "on hold"],
                        "resolved": ["resolved"],
                        "closed": ["closed", "canceled"]
                    }
                    if status.lower() not in ["open"]:  # "open" includes investigating
                        if sn_status not in status_mapping.get(status.lower(), []):
                            continue
                
                if search:
                    title = sn_incident.get("title", "").lower()
                    description = sn_incident.get("description", "").lower()
                    if search.lower() not in title and search.lower() not in description:
                        continue
                
                # Generate incident ID from ServiceNow number or create one
                incident_number = sn_incident.get("source_alert_id", f"SN-{i+1:03d}")
                
                # Map ServiceNow status to frontend status
                sn_status = sn_incident.get("status", "investigating")
                if sn_status == "resolving":
                    sn_status = "remediating"
                
                # Create synthetic data for fields not in ServiceNow
                agents_involved = random.randint(1, 3)
                confidence = random.randint(75, 95)
                
                # Generate recent actions based on status
                recent_actions = []
                if sn_status == "investigating":
                    recent_actions = [
                        {"type": "detection", "description": "Incident detected from ServiceNow", "time": "2 min ago"},
                        {"type": "analysis", "description": "Initial analysis started", "time": "1 min ago"}
                    ]
                elif sn_status == "remediating":
                    recent_actions = [
                        {"type": "remediation", "description": "Auto-remediation in progress", "time": "5 min ago"},
                        {"type": "verification", "description": "Verifying fix effectiveness", "time": "1 min ago"}
                    ]
                
                # Estimate resolution time based on severity
                severity_times = {
                    "critical": "15 minutes",
                    "high": "30 minutes", 
                    "medium": "45 minutes",
                    "low": "60 minutes"
                }
                estimated_resolution = severity_times.get(sn_incident.get("severity", "medium"), "30 minutes")
                
                # Parse dates with better error handling
                start_time = datetime.now()  # Default fallback
                detection_time = sn_incident.get("detection_time")
                if detection_time:
                    if isinstance(detection_time, str):
                        try:
                            start_time = datetime.fromisoformat(detection_time.replace('Z', '+00:00'))
                        except:
                            try:
                                # Try ServiceNow date format
                                start_time = datetime.strptime(detection_time, '%Y-%m-%d %H:%M:%S')
                            except:
                                start_time = datetime.now()
                    elif hasattr(detection_time, 'replace'):  # datetime object
                        start_time = detection_time
                
                last_update = start_time
                updated_at = sn_incident.get("updated_at")
                if updated_at:
                    if isinstance(updated_at, str):
                        try:
                            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        except:
                            try:
                                last_update = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                            except:
                                last_update = start_time
                    elif hasattr(updated_at, 'replace'):  # datetime object
                        last_update = updated_at
                
                incident_response = IncidentListResponse(
                    id=i + 1000,  # Use offset to avoid collision with demo data
                    incident_id=incident_number,
                    title=sn_incident.get("title", "Unknown Incident"),
                    description=sn_incident.get("description", ""),
                    severity=sn_incident.get("severity", "medium"),
                    status=sn_status,
                    category=sn_incident.get("category", "Unknown"),
                    impact=f"Customer Impact: {sn_incident.get('customer_impact')}" if sn_incident.get('customer_impact') else "No Impact",
                    assigned_agent=f"SRE Agent {random.randint(1, 5)}",
                    agents_involved=agents_involved,
                    confidence=confidence,
                    estimated_resolution=estimated_resolution,
                    start_time=start_time,
                    last_update=last_update,
                    affected_services=sn_incident.get("affected_services", []) if sn_incident.get("affected_services") != ["N/A"] else ["Service Unknown"],
                    actions=recent_actions,
                    sre_execution_summary=await SREExecutionService.get_sre_execution_summary(
                        incident_number, db
                    )
                )
                
                incident_responses.append(incident_response)
                
            except Exception as e:
                logger.error(f"Error processing incident {i}: {e}")
                # Continue with next incident instead of failing completely
                continue
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_incidents = incident_responses[start_idx:end_idx]
        
        logger.info(f"Returning {len(paginated_incidents)} incidents after processing {len(incident_responses)} total incidents")
        
        return {"incidents": paginated_incidents}
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        # Fallback to demo data on any error
        await seed_demo_data(org_member.organization_id, db)
        return {"incidents": []}


@router.get("/{incident_id}")
async def get_incident_detail(
    incident_id: str,  # Changed to string to handle ServiceNow incident numbers
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> IncidentDetailResponse:
    """Get detailed incident information from ServiceNow or database"""
    
    # Get user's organization
    org_member_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = org_member_result.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Handle synthetic ServiceNow IDs (1000+)
    try:
        numeric_id = int(incident_id)
        if numeric_id >= 1000:
            # This is a synthetic ID from ServiceNow conversion
            servicenow_service = ServiceNowService()
            if servicenow_service.client:
                try:
                    # Fetch all incidents and find the one with matching synthetic ID
                    servicenow_incidents = await servicenow_service.sync_incidents(limit=100)
                    
                    # Find the incident by synthetic ID (i + 1000)
                    target_index = numeric_id - 1000
                    if 0 <= target_index < len(servicenow_incidents):
                        sn_incident_data = servicenow_incidents[target_index]
                        
                        # Convert to detail response using the ServiceNow data
                        return await convert_servicenow_to_detail_response(sn_incident_data, incident_id, db)
                    
                except Exception as e:
                    logger.error(f"Error fetching ServiceNow incident by synthetic ID {incident_id}: {e}")
            
            # If ServiceNow lookup failed, fall through to database lookup
    except ValueError:
        # Not a numeric ID, continue with other checks
        pass
    
    # Try to fetch from ServiceNow first if incident_id looks like a ServiceNow number
    if incident_id.startswith(('INC', 'SN-')):
        try:
            servicenow_service = ServiceNowService()
            if servicenow_service.client:
                # Extract ServiceNow incident number
                sn_number = incident_id if incident_id.startswith('INC') else incident_id.replace('SN-', 'INC')
                sn_incident_data = await servicenow_service.get_incident(sn_number)
                
                if sn_incident_data:
                    return await convert_servicenow_to_detail_response(sn_incident_data, incident_id, db)
        
        except Exception as e:
            logger.error(f"Error fetching ServiceNow incident {incident_id}: {e}")
    
    # Fallback to database lookup for numeric IDs or if ServiceNow lookup failed
    try:
        numeric_id = int(incident_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Seed demo data if needed
    await seed_demo_data(org_member.organization_id, db)
    
    # Get incident with all related data from database
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
                Incident.id == numeric_id,
                Incident.organization_id == org_member.organization_id
            )
        )
    )
    
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Continue with existing database incident conversion logic...
    formatted_incident_id = generate_incident_id(incident.created_at.year, 1, incident.id)
    
    timeline_entries = [
        TimelineEntry(
            id=entry.id,
            entry_type=entry.entry_type,
            title=entry.title,
            description=entry.description,
            source=entry.source,
            occurred_at=entry.occurred_at,
            created_at=entry.created_at,
            entry_metadata=entry.entry_metadata or {}
        )
        for entry in incident.timeline
    ]
    
    active_agents = [
        AgentExecutionResponse(
            id=agent.id,
            agent_id=agent.agent_external_id or str(agent.agent_id) if agent.agent_id else f"agent-{agent.id}",
            agent_name=agent.agent_name or "Unknown Agent",
            agent_type=agent.agent_type or "Unknown Type",
            role=agent.role or "Unknown Role",
            status=agent.status,
            current_action=agent.current_action,
            progress=agent.progress or 0.0,
            confidence=agent.confidence,
            findings=agent.findings or [],
            recommendations=agent.recommendations or [],
            started_at=agent.started_at,
            completed_at=agent.completed_at
        )
        for agent in incident.agent_executions
    ]
    
    infrastructure_components = [
        InfrastructureComponentResponse(
            id=comp.id,
            name=comp.name,
            component_type=comp.component_type,
            layer=comp.layer,
            status=comp.status,
            metrics=comp.metrics or {},
            agent_actions=comp.agent_actions or [],
            component_metadata=comp.component_metadata or {}
        )
        for comp in incident.infrastructure_components
    ]
    
    verification_gates = [
        VerificationGateResponse(
            id=gate.id,
            name=gate.name,
            description=gate.description,
            target_value=gate.target_value,
            current_value=gate.current_value,
            status=gate.status,
            progress=gate.progress,
            time_remaining=gate.time_remaining,
            completed_at=gate.completed_at
        )
        for gate in incident.verification_gates
    ]
    
    executions = [
        IncidentExecutionResponse(
            id=exec.id,
            plan_id=exec.plan_id,
            plan_name=exec.plan_name,
            description=exec.description,
            status=exec.status,
            progress=exec.progress,
            estimated_duration_minutes=exec.estimated_duration_minutes,
            root_cause=exec.root_cause,
            started_at=exec.started_at,
            completed_at=exec.completed_at
        )
        for exec in incident.executions
    ]
    
    agents_involved = len(active_agents)
    assigned_agent = active_agents[0].agent_name if active_agents else None
    avg_confidence = sum(agent.confidence or 0 for agent in active_agents) / max(agents_involved, 1)
    current_progress = executions[0].progress if executions else 0
    impact = calculate_impact(incident.customer_impact, len(incident.affected_services or []))
    
    frontend_status = incident.status
    if incident.status == "resolving":
        frontend_status = "remediating"
    
    # Get SRE execution data
    sre_execution = await SREExecutionService.get_sre_execution_by_incident_number(
        formatted_incident_id, db
    )
    
    # Extract SRE data for separate fields
    sre_timeline = sre_execution.timeline_entries if sre_execution else []
    sre_hypotheses = sre_execution.hypotheses if sre_execution else []
    sre_verifications = sre_execution.verifications if sre_execution else []
    sre_evidence = sre_execution.evidence if sre_execution else []
    sre_provenance = sre_execution.provenance if sre_execution else []
    
    # If we have SRE execution data, use it to enhance the response
    if sre_execution:
        # Replace or supplement demo agents with real SRE agents
        if sre_execution.agents:
            # Convert SRE agents to AgentExecutionResponse format
            for sre_agent in sre_execution.agents:
                active_agents.append(AgentExecutionResponse(
                    id=0,  # Temporary ID for SRE agent
                    agent_id=sre_agent.id,
                    agent_name=sre_agent.name,
                    agent_type=sre_agent.type,
                    role=sre_agent.role,
                    status=sre_agent.status,
                    current_action=sre_agent.current_action,
                    progress=sre_agent.progress,
                    confidence=float(sre_agent.confidence) if sre_agent.confidence else None,
                    findings=sre_agent.findings,
                    recommendations=sre_agent.recommendations,
                    started_at=sre_agent.started_at,
                    completed_at=sre_agent.completed_at
                ))
        
        # Update metrics based on SRE execution
        if sre_execution.agents:
            agents_involved = len(sre_execution.agents)
            assigned_agent = sre_execution.agents[0].name
            avg_confidence = sum(
                agent.confidence for agent in sre_execution.agents 
                if agent.confidence
            ) / max(len(sre_execution.agents), 1)
        
        # Update progress based on SRE timeline
        if sre_timeline:
            completed_timeline = len([
                entry for entry in sre_timeline 
                if entry.status == "completed"
            ])
            current_progress = (completed_timeline / len(sre_timeline)) * 100
        
        # Update resolution summary if available
        if sre_execution.resolution_summary:
            incident.resolution_summary = sre_execution.resolution_summary
        
        # Update root cause if available
        if sre_execution.final_hypothesis:
            incident.root_cause = sre_execution.final_hypothesis
    
    return IncidentDetailResponse(
        id=incident.id,
        incident_id=formatted_incident_id,
        title=incident.title,
        description=incident.description,
        short_description=incident.short_description,
        severity=incident.severity,
        status=frontend_status,
        category=incident.category,
        source_system=incident.source_system,
        affected_services=incident.affected_services or [],
        customer_impact=incident.customer_impact,
        estimated_affected_users=incident.estimated_affected_users,
        resolution_type=incident.resolution_type,
        resolution_summary=incident.resolution_summary,
        root_cause=incident.root_cause,
        detection_time=incident.detection_time,
        response_time=incident.response_time,
        resolution_time=incident.resolution_time,
        mttr_minutes=incident.mttr_minutes,
        assigned_agent=assigned_agent,
        agents_involved=agents_involved,
        confidence=avg_confidence,
        estimated_resolution="25 minutes",
        start_time=incident.created_at,
        last_update=incident.updated_at or incident.created_at,
        resolved_at=incident.resolved_at,
        closed_at=incident.closed_at,
        timeline=timeline_entries,
        active_agents=active_agents,
        infrastructure_components=infrastructure_components,
        verification_gates=verification_gates,
        executions=executions,
        current_progress=current_progress,
        sre_execution=sre_execution,
        sre_timeline=sre_timeline,
        sre_hypotheses=sre_hypotheses,
        sre_verifications=sre_verifications,
        sre_evidence=sre_evidence,
        sre_provenance=sre_provenance
    )


@router.get("/{incident_id}/execution-logs")
async def get_incident_execution_logs(
    incident_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get execution logs for a specific incident from incident_logs.json"""
    
    try:
        # Read the incident_logs.json file
        import os
        logs_file_path = os.path.join(os.path.dirname(__file__), "incident_logs.json")
        
        logger.info(f"Looking for incident logs at: {logs_file_path}")
        logger.info(f"Path exists: {os.path.exists(logs_file_path)}")
        
        if not os.path.exists(logs_file_path):
            return {"logs": [], "message": f"No execution logs found at {logs_file_path}"}
        
        with open(logs_file_path, 'r', encoding='utf-8') as f:
            all_logs = json.load(f)
        
        logger.info(f"Loaded {len(all_logs)} log entries, looking for incident: {incident_id}")
        
        # Find logs for the specific incident
        incident_logs = None
        for log_entry in all_logs:
            if log_entry.get("incident_id") == incident_id:
                incident_logs = log_entry
                break
        
        if not incident_logs:
            return {"logs": [], "message": f"No execution logs found for incident {incident_id}"}
        
        return {
            "incident_id": incident_logs["incident_id"],
            "start_time": incident_logs["start_time"],
            "last_updated": incident_logs["last_updated"],
            "step_count": incident_logs["step_count"],
            "duration_seconds": incident_logs["duration_seconds"],
            "status": incident_logs["status"],
            "logs": incident_logs["logs"]
        }
        
    except Exception as e:
        logger.error(f"Error reading execution logs for incident {incident_id}: {e}")
        return {"logs": [], "message": "Error loading execution logs"}


async def convert_servicenow_to_detail_response(sn_incident_data: Dict[str, Any], incident_id: str, db: AsyncSession) -> IncidentDetailResponse:
    """Convert ServiceNow incident data to detail response format"""
    
    # Parse dates with better error handling
    start_time = datetime.now()  # Default fallback
    detection_time = sn_incident_data.get("detection_time")
    if detection_time:
        if isinstance(detection_time, str):
            try:
                start_time = datetime.fromisoformat(detection_time.replace('Z', '+00:00'))
            except:
                try:
                    start_time = datetime.strptime(detection_time, '%Y-%m-%d %H:%M:%S')
                except:
                    start_time = datetime.now()
        elif hasattr(detection_time, 'replace'):  # datetime object
            start_time = detection_time
    
    last_update = start_time
    updated_at = sn_incident_data.get("updated_at")
    if updated_at:
        if isinstance(updated_at, str):
            try:
                last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                try:
                    last_update = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                except:
                    last_update = start_time
        elif hasattr(updated_at, 'replace'):  # datetime object
            last_update = updated_at
    
    # Create synthetic timeline entries
    timeline_entries = [
        TimelineEntry(
            id=1,
            entry_type="detection",
            title="Incident Detected",
            description=f"Incident detected in ServiceNow: {sn_incident_data.get('title', '')}",
            source="ServiceNow",
            occurred_at=start_time.isoformat(),
            created_at=start_time.isoformat(),
            entry_metadata={}
        ),
        TimelineEntry(
            id=2,
            entry_type="analysis",
            title="Analysis Started",
            description="Automated analysis initiated for incident resolution",
            source="SRE Agent",
            occurred_at=last_update.isoformat(),
            created_at=last_update.isoformat(),
            entry_metadata={}
        )
    ]
    
    # Create synthetic active agents
    active_agents = [
        AgentExecutionResponse(
            id=1,
            agent_id="sre-agent-primary",
            agent_name="Primary SRE Agent",
            agent_type="Incident Resolution",
            role="Lead Investigator",
            status="in_progress",
            current_action=f"Analyzing {sn_incident_data.get('category', 'system')} incident",
            progress=random.randint(30, 80),
            confidence=random.randint(75, 95),
            findings=[
                f"Incident affects {len(sn_incident_data.get('affected_services', []))} services",
                f"Priority level: {sn_incident_data.get('severity', 'medium')}",
                f"Category: {sn_incident_data.get('category', 'Unknown')}"
            ],
            recommendations=[
                "Monitor system metrics closely",
                "Prepare rollback plan if needed",
                "Escalate if resolution time exceeds SLA"
            ],
            started_at=start_time.isoformat(),
            completed_at=None
        )
    ]
    
    # Create synthetic infrastructure components
    affected_services = sn_incident_data.get("affected_services", ["Unknown Service"])
    infrastructure_components = []
    for i, service in enumerate(affected_services[:3]):  # Limit to 3
        if service != "N/A":
            infrastructure_components.append(
                InfrastructureComponentResponse(
                    id=i + 1,
                    name=service,
                    component_type="Service",
                    layer="Application",
                    status="degraded" if sn_incident_data.get("customer_impact") else "healthy",
                    metrics={
                        "availability": {"current": random.randint(85, 99), "normal": 99, "unit": "%"},
                        "response_time": {"current": random.randint(200, 800), "normal": 150, "unit": "ms"}
                    },
                    agent_actions=["Monitoring", "Analysis"],
                    component_metadata={}
                )
            )
    
    # Create synthetic verification gates
    verification_gates = [
        VerificationGateResponse(
            id=1,
            name="Service Recovery",
            description="Verify service is operational",
            target_value="Available",
            current_value="Degraded" if sn_incident_data.get("customer_impact") else "Available",
            status="in_progress" if sn_incident_data.get("status") != "resolved" else "completed",
            progress=random.randint(30, 90),
            time_remaining="10 minutes",
            completed_at=None
        )
    ]
    
    # Create synthetic execution
    executions = [
        IncidentExecutionResponse(
            id=1,
            plan_id="sn-remediation-001",
            plan_name="ServiceNow Incident Remediation",
            description=f"Automated remediation plan for {sn_incident_data.get('category', 'system')} incident",
            status="executing" if sn_incident_data.get("status") != "resolved" else "completed",
            progress=random.randint(40, 90),
            estimated_duration_minutes=30,
            root_cause=sn_incident_data.get("root_cause"),
            started_at=start_time.isoformat(),
            completed_at=None
        )
    ]
    
    # Map ServiceNow status to frontend status
    sn_status = sn_incident_data.get("status", "investigating")
    if sn_status == "resolving":
        sn_status = "remediating"
    
    # Get SRE execution data for this incident
    source_alert_id = sn_incident_data.get("source_alert_id", incident_id)
    sre_execution = await SREExecutionService.get_sre_execution_by_incident_number(
        source_alert_id, db
    )
    
    # Extract SRE data for separate fields
    sre_timeline = sre_execution.timeline_entries if sre_execution else []
    sre_hypotheses = sre_execution.hypotheses if sre_execution else []
    sre_verifications = sre_execution.verifications if sre_execution else []
    sre_evidence = sre_execution.evidence if sre_execution else []
    sre_provenance = sre_execution.provenance if sre_execution else []
    
    # Initialize default values
    assigned_agent = "Primary SRE Agent"
    agents_involved = len(active_agents)
    confidence = active_agents[0].confidence if active_agents else 85
    resolution_summary = sn_incident_data.get("resolution_summary")
    root_cause = sn_incident_data.get("root_cause")
    current_progress = executions[0].progress if executions else 0
    
    # Enhance active agents with SRE execution data
    if sre_execution and sre_execution.agents:
        # Replace synthetic agents with real SRE agents
        active_agents = []
        for sre_agent in sre_execution.agents:
            active_agents.append(AgentExecutionResponse(
                id=0,  # Temporary ID for SRE agent
                agent_id=sre_agent.id,
                agent_name=sre_agent.name,
                agent_type=sre_agent.type,
                role=sre_agent.role,
                status=sre_agent.status,
                current_action=sre_agent.current_action,
                progress=sre_agent.progress,
                confidence=float(sre_agent.confidence) if sre_agent.confidence else None,
                findings=sre_agent.findings,
                recommendations=sre_agent.recommendations,
                started_at=sre_agent.started_at,
                completed_at=sre_agent.completed_at
            ))
    
    # Update execution data with SRE information
    if sre_execution:
        # Update progress based on SRE timeline
        if sre_timeline:
            completed_timeline = len([
                entry for entry in sre_timeline 
                if entry.status == "completed"
            ])
            current_progress = (completed_timeline / len(sre_timeline)) * 100
        
        # Update resolution summary and root cause
        if sre_execution.resolution_summary:
            resolution_summary = sre_execution.resolution_summary
        if sre_execution.final_hypothesis:
            root_cause = sre_execution.final_hypothesis
            
        # Update confidence and agent metrics
        if sre_execution.agents:
            agents_involved = len(sre_execution.agents)
            assigned_agent = sre_execution.agents[0].name
            confidences = [
                agent.confidence for agent in sre_execution.agents 
                if agent.confidence is not None
            ]
            confidence = sum(confidences) / len(confidences) if confidences else confidence
    
    return IncidentDetailResponse(
        id=999999,  # High number to avoid collision
        incident_id=incident_id,
        title=sn_incident_data.get("title", "Unknown Incident"),
        description=sn_incident_data.get("description", ""),
        short_description=sn_incident_data.get("short_description"),
        severity=sn_incident_data.get("severity", "medium"),
        status=sn_status,
        category=sn_incident_data.get("category"),
        source_system=sn_incident_data.get("source_system", "ServiceNow"),
        affected_services=sn_incident_data.get("affected_services", []),
        customer_impact=sn_incident_data.get("customer_impact", False),
        estimated_affected_users=sn_incident_data.get("estimated_affected_users"),
        resolution_type=sn_incident_data.get("resolution_type"),
        resolution_summary=resolution_summary,
        root_cause=root_cause,
        detection_time=start_time.isoformat() if start_time else None,
        response_time=start_time.isoformat() if start_time else None,
        resolution_time=sn_incident_data.get("resolution_time"),
        mttr_minutes=sn_incident_data.get("mttr_minutes"),
        assigned_agent=assigned_agent,
        agents_involved=agents_involved,
        confidence=confidence,
        estimated_resolution="30 minutes",
        start_time=start_time,
        last_update=last_update,
        resolved_at=sn_incident_data.get("resolution_time"),
        closed_at=sn_incident_data.get("closed_time"),
        timeline=timeline_entries,
        active_agents=active_agents,
        infrastructure_components=infrastructure_components,
        verification_gates=verification_gates,
        executions=executions,
        current_progress=current_progress,
        sre_execution=sre_execution,
        sre_timeline=sre_timeline,
        sre_hypotheses=sre_hypotheses,
        sre_verifications=sre_verifications,
        sre_evidence=sre_evidence,
        sre_provenance=sre_provenance
    )
