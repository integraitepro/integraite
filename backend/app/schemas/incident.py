"""
Incident API schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class IncidentBase(BaseModel):
    """Base incident schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    short_description: Optional[str] = Field(None, max_length=255)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(None, max_length=100)
    source_system: Optional[str] = Field(None, max_length=255)
    affected_services: Optional[List[str]] = Field(default=[])
    customer_impact: bool = Field(default=False)
    estimated_affected_users: Optional[int] = Field(None, ge=0)


class IncidentCreate(IncidentBase):
    """Schema for creating incidents"""
    pass


class IncidentUpdate(BaseModel):
    """Schema for updating incidents"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(open|investigating|resolving|resolved|closed)$")
    resolution_summary: Optional[str] = None
    root_cause: Optional[str] = None


class TimelineEntry(BaseModel):
    """Timeline entry schema"""
    id: int
    entry_type: str
    title: str
    description: Optional[str]
    source: Optional[str]
    occurred_at: datetime
    created_at: datetime
    entry_metadata: Optional[Dict[str, Any]] = {}

    model_config = {"from_attributes": True}


class AgentExecutionResponse(BaseModel):
    """Agent execution response schema"""
    id: int
    agent_id: str
    agent_name: str
    agent_type: str
    role: str
    status: str
    current_action: Optional[str]
    progress: float
    confidence: Optional[float]
    findings: List[str] = []
    recommendations: List[str] = []
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class InfrastructureComponentResponse(BaseModel):
    """Infrastructure component response schema"""
    id: int
    name: str
    component_type: str
    layer: str
    status: str
    metrics: Dict[str, Any] = {}
    agent_actions: List[str] = []
    component_metadata: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class VerificationGateResponse(BaseModel):
    """Verification gate response schema"""
    id: int
    name: str
    description: str
    target_value: str
    current_value: Optional[str]
    status: str
    progress: float
    time_remaining: Optional[str]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class IncidentExecutionResponse(BaseModel):
    """Incident execution response schema"""
    id: int
    plan_id: str
    plan_name: str
    description: Optional[str]
    status: str
    progress: float
    estimated_duration_minutes: Optional[float]
    root_cause: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PreExecutionCheckResponse(BaseModel):
    """Pre-execution check response schema"""
    id: int
    check_name: str
    check_description: Optional[str]
    status: str
    error_message: Optional[str]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class IncidentDetailResponse(BaseModel):
    """Detailed incident response schema"""
    id: int
    incident_id: str  # Generated incident ID like INC-2024-001
    title: str
    description: str
    short_description: Optional[str]
    severity: str
    status: str
    category: Optional[str]
    source_system: Optional[str]
    affected_services: List[str] = []
    customer_impact: bool
    estimated_affected_users: Optional[int]
    
    # Resolution details
    resolution_type: Optional[str]
    resolution_summary: Optional[str]
    root_cause: Optional[str]
    
    # Metrics
    detection_time: Optional[datetime]
    response_time: Optional[datetime]
    resolution_time: Optional[datetime]
    mttr_minutes: Optional[float]
    
    # Assignment
    assigned_agent: Optional[str]  # Derived from agent executions
    agents_involved: int = 0  # Count of agents
    confidence: float = 0.0  # Average confidence from agents
    estimated_resolution: str = "Unknown"  # Calculated estimate
    
    # Timestamps
    start_time: datetime
    last_update: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    # Related data
    timeline: List[TimelineEntry] = []
    active_agents: List[AgentExecutionResponse] = []
    infrastructure_components: List[InfrastructureComponentResponse] = []
    verification_gates: List[VerificationGateResponse] = []
    executions: List[IncidentExecutionResponse] = []
    current_progress: float = 0.0  # Overall execution progress

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    """Incident list item response schema"""
    id: int
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    category: Optional[str]
    impact: str  # Derived from customer_impact and affected services
    assigned_agent: Optional[str]
    agents_involved: int
    confidence: float
    estimated_resolution: str
    start_time: datetime
    last_update: datetime
    affected_services: List[str] = []
    actions: List[Dict[str, str]] = []  # Recent actions from timeline

    model_config = {"from_attributes": True}


class IncidentStatsResponse(BaseModel):
    """Incident statistics response schema"""
    total: int
    critical: int
    investigating: int
    remediating: int
    resolved: int


class IncidentListQuery(BaseModel):
    """Query parameters for incident list"""
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(open|investigating|resolving|resolved|closed)$")
    search: Optional[str] = Field(None, max_length=255)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
