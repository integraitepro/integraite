"""
Extended incident management models for detailed incident tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, List, Optional

from app.core.database import Base


# Note: AgentExecution is already defined in agent.py
# We'll extend that model instead of creating a duplicate


class InfrastructureComponent(Base):
    """Infrastructure components affected by incidents"""
    __tablename__ = "infrastructure_components"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Component details
    name = Column(String(255), nullable=False)
    component_type = Column(String(100), nullable=False)  # EC2 Instance, Load Balancer, etc.
    layer = Column(String(100), nullable=False)  # Application, Network, Data
    status = Column(String(50), nullable=False)  # healthy, degraded, critical
    
    # Metrics
    metrics = Column(JSON, nullable=True)  # Current metrics with normal baselines
    
    # Agent actions on this component
    agent_actions = Column(JSON, nullable=True)  # List of agent actions
    
    # Component metadata
    component_metadata = Column(JSON, nullable=True)  # Additional component data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    incident = relationship("Incident")


class VerificationGate(Base):
    """Verification gates for incident resolution"""
    __tablename__ = "verification_gates"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Gate details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_value = Column(String(100), nullable=False)
    current_value = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    progress = Column(Float, default=0.0)  # 0-100 percentage
    
    # Timing
    time_remaining = Column(String(100), nullable=True)
    
    # Gate metadata
    gate_metadata = Column(JSON, nullable=True)  # Additional gate configuration
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    incident = relationship("Incident")


class IncidentExecution(Base):
    """Incident execution plan tracking"""
    __tablename__ = "incident_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    # Execution plan details
    plan_id = Column(String(100), nullable=False)
    plan_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Progress tracking
    status = Column(String(50), default="pending")  # pending, executing, completed, failed
    progress = Column(Float, default=0.0)  # 0-100 percentage
    
    # Timing
    estimated_duration_minutes = Column(Float, nullable=True)
    actual_duration_minutes = Column(Float, nullable=True)
    
    # Root cause
    root_cause = Column(Text, nullable=True)
    
    # Execution metadata
    execution_metadata = Column(JSON, nullable=True)  # Additional execution data
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    incident = relationship("Incident")


class PreExecutionCheck(Base):
    """Pre-execution safety checks"""
    __tablename__ = "pre_execution_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_execution_id = Column(Integer, ForeignKey("incident_executions.id"), nullable=False)
    
    # Check details
    check_name = Column(String(255), nullable=False)
    check_description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, passed, failed
    
    # Check metadata
    check_metadata = Column(JSON, nullable=True)  # Additional check data
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    execution = relationship("IncidentExecution")
