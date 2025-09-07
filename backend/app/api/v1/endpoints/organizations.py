"""
Organization management endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=Dict[str, List[OrganizationResponse]])
async def list_organizations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's organizations"""
    # Get organizations where user is a member
    result = await db.execute(
        select(Organization, OrganizationMember.role)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .order_by(Organization.created_at.desc())
    )
    
    organizations_data = []
    for org, role in result.all():
        # Manually construct response to avoid async property issues
        org_data = OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            domain=org.domain,
            plan=org.plan,
            max_agents=org.max_agents,
            logo_url=org.logo_url,
            description=org.description,
            timezone=org.timezone,
            user_role=role.value,
            agents_count=0,  # TODO: Calculate actual count
            integrations_count=0,  # TODO: Calculate actual count
            team_size=1,  # TODO: Calculate actual count
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
        organizations_data.append(org_data)
    
    return {"organizations": organizations_data}


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    organization_data: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization"""
    # Check if organization name already exists (for the user)
    result = await db.execute(
        select(Organization)
        .join(OrganizationMember)
        .where(
            OrganizationMember.user_id == current_user.id,
            Organization.name == organization_data.name
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this name already exists"
        )
    
    # Create organization
    organization = Organization(
        name=organization_data.name,
        slug=organization_data.name.lower().replace(" ", "-").replace("_", "-"),
        description=organization_data.description,
        logo_url=organization_data.logo_url,
        timezone=organization_data.timezone,
    )
    
    db.add(organization)
    await db.flush()  # Get organization.id
    
    # Add user as organization owner
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role=UserRole.OWNER,
    )
    db.add(membership)
    
    await db.commit()
    await db.refresh(organization)
    
    # Return organization with user role - manually construct to avoid async issues
    org_response = OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        domain=organization.domain,
        plan=organization.plan,
        max_agents=organization.max_agents,
        logo_url=organization.logo_url,
        description=organization.description,
        timezone=organization.timezone,
        user_role=UserRole.OWNER.value,
        agents_count=0,
        integrations_count=0,
        team_size=1,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )
    
    return org_response


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization details"""
    # Check if user has access to this organization
    result = await db.execute(
        select(Organization, OrganizationMember.role)
        .join(OrganizationMember)
        .where(
            Organization.id == organization_id,
            OrganizationMember.user_id == current_user.id
        )
    )
    
    org_data = result.first()
    if not org_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization, role = org_data
    # Manually construct response to avoid async property issues
    org_response = OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        domain=organization.domain,
        plan=organization.plan,
        max_agents=organization.max_agents,
        logo_url=organization.logo_url,
        description=organization.description,
        timezone=organization.timezone,
        user_role=role.value,
        agents_count=0,  # TODO: Calculate actual count
        integrations_count=0,  # TODO: Calculate actual count
        team_size=1,  # TODO: Calculate actual count
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )
    
    return org_response


@router.put("/{organization_id}/switch")
async def switch_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Switch to a different organization"""
    # Verify user has access to this organization
    result = await db.execute(
        select(Organization, OrganizationMember.role)
        .join(OrganizationMember)
        .where(
            Organization.id == organization_id,
            OrganizationMember.user_id == current_user.id
        )
    )
    
    org_data = result.first()
    if not org_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied"
        )
    
    organization, role = org_data
    
    return {
        "success": True,
        "message": f"Switched to {organization.name}",
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
            "role": role.value
        }
    }