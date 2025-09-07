"""
User management endpoints
"""

from fastapi import APIRouter, Depends
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Update current user profile"""
    # TODO: Implement user profile update
    return UserResponse.model_validate(current_user)
