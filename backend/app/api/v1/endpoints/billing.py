"""
Billing and subscription endpoints
"""

from fastapi import APIRouter, Depends
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_active_user)
):
    """Get current subscription details"""
    # TODO: Implement subscription details
    return {"plan": "free", "status": "active"}


@router.post("/upgrade")
async def upgrade_subscription(
    current_user: User = Depends(get_current_active_user)
):
    """Upgrade subscription"""
    # TODO: Implement Stripe integration for upgrades
    return {"message": "Subscription upgrade initiated"}


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_active_user)
):
    """Get usage statistics"""
    # TODO: Implement usage tracking
    return {"usage": {}}
