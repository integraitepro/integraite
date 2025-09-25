"""
Agent models for autonomous operations
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, Optional

from app.core.database import Base


class AgentType(PyEnum):
    """Types of infrastructure agents"""
    COMPUTE = "compute"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    MONITORING = "monitoring"
    CONTAINER = "container"
    STORAGE = "storage"
    API = "api"


class AgentStatus(PyEnum):
    """Agent operational status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DEPLOYING = "deploying"
    STOPPED = "stopped"


class ExecutionStatus(PyEnum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent(Base):
    """AI Agent model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # AgentType enum
    status = Column(String(50), default=AgentStatus.ACTIVE.value)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Agent-specific configuration
    environment = Column(String(100), default="production")  # production, staging, development
    
    # Performance metrics
    confidence_score = Column(Float, default=0.0)  # 0-100
    success_rate = Column(Float, default=0.0)  # 0-100
    incidents_handled = Column(Integer, default=0)
    
    # Resource allocation
    cpu_limit = Column(Float, default=1.0)  # CPU cores
    memory_limit = Column(Integer, default=512)  # MB
    
    # Monitoring
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    last_action = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="agents")
    executions = relationship("AgentExecution", back_populates="agent")
    metrics = relationship("AgentMetrics", back_populates="agent")
    
    @property
    def is_healthy(self) -> bool:
        """Check if agent is healthy based on last heartbeat"""
        if not self.last_heartbeat:
            return False
        
        # Consider agent unhealthy if no heartbeat in last 5 minutes
        threshold = datetime.utcnow().timestamp() - 300  # 5 minutes
        return self.last_heartbeat.timestamp() > threshold
    
    @property
    def layer(self) -> str:
        """Get the infrastructure layer this agent operates on"""
        layer_mapping = {
            AgentType.COMPUTE: "Infrastructure",
            AgentType.DATABASE: "Data",
            AgentType.NETWORK: "Network", 
            AgentType.SECURITY: "Security",
            AgentType.MONITORING: "Observability",
            AgentType.CONTAINER: "Container",
            AgentType.STORAGE: "Storage",
            AgentType.API: "Application"
        }
        return layer_mapping.get(AgentType(self.type), "Unknown")


class AgentExecution(Base):
    """Agent execution/action history (Legacy)"""
    __tablename__ = "legacy_agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # Can be null for incident-specific agents
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    # Execution details
    action_type = Column(String(100), nullable=True)  # restart, scale, patch, etc.
    description = Column(Text, nullable=True)
    status = Column(String(50), default=ExecutionStatus.PENDING.value)
    
    # Context
    trigger_reason = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-100
    
    # Results
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    output = Column(JSON, nullable=True)  # Execution output/logs
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Incident-specific fields for detailed tracking
    agent_external_id = Column(String(255), nullable=True)  # Reference to deployed agent
    agent_name = Column(String(255), nullable=True)
    agent_type = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)  # Lead Investigator, Supporting Analyst, etc.
    current_action = Column(String(500), nullable=True)
    progress = Column(Float, default=0.0)  # 0-100 percentage
    confidence = Column(Float, nullable=True)  # 0-100 confidence level (incident-specific)
    findings = Column(JSON, nullable=True)  # List of findings
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    execution_data = Column(JSON, nullable=True)  # Additional execution data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")
    incident = relationship("Incident")
    
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed"""
        return self.status in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value]


class AgentMetrics(Base):
    """Agent performance metrics over time"""
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Resource usage
    cpu_usage = Column(Float, nullable=True)  # Percentage
    memory_usage = Column(Float, nullable=True)  # MB
    network_io = Column(Float, nullable=True)  # MB/s
    
    # Performance metrics
    actions_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)  # Seconds
    
    # Custom metrics (agent-specific)
    custom_metrics = Column(JSON, nullable=True)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="metrics")
