"""
Incident management models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, List, Optional

from app.core.database import Base


class IncidentSeverity(PyEnum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(PyEnum):
    """Incident status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ResolutionType(PyEnum):
    """How the incident was resolved"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class Incident(Base):
    """Incident model"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(255), nullable=True)
    
    # Classification
    severity = Column(String(50), default=IncidentSeverity.MEDIUM.value)
    status = Column(String(50), default=IncidentStatus.OPEN.value)
    category = Column(String(100), nullable=True)  # Infrastructure, Application, etc.
    
    # Source
    source_system = Column(String(255), nullable=True)  # Which system detected it
    source_alert_id = Column(String(255), nullable=True)
    
    # Impact
    affected_services = Column(JSON, nullable=True)  # List of affected services
    customer_impact = Column(Boolean, default=False)
    estimated_affected_users = Column(Integer, nullable=True)
    
    # Resolution
    resolution_type = Column(String(50), nullable=True)
    resolution_summary = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    
    # Metrics
    detection_time = Column(DateTime(timezone=True), nullable=True)
    response_time = Column(DateTime(timezone=True), nullable=True)
    resolution_time = Column(DateTime(timezone=True), nullable=True)
    mttr_minutes = Column(Float, nullable=True)  # Mean Time To Recovery
    
    # Assignments
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    
    # SLO tracking
    slo_breached = Column(Boolean, default=False)
    slo_target_minutes = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="incidents")
    assigned_to = relationship("User")
    timeline = relationship("IncidentTimeline", back_populates="incident", order_by="IncidentTimeline.created_at")
    hypotheses = relationship("IncidentHypothesis", back_populates="incident")
    agent_executions = relationship("AgentExecution", back_populates="incident")
    infrastructure_components = relationship("InfrastructureComponent", order_by="InfrastructureComponent.created_at")
    verification_gates = relationship("VerificationGate", order_by="VerificationGate.created_at")
    executions = relationship("IncidentExecution", order_by="IncidentExecution.created_at")
    
    @property
    def is_open(self) -> bool:
        """Check if incident is still open"""
        return self.status in [IncidentStatus.OPEN.value, IncidentStatus.INVESTIGATING.value, IncidentStatus.RESOLVING.value]
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Get incident duration in minutes"""
        if not self.resolved_at:
            return None
        
        start_time = self.created_at
        end_time = self.resolved_at
        return (end_time - start_time).total_seconds() / 60


class IncidentTimeline(Base):
    """Incident timeline entries"""
    __tablename__ = "incident_timeline"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Entry details
    entry_type = Column(String(100), nullable=False)  # alert, action, log, deploy, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Source
    source = Column(String(255), nullable=True)  # System that created this entry
    source_id = Column(String(255), nullable=True)  # External ID
    
    # Metadata
    entry_metadata = Column(JSON, nullable=True)  # Additional structured data
    severity = Column(String(50), nullable=True)
    
    # User context
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    incident = relationship("Incident", back_populates="timeline")
    created_by = relationship("User")


class IncidentHypothesis(Base):
    """Incident investigation hypotheses"""
    __tablename__ = "incident_hypotheses"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Hypothesis details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    likelihood = Column(Float, nullable=False)  # 0-100 probability
    
    # Evidence
    supporting_evidence = Column(JSON, nullable=True)  # List of evidence items
    contradicting_evidence = Column(JSON, nullable=True)
    
    # Status
    is_confirmed = Column(Boolean, nullable=True)  # True/False/None (unknown)
    confirmation_notes = Column(Text, nullable=True)
    
    # AI-generated
    generated_by_ai = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)  # AI confidence
    
    # User context
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="hypotheses")
    created_by = relationship("User", foreign_keys=[created_by_id])
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])
