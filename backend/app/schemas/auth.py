"""
Authentication schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    timezone: str
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    """Google OAuth request"""
    id_token: str
    organization_name: Optional[str] = None


class MicrosoftAuthRequest(BaseModel):
    """Microsoft OAuth request"""
    access_token: str
    organization_name: Optional[str] = None
