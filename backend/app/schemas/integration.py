"""
Integration API schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class IntegrationProviderBase(BaseModel):
    """Base integration provider schema"""
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(default="other")
    status: str = Field(default="available")
    
    # Branding
    icon_url: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    
    # Documentation
    documentation_url: Optional[str] = None
    setup_guide_url: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = []
    supported_features: Optional[List[str]] = []
    
    # Availability
    is_active: bool = True
    is_featured: bool = False
    requires_approval: bool = False


class IntegrationProviderCreate(IntegrationProviderBase):
    """Schema for creating integration providers"""
    pass


class IntegrationProviderUpdate(BaseModel):
    """Schema for updating integration providers"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    icon_url: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    documentation_url: Optional[str] = None
    setup_guide_url: Optional[str] = None
    tags: Optional[List[str]] = None
    supported_features: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    requires_approval: Optional[bool] = None


class ConfigurationFieldBase(BaseModel):
    """Base configuration field schema"""
    field_name: str = Field(..., min_length=1, max_length=100)
    display_label: str = Field(..., min_length=1, max_length=255)
    field_type: str = Field(default="text")
    description: Optional[str] = None
    placeholder: Optional[str] = None
    
    # Validation
    is_required: bool = True
    is_sensitive: bool = False
    validation_regex: Optional[str] = None
    validation_message: Optional[str] = None
    
    # Field options
    field_options: Optional[List[Dict[str, str]]] = None
    default_value: Optional[str] = None
    
    # Ordering and grouping
    sort_order: int = 0
    field_group: Optional[str] = None


class ConfigurationFieldCreate(ConfigurationFieldBase):
    """Schema for creating configuration fields"""
    provider_id: int


class ConfigurationFieldResponse(ConfigurationFieldBase):
    """Configuration field response schema"""
    id: int
    provider_id: int
    
    model_config = {"from_attributes": True}


class IntegrationProviderResponse(IntegrationProviderBase):
    """Integration provider response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Include configuration fields
    configuration_fields: List[ConfigurationFieldResponse] = []
    
    # Statistics
    total_integrations: int = 0
    active_integrations: int = 0
    
    model_config = {"from_attributes": True}


class UserIntegrationBase(BaseModel):
    """Base user integration schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Dict[str, Any] = Field(..., description="Configuration values for the integration")
    tags: Optional[List[str]] = []
    integration_metadata: Optional[Dict[str, Any]] = {}


class UserIntegrationCreate(UserIntegrationBase):
    """Schema for creating user integrations"""
    provider_id: int


class UserIntegrationUpdate(BaseModel):
    """Schema for updating user integrations"""
    name: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    integration_metadata: Optional[Dict[str, Any]] = None


class UserIntegrationResponse(UserIntegrationBase):
    """User integration response schema"""
    id: int
    provider_id: int
    user_id: int
    organization_id: int
    
    # Status
    is_active: bool
    is_verified: bool
    last_sync_at: Optional[datetime]
    last_error: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Provider information
    provider: IntegrationProviderResponse
    
    model_config = {"from_attributes": True}


class IntegrationTestRequest(BaseModel):
    """Schema for testing integration connectivity"""
    configuration: Dict[str, Any] = Field(..., description="Configuration values to test")


class IntegrationTestResponse(BaseModel):
    """Integration test result schema"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[int] = None


class IntegrationRequestBase(BaseModel):
    """Base integration request schema"""
    service_name: str = Field(..., min_length=1, max_length=255)
    service_url: Optional[str] = None
    description: str = Field(..., min_length=10)
    business_justification: Optional[str] = None
    expected_usage: Optional[str] = None
    
    # Classification
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: Optional[str] = None
    estimated_users: Optional[int] = Field(None, ge=1)


class IntegrationRequestCreate(IntegrationRequestBase):
    """Schema for creating integration requests"""
    provider_id: Optional[int] = None  # If requesting existing but inactive provider


class IntegrationRequestUpdate(BaseModel):
    """Schema for updating integration requests"""
    status: Optional[str] = Field(None, pattern="^(pending|reviewed|in_progress|completed|rejected)$")
    admin_notes: Optional[str] = None


class IntegrationRequestResponse(IntegrationRequestBase):
    """Integration request response schema"""
    id: int
    user_id: int
    organization_id: int
    provider_id: Optional[int]
    
    # Status tracking
    status: str
    admin_notes: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # User information
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    model_config = {"from_attributes": True}


class IntegrationStatsResponse(BaseModel):
    """Integration statistics response schema"""
    total_providers: int
    active_providers: int
    total_user_integrations: int
    active_user_integrations: int
    pending_requests: int
    
    # Category breakdown
    providers_by_category: Dict[str, int]
    integrations_by_category: Dict[str, int]
    
    # Popular integrations
    popular_providers: List[Dict[str, Any]]


class IntegrationSyncRequest(BaseModel):
    """Schema for triggering integration sync"""
    force: bool = False


class IntegrationSyncResponse(BaseModel):
    """Integration sync result schema"""
    success: bool
    message: str
    synced_at: datetime
    records_synced: Optional[int] = None
    errors: Optional[List[str]] = None


class IntegrationWebhookBase(BaseModel):
    """Base webhook schema"""
    webhook_url: str = Field(..., pattern=r"^https?://.*")
    webhook_secret: Optional[str] = None
    event_types: Optional[List[str]] = []
    is_active: bool = True


class IntegrationWebhookCreate(IntegrationWebhookBase):
    """Schema for creating webhooks"""
    user_integration_id: int


class IntegrationWebhookResponse(IntegrationWebhookBase):
    """Webhook response schema"""
    id: int
    user_integration_id: int
    
    # Statistics
    total_calls: int
    successful_calls: int
    failed_calls: int
    last_call_at: Optional[datetime]
    last_success_at: Optional[datetime]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
