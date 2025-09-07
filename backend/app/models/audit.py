"""
Audit logging model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, Optional

from app.core.database import Base


class AuditAction(PyEnum):
    """Types of audit actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXECUTE = "execute"
    APPROVE = "approve"
    DEPLOY = "deploy"
    ACCESS = "access"


class AuditResource(PyEnum):
    """Types of resources being audited"""
    USER = "user"
    ORGANIZATION = "organization"
    AGENT = "agent"
    INCIDENT = "incident"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    BILLING = "billing"
    SETTINGS = "settings"


class AuditLog(Base):
    """Audit log model for compliance and security"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for system actions
    
    # Action details
    action = Column(String(50), nullable=False)  # AuditAction enum
    resource_type = Column(String(50), nullable=False)  # AuditResource enum
    resource_id = Column(String(255), nullable=True)  # ID of the resource affected
    resource_name = Column(String(255), nullable=True)  # Human-readable name
    
    # Context
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional structured data
    
    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # API context
    api_endpoint = Column(String(255), nullable=True)
    http_method = Column(String(10), nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values for updates
    
    # Risk assessment
    risk_level = Column(String(50), default="low")  # low, medium, high, critical
    is_sensitive = Column(Boolean, default=False)
    
    # Compliance
    compliance_tags = Column(JSON, nullable=True)  # Tags for compliance tracking
    retention_until = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User", back_populates="audit_logs")
    
    @property
    def is_expired(self) -> bool:
        """Check if audit log has expired based on retention policy"""
        if not self.retention_until:
            return False
        return datetime.utcnow() > self.retention_until
    
    @classmethod
    def log_action(
        cls,
        organization_id: int,
        action: AuditAction,
        resource_type: AuditResource,
        description: str,
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        risk_level: str = "low",
        is_sensitive: bool = False,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> "AuditLog":
        """
        Helper method to create audit log entries
        """
        return cls(
            organization_id=organization_id,
            user_id=user_id,
            action=action.value,
            resource_type=resource_type.value,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            details=details,
            old_values=old_values,
            new_values=new_values,
            risk_level=risk_level,
            is_sensitive=is_sensitive,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            api_endpoint=api_endpoint,
            http_method=http_method,
            request_id=request_id,
        )
