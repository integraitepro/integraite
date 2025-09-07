"""
Integration models for managing external service connections
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

from app.core.database import Base


class IntegrationCategory(PyEnum):
    """Integration categories"""
    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"
    MONITORING = "monitoring"
    INCIDENT_MANAGEMENT = "incident_management"
    COMMUNICATION = "communication"
    VERSION_CONTROL = "version_control"
    CI_CD = "ci_cd"
    SECURITY = "security"
    DATABASE = "database"
    CONTAINER = "container"
    LOGGING = "logging"
    ANALYTICS = "analytics"
    STORAGE = "storage"
    NETWORKING = "networking"
    OTHER = "other"


class IntegrationStatus(PyEnum):
    """Integration status"""
    AVAILABLE = "available"
    COMING_SOON = "coming_soon"
    BETA = "beta"
    DEPRECATED = "deprecated"


class ConfigurationFieldType(PyEnum):
    """Configuration field types"""
    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"
    URL = "url"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    JSON = "json"
    FILE = "file"


class IntegrationProvider(Base):
    """Integration provider/service definition"""
    __tablename__ = "integration_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default=IntegrationCategory.OTHER.value)
    status = Column(String(50), default=IntegrationStatus.AVAILABLE.value)
    
    # Branding
    icon_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    brand_color = Column(String(7), nullable=True)  # Hex color
    
    # Documentation
    documentation_url = Column(String(500), nullable=True)
    setup_guide_url = Column(String(500), nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags
    supported_features = Column(JSON, nullable=True)  # List of features
    
    # Availability
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    configuration_fields = relationship("IntegrationConfigurationField", back_populates="provider", cascade="all, delete-orphan")
    user_integrations = relationship("UserIntegration", back_populates="provider")
    integration_requests = relationship("IntegrationRequest", back_populates="provider")


class IntegrationConfigurationField(Base):
    """Configuration fields required for each integration"""
    __tablename__ = "integration_configuration_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("integration_providers.id"), nullable=False)
    
    # Field definition
    field_name = Column(String(100), nullable=False)  # Internal name
    display_label = Column(String(255), nullable=False)  # User-facing label
    field_type = Column(String(50), default=ConfigurationFieldType.TEXT.value)
    description = Column(Text, nullable=True)
    placeholder = Column(String(255), nullable=True)
    
    # Validation
    is_required = Column(Boolean, default=True)
    is_sensitive = Column(Boolean, default=False)  # For passwords, tokens, etc.
    validation_regex = Column(String(500), nullable=True)
    validation_message = Column(String(255), nullable=True)
    
    # Field options (for select/multiselect)
    field_options = Column(JSON, nullable=True)  # [{"value": "val", "label": "Label"}]
    default_value = Column(String(500), nullable=True)
    
    # Ordering and grouping
    sort_order = Column(Integer, default=0)
    field_group = Column(String(100), nullable=True)  # Group related fields
    
    # Relationships
    provider = relationship("IntegrationProvider", back_populates="configuration_fields")


class UserIntegration(Base):
    """User's configured integrations"""
    __tablename__ = "user_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("integration_providers.id"), nullable=False)
    
    # Configuration
    name = Column(String(255), nullable=False)  # User-given name for this integration
    description = Column(Text, nullable=True)
    configuration = Column(JSON, nullable=False)  # Encrypted configuration values
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Whether connection was tested successfully
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    integration_metadata = Column(JSON, nullable=True)  # Additional provider-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")
    organization = relationship("Organization", back_populates="integrations")
    provider = relationship("IntegrationProvider", back_populates="user_integrations")


class IntegrationRequest(Base):
    """Requests for new integrations not currently supported"""
    __tablename__ = "integration_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("integration_providers.id"), nullable=True)  # If requesting existing but inactive
    
    # Request details
    service_name = Column(String(255), nullable=False)
    service_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    business_justification = Column(Text, nullable=True)
    expected_usage = Column(Text, nullable=True)
    
    # Classification
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    category = Column(String(50), nullable=True)
    estimated_users = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, reviewed, in_progress, completed, rejected
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization")
    provider = relationship("IntegrationProvider", back_populates="integration_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class IntegrationWebhook(Base):
    """Webhook endpoints for integrations"""
    __tablename__ = "integration_webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_integration_id = Column(Integer, ForeignKey("user_integrations.id"), nullable=False)
    
    # Webhook configuration
    webhook_url = Column(String(500), nullable=False)
    webhook_secret = Column(String(255), nullable=True)
    event_types = Column(JSON, nullable=True)  # List of events to listen for
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    last_call_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    user_integration = relationship("UserIntegration")