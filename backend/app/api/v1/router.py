"""
Main API v1 router that includes all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    organizations,
    agents,
    incidents,
    integrations,
    automations,
    billing,
    audit,
    dashboard,
    onboarding,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(automations.router, prefix="/automations", tags=["Automations"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
