"""
Organization schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class OrganizationCreate(BaseModel):
    """Organization creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str = Field(default="UTC")


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    timezone: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Organization response schema"""
    id: int
    name: str
    slug: str
    domain: Optional[str] = None
    plan: str = "free"
    max_agents: int = 10
    logo_url: Optional[str] = None
    description: Optional[str] = None
    timezone: str = "UTC"
    user_role: Optional[str] = None  # Added for frontend
    agents_count: int = 0
    integrations_count: int = 0
    team_size: int = 1
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class OrganizationMemberResponse(BaseModel):
    """Organization member response schema"""
    id: int
    role: str
    joined_at: datetime
    user: "UserResponse"  # Forward reference
    
    model_config = {"from_attributes": True}


class InviteUserRequest(BaseModel):
    """Invite user to organization"""
    email: str
    role: str = Field(..., pattern="^(owner|admin|member|viewer)$")
    message: Optional[str] = None


# Import here to avoid circular imports
from app.schemas.auth import UserResponse
OrganizationMemberResponse.model_rebuild()
