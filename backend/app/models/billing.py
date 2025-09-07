"""
Billing and subscription models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import Dict, Any, Optional
from decimal import Decimal

from app.core.database import Base


class SubscriptionStatus(PyEnum):
    """Subscription status"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class UsageType(PyEnum):
    """Types of usage tracking"""
    AGENT_HOURS = "agent_hours"
    INCIDENTS_PROCESSED = "incidents_processed"
    API_CALLS = "api_calls"
    STORAGE_GB = "storage_gb"
    SEATS = "seats"


class Subscription(Base):
    """Organization subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Plan details
    plan_type = Column(String(50), nullable=False)  # free, team, enterprise
    plan_name = Column(String(255), nullable=False)
    
    # Pricing
    monthly_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(String(50), default=SubscriptionStatus.ACTIVE.value)
    is_trial = Column(Boolean, default=False)
    
    # Limits
    max_agents = Column(Integer, default=5)
    max_seats = Column(Integer, default=5)
    max_incidents_per_month = Column(Integer, nullable=True)
    max_api_calls_per_month = Column(Integer, nullable=True)
    max_storage_gb = Column(Integer, nullable=True)
    
    # Features
    features = Column(JSON, nullable=True)  # List of enabled features
    
    # Billing cycle
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Payment
    last_payment_at = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    usage_records = relationship("Usage", back_populates="subscription")
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired"""
        if not self.is_trial or not self.trial_ends_at:
            return False
        return datetime.utcnow() > self.trial_ends_at
    
    @property
    def days_until_billing(self) -> Optional[int]:
        """Days until next billing"""
        if not self.next_billing_date:
            return None
        
        delta = self.next_billing_date - datetime.utcnow()
        return max(0, delta.days)


class Usage(Base):
    """Usage tracking for billing"""
    __tablename__ = "usage"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Usage details
    usage_type = Column(String(50), nullable=False)  # UsageType enum
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False)  # hours, count, gb, etc.
    
    # Billing period
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Pricing
    unit_price = Column(Numeric(10, 4), nullable=True)  # Price per unit
    total_cost = Column(Numeric(10, 2), nullable=True)  # Total cost for this usage
    
    # Metadata
    description = Column(String(500), nullable=True)
    usage_metadata = Column(JSON, nullable=True)  # Additional usage context
    
    # Limits
    included_quantity = Column(Float, default=0.0)  # Included in plan
    overage_quantity = Column(Float, default=0.0)  # Usage above limit
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")
    organization = relationship("Organization")
    
    @property
    def is_overage(self) -> bool:
        """Check if usage exceeds included quantity"""
        return self.quantity > self.included_quantity
    
    @property
    def overage_cost(self) -> Optional[Decimal]:
        """Calculate overage cost"""
        if not self.is_overage or not self.unit_price:
            return None
        
        return Decimal(str(self.overage_quantity)) * self.unit_price
