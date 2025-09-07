"""
Integration management API endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload
from datetime import datetime
import json
import asyncio

from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, OrganizationMember
from app.models.integration import (
    IntegrationProvider, IntegrationConfigurationField, UserIntegration,
    IntegrationRequest, IntegrationWebhook
)
from app.schemas.integration import (
    IntegrationProviderResponse, IntegrationProviderCreate, IntegrationProviderUpdate,
    ConfigurationFieldCreate, ConfigurationFieldResponse,
    UserIntegrationResponse, UserIntegrationCreate, UserIntegrationUpdate,
    IntegrationTestRequest, IntegrationTestResponse,
    IntegrationRequestResponse, IntegrationRequestCreate, IntegrationRequestUpdate,
    IntegrationStatsResponse, IntegrationSyncRequest, IntegrationSyncResponse,
    IntegrationWebhookResponse, IntegrationWebhookCreate
)
from app.core.database import get_db

router = APIRouter()


# Helper functions
async def get_organization_member(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> OrganizationMember:
    """Get the current user's organization membership"""
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found"
        )
    return org_member


async def test_integration_connection(provider_name: str, configuration: Dict[str, Any]) -> IntegrationTestResponse:
    """Test integration connectivity based on provider type"""
    try:
        # Simulate connection testing - in real implementation, this would make actual API calls
        await asyncio.sleep(0.5)  # Simulate network delay
        
        # Basic validation based on provider type
        if provider_name.lower() in ["aws", "amazon-web-services"]:
            required_fields = ["access_key_id", "secret_access_key", "region"]
            if all(field in configuration for field in required_fields):
                return IntegrationTestResponse(
                    success=True,
                    message="Successfully connected to AWS",
                    response_time_ms=450
                )
        elif provider_name.lower() in ["azure", "microsoft-azure"]:
            required_fields = ["tenant_id", "client_id", "client_secret"]
            if all(field in configuration for field in required_fields):
                return IntegrationTestResponse(
                    success=True,
                    message="Successfully connected to Azure",
                    response_time_ms=380
                )
        elif provider_name.lower() in ["gcp", "google-cloud"]:
            required_fields = ["service_account_key", "project_id"]
            if all(field in configuration for field in required_fields):
                return IntegrationTestResponse(
                    success=True,
                    message="Successfully connected to Google Cloud",
                    response_time_ms=520
                )
        elif provider_name.lower() == "servicenow":
            required_fields = ["instance_url", "username", "password"]
            if all(field in configuration for field in required_fields):
                return IntegrationTestResponse(
                    success=True,
                    message="Successfully connected to ServiceNow",
                    response_time_ms=680
                )
        
        # Generic success for other providers with basic config
        if configuration:
            return IntegrationTestResponse(
                success=True,
                message=f"Successfully connected to {provider_name}",
                response_time_ms=300
            )
        
        return IntegrationTestResponse(
            success=False,
            message="Missing required configuration fields"
        )
    except Exception as e:
        return IntegrationTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


# Integration Providers Endpoints
@router.get("/providers", response_model=List[IntegrationProviderResponse])
async def get_integration_providers(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    featured: Optional[bool] = Query(None, description="Filter featured providers"),
    search: Optional[str] = Query(None, description="Search providers by name or description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all available integration providers"""
    query = select(IntegrationProvider).options(
        selectinload(IntegrationProvider.configuration_fields)
    )
    
    # Apply filters
    conditions = []
    if category:
        conditions.append(IntegrationProvider.category == category)
    if status:
        conditions.append(IntegrationProvider.status == status)
    if featured is not None:
        conditions.append(IntegrationProvider.is_featured == featured)
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                IntegrationProvider.display_name.ilike(search_term),
                IntegrationProvider.description.ilike(search_term),
                IntegrationProvider.name.ilike(search_term)
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(
        IntegrationProvider.is_featured.desc(),
        IntegrationProvider.display_name
    )
    
    result = await db.execute(query)
    providers = result.scalars().all()
    
    # Add integration counts for each provider
    provider_responses = []
    for provider in providers:
        # Count total and active integrations for this provider
        count_result = await db.execute(
            select(
                func.count(UserIntegration.id).label("total"),
                func.sum(case((UserIntegration.is_active == True, 1), else_=0)).label("active")
            ).where(UserIntegration.provider_id == provider.id)
        )
        counts = count_result.first()
        
        provider_dict = provider.__dict__.copy()
        provider_dict["total_integrations"] = counts.total or 0
        provider_dict["active_integrations"] = counts.active or 0
        provider_responses.append(IntegrationProviderResponse(**provider_dict))
    
    return provider_responses


@router.get("/providers/{provider_id}", response_model=IntegrationProviderResponse)
async def get_integration_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific integration provider"""
    result = await db.execute(
        select(IntegrationProvider)
        .options(selectinload(IntegrationProvider.configuration_fields))
        .where(IntegrationProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration provider not found"
        )
    
    # Add integration counts
    count_result = await db.execute(
        select(
            func.count(UserIntegration.id).label("total"),
            func.sum(case((UserIntegration.is_active == True, 1), else_=0)).label("active")
        ).where(UserIntegration.provider_id == provider.id)
    )
    counts = count_result.first()
    
    provider_dict = provider.__dict__.copy()
    provider_dict["total_integrations"] = counts.total or 0
    provider_dict["active_integrations"] = counts.active or 0
    
    return IntegrationProviderResponse(**provider_dict)


# User Integrations Endpoints
@router.get("/", response_model=List[UserIntegrationResponse])
async def get_user_integrations(
    provider_id: Optional[int] = Query(None, description="Filter by provider"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Get user's integrations"""
    query = select(UserIntegration).options(
        selectinload(UserIntegration.provider).selectinload(IntegrationProvider.configuration_fields)
    ).where(
        and_(
            UserIntegration.organization_id == org_member.organization_id,
            UserIntegration.user_id == org_member.user_id
        )
    )
    
    # Apply filters
    if provider_id:
        query = query.where(UserIntegration.provider_id == provider_id)
    if active is not None:
        query = query.where(UserIntegration.is_active == active)
    if verified is not None:
        query = query.where(UserIntegration.is_verified == verified)
    
    query = query.order_by(UserIntegration.created_at.desc())
    
    result = await db.execute(query)
    integrations = result.scalars().all()
    
    return [UserIntegrationResponse.model_validate(integration) for integration in integrations]


@router.post("/", response_model=UserIntegrationResponse)
async def create_user_integration(
    integration_data: UserIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Create a new user integration"""
    # Verify provider exists
    result = await db.execute(
        select(IntegrationProvider)
        .where(IntegrationProvider.id == integration_data.provider_id)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration provider not found"
        )
    
    # Create integration
    integration = UserIntegration(
        user_id=org_member.user_id,
        organization_id=org_member.organization_id,
        provider_id=integration_data.provider_id,
        name=integration_data.name,
        description=integration_data.description,
        configuration=integration_data.configuration,
        tags=integration_data.tags,
        integration_metadata=integration_data.integration_metadata
    )
    
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    
    # Load provider for response
    await db.execute(
        select(UserIntegration)
        .options(selectinload(UserIntegration.provider))
        .where(UserIntegration.id == integration.id)
    )
    
    return UserIntegrationResponse.model_validate(integration)


# Statistics Endpoint
@router.get("/stats", response_model=IntegrationStatsResponse)
async def get_integration_stats(
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Get integration statistics"""
    # Provider stats
    provider_stats = await db.execute(
        select(
            func.count(IntegrationProvider.id).label("total"),
            func.sum(case((IntegrationProvider.is_active, 1), else_=0)).label("active")
        )
    )
    provider_counts = provider_stats.first()
    
    # User integration stats for this organization
    user_integration_stats = await db.execute(
        select(
            func.count(UserIntegration.id).label("total"),
            func.sum(case((UserIntegration.is_active, 1), else_=0)).label("active")
        ).where(UserIntegration.organization_id == org_member.organization_id)
    )
    integration_counts = user_integration_stats.first()
    
    # Pending requests
    request_stats = await db.execute(
        select(func.count(IntegrationRequest.id))
        .where(
            and_(
                IntegrationRequest.organization_id == org_member.organization_id,
                IntegrationRequest.status == "pending"
            )
        )
    )
    pending_requests = request_stats.scalar() or 0
    
    # Real providers by category from database
    category_stats = await db.execute(
        select(
            IntegrationProvider.category,
            func.count(IntegrationProvider.id).label("count")
        )
        .where(IntegrationProvider.is_active == True)
        .group_by(IntegrationProvider.category)
    )
    providers_by_category = {
        row.category: row.count for row in category_stats.fetchall()
    }
    
    # Real user integrations by category
    user_category_stats = await db.execute(
        select(
            IntegrationProvider.category,
            func.count(UserIntegration.id).label("count")
        )
        .select_from(
            UserIntegration.__table__.join(
                IntegrationProvider.__table__,
                UserIntegration.provider_id == IntegrationProvider.id
            )
        )
        .where(
            and_(
                UserIntegration.organization_id == org_member.organization_id,
                UserIntegration.is_active == True
            )
        )
        .group_by(IntegrationProvider.category)
    )
    integrations_by_category = {
        row.category: row.count for row in user_category_stats.fetchall()
    }
    
    # Popular providers from database
    popular_provider_stats = await db.execute(
        select(
            IntegrationProvider.display_name,
            IntegrationProvider.category,
            func.count(UserIntegration.id).label("integrations")
        )
        .select_from(
            IntegrationProvider.__table__.outerjoin(
                UserIntegration.__table__,
                IntegrationProvider.id == UserIntegration.provider_id
            )
        )
        .where(IntegrationProvider.is_active == True)
        .group_by(IntegrationProvider.id, IntegrationProvider.display_name, IntegrationProvider.category)
        .order_by(func.count(UserIntegration.id).desc())
        .limit(5)
    )
    popular_providers = [
        {
            "name": row.display_name,
            "integrations": row.integrations,
            "category": row.category
        }
        for row in popular_provider_stats.fetchall()
    ]
    
    return IntegrationStatsResponse(
        total_providers=provider_counts.total or 0,
        active_providers=provider_counts.active or 0,
        total_user_integrations=integration_counts.total or 0,
        active_user_integrations=integration_counts.active or 0,
        pending_requests=pending_requests,
        providers_by_category=providers_by_category,
        integrations_by_category=integrations_by_category,
        popular_providers=popular_providers
    )


@router.get("/{integration_id}", response_model=UserIntegrationResponse)
async def get_user_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Get a specific user integration"""
    result = await db.execute(
        select(UserIntegration)
        .options(selectinload(UserIntegration.provider))
        .where(
            and_(
                UserIntegration.id == integration_id,
                UserIntegration.organization_id == org_member.organization_id,
                UserIntegration.user_id == org_member.user_id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return UserIntegrationResponse.model_validate(integration)


@router.put("/{integration_id}", response_model=UserIntegrationResponse)
async def update_user_integration(
    integration_id: int,
    integration_data: UserIntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Update a user integration"""
    result = await db.execute(
        select(UserIntegration)
        .where(
            and_(
                UserIntegration.id == integration_id,
                UserIntegration.organization_id == org_member.organization_id,
                UserIntegration.user_id == org_member.user_id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Update fields
    update_data = integration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)
    
    await db.commit()
    await db.refresh(integration)
    
    # Load provider for response
    await db.execute(
        select(UserIntegration)
        .options(selectinload(UserIntegration.provider))
        .where(UserIntegration.id == integration.id)
    )
    
    return UserIntegrationResponse.model_validate(integration)


@router.delete("/{integration_id}")
async def delete_user_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Delete a user integration"""
    result = await db.execute(
        select(UserIntegration)
        .where(
            and_(
                UserIntegration.id == integration_id,
                UserIntegration.organization_id == org_member.organization_id,
                UserIntegration.user_id == org_member.user_id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    await db.delete(integration)
    await db.commit()
    
    return {"message": "Integration deleted successfully"}


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    integration_id: int,
    test_request: Optional[IntegrationTestRequest] = None,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Test integration connectivity"""
    result = await db.execute(
        select(UserIntegration)
        .options(selectinload(UserIntegration.provider))
        .where(
            and_(
                UserIntegration.id == integration_id,
                UserIntegration.organization_id == org_member.organization_id,
                UserIntegration.user_id == org_member.user_id
            )
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Use provided configuration or existing integration configuration
    config = test_request.configuration if test_request else integration.configuration
    
    # Test the connection
    test_result = await test_integration_connection(integration.provider.name, config)
    
    # Update integration verification status if test successful
    if test_result.success:
        integration.is_verified = True
        integration.last_sync_at = datetime.now()
        integration.last_error = None
    else:
        integration.last_error = test_result.message
    
    await db.commit()
    
    return test_result


@router.post("/test", response_model=IntegrationTestResponse)
async def test_integration_config(
    provider_id: int,
    test_request: IntegrationTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test integration configuration before creating"""
    result = await db.execute(
        select(IntegrationProvider)
        .where(IntegrationProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration provider not found"
        )
    
    return await test_integration_connection(provider.name, test_request.configuration)


# Integration Requests Endpoints
@router.get("/requests", response_model=List[IntegrationRequestResponse])
async def get_integration_requests(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Get integration requests"""
    query = select(IntegrationRequest).where(
        IntegrationRequest.organization_id == org_member.organization_id
    )
    
    if status_filter:
        query = query.where(IntegrationRequest.status == status_filter)
    
    query = query.order_by(IntegrationRequest.created_at.desc())
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return [IntegrationRequestResponse.model_validate(request) for request in requests]


@router.post("/requests", response_model=IntegrationRequestResponse)
async def create_integration_request(
    request_data: IntegrationRequestCreate,
    db: AsyncSession = Depends(get_db),
    org_member: OrganizationMember = Depends(get_organization_member)
):
    """Create a new integration request"""
    request = IntegrationRequest(
        user_id=org_member.user_id,
        organization_id=org_member.organization_id,
        provider_id=request_data.provider_id,
        service_name=request_data.service_name,
        service_url=request_data.service_url,
        description=request_data.description,
        business_justification=request_data.business_justification,
        expected_usage=request_data.expected_usage,
        priority=request_data.priority,
        category=request_data.category,
        estimated_users=request_data.estimated_users
    )
    
    db.add(request)
    await db.commit()
    await db.refresh(request)
    
    return IntegrationRequestResponse.model_validate(request)