"""
Integration models for external services
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, Optional

from app.core.database import Base


class IntegrationType(PyEnum):
    """Types of integrations"""
    MONITORING = "monitoring"
    INCIDENT_MANAGEMENT = "incident_management"
    TICKETING = "ticketing"
    CLOUD_PLATFORM = "cloud_platform"
    CI_CD = "ci_cd"
    COMMUNICATION = "communication"
    SECURITY = "security"
    OBSERVABILITY = "observability"


class IntegrationStatus(PyEnum):
    """Integration connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONFIGURING = "configuring"


class Integration(Base):
    """External service integration"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    service_name = Column(String(100), nullable=False)  # prometheus, datadog, etc.
    type = Column(String(50), nullable=False)  # IntegrationType enum
    description = Column(Text, nullable=True)
    
    # Connection
    status = Column(String(50), default=IntegrationStatus.CONFIGURING.value)
    endpoint_url = Column(String(500), nullable=True)
    
    # Configuration
    config = Column(JSON, nullable=False)  # Service-specific configuration
    auth_config = Column(JSON, nullable=True)  # Encrypted authentication data
    
    # Features
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    can_execute = Column(Boolean, default=False)
    
    # Health monitoring
    last_sync = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    sync_interval_minutes = Column(Integer, default=5)
    
    # Rate limiting
    rate_limit_requests = Column(Integer, default=100)
    rate_limit_window_seconds = Column(Integer, default=60)
    
    # User context
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="integrations")
    created_by = relationship("User")
    
    @property
    def is_healthy(self) -> bool:
        """Check if integration is healthy"""
        if self.status != IntegrationStatus.CONNECTED.value:
            return False
        
        if not self.last_sync:
            return False
        
        # Consider unhealthy if no sync in expected interval + buffer
        expected_interval = self.sync_interval_minutes * 60  # Convert to seconds
        buffer = 300  # 5 minute buffer
        threshold = datetime.utcnow().timestamp() - (expected_interval + buffer)
        
        return self.last_sync.timestamp() > threshold


class IntegrationConfig(Base):
    """Integration configuration templates and validation"""
    __tablename__ = "integration_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Service info
    service_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration schema
    config_schema = Column(JSON, nullable=False)  # JSON schema for validation
    auth_schema = Column(JSON, nullable=True)  # Authentication schema
    
    # Capabilities
    supported_features = Column(JSON, nullable=False)  # List of supported features
    required_permissions = Column(JSON, nullable=True)  # Required API permissions
    
    # Documentation
    setup_instructions = Column(Text, nullable=True)
    documentation_url = Column(String(500), nullable=True)
    
    # Metadata
    logo_url = Column(String(500), nullable=True)
    vendor = Column(String(255), nullable=True)
    is_popular = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
