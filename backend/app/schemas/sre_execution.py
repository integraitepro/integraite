"""
SRE Execution schemas for API responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SRETimelineEntryResponse(BaseModel):
    """Timeline entry from SRE execution"""
    id: int
    step_number: int
    timestamp: datetime
    action_type: str
    title: str
    description: Optional[str] = None
    status: str
    duration_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class SREHypothesisResponse(BaseModel):
    """Hypothesis from SRE execution"""
    id: int
    hypothesis_text: str
    confidence_score: Optional[int] = None
    reasoning: Optional[str] = None
    supporting_evidence: Optional[Dict[str, Any]] = None
    status: str = "proposed"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SREVerificationResponse(BaseModel):
    """Verification step from SRE execution"""
    id: int
    verification_type: str
    description: str
    command_executed: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    success: bool = False
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class SREEvidenceResponse(BaseModel):
    """Evidence from SRE execution"""
    id: int
    evidence_type: str
    source: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    collected_at: datetime
    relevance_score: Optional[int] = None
    
    class Config:
        from_attributes = True


class SREProvenanceResponse(BaseModel):
    """Provenance tracking from SRE execution"""
    id: int
    step_id: str
    parent_step_id: Optional[str] = None
    reasoning_type: str
    input_data: Optional[Dict[str, Any]] = None
    reasoning_process: Optional[str] = None
    output_conclusion: Optional[str] = None
    confidence: Optional[int] = None
    timestamp: datetime
    agent_component: Optional[str] = None
    
    class Config:
        from_attributes = True


class IncidentExecutionLogResponse(BaseModel):
    """Execution log from SRE execution"""
    id: int
    incident_number: str
    agent_name: str
    step: int
    timestamp: datetime
    action_type: str
    hypothesis: Optional[str] = None
    command_executed: Optional[str] = None
    command_output: Optional[str] = None
    verification: Optional[str] = None
    status: str
    evidence: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class SREExecutionAgent(BaseModel):
    """Agent information from SRE execution"""
    id: str
    name: str
    type: str = "SRE Agent"
    role: str = "Lead Investigator"
    status: str
    current_action: Optional[str] = None
    progress: float = 0.0
    confidence: Optional[int] = None
    findings: List[str] = []
    recommendations: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None


class SREIncidentExecutionResponse(BaseModel):
    """Complete SRE execution data for an incident"""
    id: int
    incident_number: str
    incident_title: Optional[str] = None
    incident_description: Optional[str] = None
    target_ip: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assignment_group: Optional[str] = None
    status: str
    agent_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    resolution_summary: Optional[str] = None
    final_hypothesis: Optional[str] = None
    resolution_steps: Optional[List[Dict[str, Any]]] = None
    verification_results: Optional[Dict[str, Any]] = None
    
    # Related data
    timeline_entries: List[SRETimelineEntryResponse] = []
    hypotheses: List[SREHypothesisResponse] = []
    verifications: List[SREVerificationResponse] = []
    evidence: List[SREEvidenceResponse] = []
    provenance: List[SREProvenanceResponse] = []
    execution_logs: List[IncidentExecutionLogResponse] = []
    
    # Computed agent information
    agents: List[SREExecutionAgent] = []
    
    class Config:
        from_attributes = True


class SREExecutionSummary(BaseModel):
    """Summary of SRE execution for incident list"""
    has_sre_execution: bool = False
    execution_status: Optional[str] = None
    agent_count: int = 0
    progress: float = 0.0
    confidence: Optional[int] = None
    current_action: Optional[str] = None
    started_at: Optional[datetime] = None