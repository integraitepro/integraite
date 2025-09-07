"""
User and Organization models for multi-tenant architecture
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from app.core.database import Base


class UserRole(PyEnum):
    """User roles within an organization"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class PlanType(PyEnum):
    """Organization subscription plans"""
    FREE = "free"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    google_id = Column(String(255), nullable=True, unique=True)
    microsoft_id = Column(String(255), nullable=True, unique=True)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization_memberships = relationship("OrganizationMember", back_populates="user", foreign_keys="OrganizationMember.user_id")
    integrations = relationship("UserIntegration", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def primary_organization(self) -> Optional["Organization"]:
        """Get the user's primary organization (first one they joined)"""
        if self.organization_memberships:
            return self.organization_memberships[0].organization
        return None


class Organization(Base):
    """Organization model for multi-tenancy"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    domain = Column(String(255), nullable=True)  # For SSO and verification
    
    # Subscription
    plan = Column(Enum(PlanType), default=PlanType.FREE)
    max_agents = Column(Integer, default=5)
    
    # Settings
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Features
    sso_enabled = Column(Boolean, default=False)
    audit_retention_days = Column(Integer, default=90)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("OrganizationMember", back_populates="organization")
    integrations = relationship("UserIntegration", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    incidents = relationship("Incident", back_populates="organization")
    automations = relationship("Automation", back_populates="organization")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)
    
    @property
    def member_count(self) -> int:
        return len(self.members)
    
    @property
    def active_agents_count(self) -> int:
        return len([agent for agent in self.agents if agent.is_active])


class OrganizationMember(Base):
    """Many-to-many relationship between Users and Organizations with roles"""
    __tablename__ = "organization_members"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    
    # Invitation fields
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships", foreign_keys=[user_id])
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    def can_manage_agents(self) -> bool:
        """Check if user can manage agents"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    def can_manage_members(self) -> bool:
        """Check if user can manage organization members"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
    
    def can_view_billing(self) -> bool:
        """Check if user can view billing information"""
        return self.role in [UserRole.OWNER, UserRole.ADMIN]
