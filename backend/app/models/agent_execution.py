"""
Agent models for SRE automation and execution tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import Base


class Agent(Base):
    """Agent configuration and metadata"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Agent identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_type = Column(String(100), nullable=False)  # 'sre', 'network', 'database', etc.
    version = Column(String(50), default="1.0.0")
    
    # Agent configuration
    configuration = Column(JSON)  # Stores agent-specific config like SSH details, API keys, etc.
    environment_variables = Column(JSON)  # Secure storage for env vars
    capabilities = Column(JSON)  # List of what this agent can do
    
    # Status and metadata
    status = Column(String(50), default="active")  # active, inactive, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.agent_type}')>"


class AgentExecution(Base):
    """Individual agent execution/run"""
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)  # Can be manual runs
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Execution metadata
    execution_id = Column(String(100), unique=True, nullable=False)  # UUID for tracking
    trigger_type = Column(String(50), nullable=False)  # 'manual', 'automatic', 'scheduled'
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Execution state
    status = Column(String(50), default="running")  # running, completed, failed, cancelled
    current_step = Column(String(255))  # Current action being performed
    progress_percentage = Column(Float, default=0.0)
    
    # Results and findings
    final_status = Column(String(50))  # success, partial_success, failure
    summary = Column(Text)  # Human-readable summary of what was done
    root_cause = Column(Text)  # Identified root cause
    resolution_applied = Column(Text)  # What fix was applied
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Execution context
    input_data = Column(JSON)  # Initial parameters/context
    output_data = Column(JSON)  # Final results/artifacts
    error_message = Column(Text)  # Error details if failed
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")
    timeline_entries = relationship("AgentTimelineEntry", back_populates="execution", cascade="all, delete-orphan")
    hypotheses = relationship("AgentHypothesis", back_populates="execution", cascade="all, delete-orphan")
    verifications = relationship("AgentVerification", back_populates="execution", cascade="all, delete-orphan")
    evidence = relationship("AgentEvidence", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentExecution(id={self.id}, execution_id='{self.execution_id}', status='{self.status}')>"


class AgentTimelineEntry(Base):
    """Timeline entries for agent execution"""
    __tablename__ = "agent_timeline_entries"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    # Timeline entry details
    step_number = Column(Integer, nullable=False)
    action_type = Column(String(100), nullable=False)  # 'diagnosis', 'command', 'analysis', 'remediation'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Command details (for SSH commands)
    command = Column(Text)  # The actual command executed
    target_host = Column(String(255))  # IP/hostname where command was run
    
    # Results
    success = Column(Boolean, default=True)
    stdout = Column(Text)  # Command output
    stderr = Column(Text)  # Command errors
    exit_code = Column(Integer)
    duration_ms = Column(Integer)  # How long the step took
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON)  # Additional context/data
    
    # Relationships
    execution = relationship("AgentExecution", back_populates="timeline_entries")
    
    def __repr__(self):
        return f"<AgentTimelineEntry(id={self.id}, step={self.step_number}, action='{self.action_type}')>"


class AgentHypothesis(Base):
    """Agent hypotheses about incident causes"""
    __tablename__ = "agent_hypotheses"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    # Hypothesis details
    hypothesis_text = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    category = Column(String(100))  # 'system', 'network', 'application', 'configuration'
    
    # Testing and validation
    test_plan = Column(Text)  # How to test this hypothesis
    test_results = Column(Text)  # Results of testing
    status = Column(String(50), default="proposed")  # proposed, testing, confirmed, rejected
    
    # Supporting evidence
    supporting_evidence = Column(JSON)  # References to evidence that supports this
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    execution = relationship("AgentExecution", back_populates="hypotheses")
    
    def __repr__(self):
        return f"<AgentHypothesis(id={self.id}, confidence={self.confidence_score}, status='{self.status}')>"


class AgentVerification(Base):
    """Verification steps and gates for agent actions"""
    __tablename__ = "agent_verifications"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    # Verification details
    verification_type = Column(String(100), nullable=False)  # 'pre_check', 'post_action', 'final_validation'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Expected vs actual
    expected_result = Column(Text)
    actual_result = Column(Text)
    verification_command = Column(Text)  # Command used to verify
    
    # Status
    status = Column(String(50), default="pending")  # pending, passed, failed, skipped
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSON)  # Additional verification data
    
    # Relationships
    execution = relationship("AgentExecution", back_populates="verifications")
    
    def __repr__(self):
        return f"<AgentVerification(id={self.id}, type='{self.verification_type}', status='{self.status}')>"


class AgentEvidence(Base):
    """Evidence collected by agents during execution"""
    __tablename__ = "agent_evidence"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    # Evidence details
    evidence_type = Column(String(100), nullable=False)  # 'log', 'metric', 'command_output', 'file', 'config'
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Evidence content
    content = Column(Text)  # The actual evidence data
    source = Column(String(255))  # Where this evidence came from
    file_path = Column(String(500))  # If evidence is stored as file
    
    # Classification
    relevance_score = Column(Float, default=0.0)  # How relevant to the incident (0.0-1.0)
    category = Column(String(100))  # 'critical', 'supporting', 'contextual'
    tags = Column(JSON)  # Searchable tags
    
    # Metadata
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    size_bytes = Column(Integer)  # Size of evidence if it's a file
    checksum = Column(String(64))  # For integrity verification
    
    # Relationships
    execution = relationship("AgentExecution", back_populates="evidence")
    
    def __repr__(self):
        return f"<AgentEvidence(id={self.id}, type='{self.evidence_type}', title='{self.title}')>"


class AgentProvenance(Base):
    """Provenance tracking for agent decisions and actions"""
    __tablename__ = "agent_provenance"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    
    # Action tracking
    action_id = Column(String(100), nullable=False)  # Unique ID for this action
    action_type = Column(String(100), nullable=False)  # 'decision', 'command', 'analysis'
    action_description = Column(Text)
    
    # Decision reasoning
    reasoning = Column(Text)  # Why this action was taken
    input_data = Column(JSON)  # What data was used to make this decision
    model_used = Column(String(100))  # AI model that made the decision
    model_parameters = Column(JSON)  # Model parameters/settings
    
    # Traceability
    parent_action_id = Column(String(100))  # Previous action that led to this one
    triggers = Column(JSON)  # What triggered this action
    alternatives_considered = Column(JSON)  # Other options that were considered
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confidence_level = Column(Float)  # Confidence in this decision
    
    def __repr__(self):
        return f"<AgentProvenance(id={self.id}, action_id='{self.action_id}', type='{self.action_type}')>"