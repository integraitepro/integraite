"""
Incident management API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload
from datetime import datetime
import random

from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, OrganizationMember
from app.models.incident import Incident, IncidentTimeline, IncidentHypothesis, IncidentSeverity, IncidentStatus
from app.models.agent import AgentExecution
from app.models.incident_extended import (
    InfrastructureComponent, VerificationGate, 
    IncidentExecution, PreExecutionCheck
)
from app.schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentDetailResponse, IncidentListResponse,
    IncidentStatsResponse, IncidentListQuery, TimelineEntry, AgentExecutionResponse,
    InfrastructureComponentResponse, VerificationGateResponse, IncidentExecutionResponse
)
from app.core.database import get_db

router = APIRouter()

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
            "description": "SSL certificate for api.integraite.com expires in 7 days",
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
    """Get incident statistics for the current organization"""
    
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
    
    # Seed demo data if needed
    await seed_demo_data(org_member.organization_id, db)
    
    # Get incident counts
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
    """List incidents for the current organization with filtering"""
    
    # Get user's organization
    org_member_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = org_member_result.scalar_one_or_none()
    
    if not org_member:
        return {"incidents": []}
    
    # Seed demo data if needed
    await seed_demo_data(org_member.organization_id, db)
    
    # Build query filters
    filters = [Incident.organization_id == org_member.organization_id]
    
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
    
    # Convert to response format
    incident_responses = []
    for incident in incidents:
        # Generate incident ID
        incident_id = generate_incident_id(incident.created_at.year, 1, incident.id)
        
        # Calculate derived fields
        agents_involved = len(incident.agent_executions)
        assigned_agent = incident.agent_executions[0].agent_name if incident.agent_executions else None
        avg_confidence = sum(ae.confidence or 0 for ae in incident.agent_executions) / max(agents_involved, 1)
        
        # Calculate impact
        impact = calculate_impact(incident.customer_impact, len(incident.affected_services or []))
        
        # Get recent actions from timeline
        recent_actions = []
        for entry in incident.timeline[-2:]:  # Last 2 entries
            action_type = entry.entry_type
            recent_actions.append({
                "type": action_type,
                "description": entry.description or entry.title,
                "time": "5 min ago"  # Simplified for demo
            })
        
        # Map status for frontend
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
            estimated_resolution="25 minutes",  # Simplified for demo
            start_time=incident.created_at,
            last_update=incident.updated_at or incident.created_at,
            affected_services=incident.affected_services or [],
            actions=recent_actions
        )
        
        incident_responses.append(incident_response)
    
    return {"incidents": incident_responses}


@router.get("/{incident_id}")
async def get_incident_detail(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> IncidentDetailResponse:
    """Get detailed incident information"""
    
    # Get user's organization
    org_member_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = org_member_result.scalar_one_or_none()
    
    if not org_member:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Seed demo data if needed
    await seed_demo_data(org_member.organization_id, db)
    
    # Get incident with all related data
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
                Incident.organization_id == org_member.organization_id
            )
        )
    )
    
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Generate incident ID
    formatted_incident_id = generate_incident_id(incident.created_at.year, 1, incident.id)
    
    # Convert timeline entries
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
    
    # Convert agent executions
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
    
    # Convert infrastructure components
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
    
    # Convert verification gates
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
    
    # Convert executions
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
    
    # Calculate derived fields
    agents_involved = len(active_agents)
    assigned_agent = active_agents[0].agent_name if active_agents else None
    avg_confidence = sum(agent.confidence or 0 for agent in active_agents) / max(agents_involved, 1)
    current_progress = executions[0].progress if executions else 0
    impact = calculate_impact(incident.customer_impact, len(incident.affected_services or []))
    
    # Map status for frontend
    frontend_status = incident.status
    if incident.status == "resolving":
        frontend_status = "remediating"
    
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
        estimated_resolution="25 minutes",  # Simplified for demo
        start_time=incident.created_at,
        last_update=incident.updated_at or incident.created_at,
        resolved_at=incident.resolved_at,
        closed_at=incident.closed_at,
        timeline=timeline_entries,
        active_agents=active_agents,
        infrastructure_components=infrastructure_components,
        verification_gates=verification_gates,
        executions=executions,
        current_progress=current_progress
    )