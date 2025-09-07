"""
Automation and playbook models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, List, Optional

from app.core.database import Base


class AutomationType(PyEnum):
    """Types of automations"""
    PLAYBOOK = "playbook"
    RUNBOOK = "runbook"
    POLICY = "policy"
    WORKFLOW = "workflow"


class AutomationTrigger(PyEnum):
    """Automation trigger types"""
    INCIDENT = "incident"
    ALERT = "alert"
    METRIC_THRESHOLD = "metric_threshold"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    WEBHOOK = "webhook"


class ExecutionMode(PyEnum):
    """Automation execution modes"""
    AUTOMATIC = "automatic"
    APPROVAL_REQUIRED = "approval_required"
    MANUAL_ONLY = "manual_only"


class Automation(Base):
    """Automation/Playbook model"""
    __tablename__ = "automations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # AutomationType enum
    category = Column(String(100), nullable=True)
    
    # Configuration
    trigger_type = Column(String(50), nullable=False)  # AutomationTrigger enum
    trigger_config = Column(JSON, nullable=False)  # Trigger-specific configuration
    
    # Execution
    execution_mode = Column(String(50), default=ExecutionMode.APPROVAL_REQUIRED.value)
    steps = Column(JSON, nullable=False)  # List of automation steps
    
    # Risk assessment
    confidence_threshold = Column(Float, default=80.0)  # Minimum confidence to execute
    blast_radius = Column(String(50), default="low")  # low, medium, high
    max_concurrent_executions = Column(Integer, default=1)
    
    # Conditions
    pre_conditions = Column(JSON, nullable=True)  # Pre-execution checks
    post_conditions = Column(JSON, nullable=True)  # Post-execution verification
    
    # Settings
    is_active = Column(Boolean, default=True)
    timeout_minutes = Column(Integer, default=30)
    retry_count = Column(Integer, default=0)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=True)
    approvers = Column(JSON, nullable=True)  # List of user IDs who can approve
    
    # Usage tracking
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    last_executed = Column(DateTime(timezone=True), nullable=True)
    
    # User context
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="automations")
    created_by = relationship("User")
    executions = relationship("AutomationExecution", back_populates="automation")
    
    @property
    def is_high_risk(self) -> bool:
        """Check if automation is considered high risk"""
        return self.blast_radius == "high" or self.execution_mode == ExecutionMode.AUTOMATIC.value


class AutomationExecution(Base):
    """Automation execution history"""
    __tablename__ = "automation_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    # Execution context
    trigger_data = Column(JSON, nullable=True)  # Data that triggered the execution
    execution_mode = Column(String(50), nullable=False)  # How it was executed
    
    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Execution details
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, nullable=False)
    
    # Results
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    output = Column(JSON, nullable=True)  # Execution output
    
    # Verification
    pre_check_results = Column(JSON, nullable=True)
    post_check_results = Column(JSON, nullable=True)
    verification_status = Column(String(50), nullable=True)  # passed, failed, pending
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # User context
    executed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    automation = relationship("Automation", back_populates="executions")
    incident = relationship("Incident")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    executed_by = relationship("User", foreign_keys=[executed_by_id])
    
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed"""
        return self.status in ["completed", "failed"]
    
    @property
    def needs_approval(self) -> bool:
        """Check if execution needs approval"""
        return self.execution_mode == ExecutionMode.APPROVAL_REQUIRED.value and not self.approved_at
