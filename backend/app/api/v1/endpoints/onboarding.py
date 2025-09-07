"""
Onboarding endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.core.database import get_db

router = APIRouter()


class OnboardingCompanyData(BaseModel):
    """Company setup data"""
    organization_name: str = Field(..., min_length=2)
    domain: str = Field(None)
    description: str = Field(None)
    logo_url: str = Field(None)


class OnboardingIntegrationsData(BaseModel):
    """Integrations selection data"""
    selected_integrations: List[str] = Field(default_factory=list)


class OnboardingAgentsData(BaseModel):
    """Agents selection data"""
    selected_agents: List[str] = Field(default_factory=list)


class OnboardingPoliciesData(BaseModel):
    """Policies configuration data"""
    auto_approval_threshold: int = Field(80, ge=50, le=100)
    require_approval_for_high: bool = Field(True)
    require_approval_for_medium: bool = Field(False)
    enable_rollback: bool = Field(True)


class TeamMember(BaseModel):
    """Team member invitation"""
    email: str
    role: str = Field(..., pattern="^(viewer|member|admin)$")


class OnboardingTeamData(BaseModel):
    """Team setup data"""
    team_members: List[TeamMember] = Field(default_factory=list)


class OnboardingCompleteRequest(BaseModel):
    """Complete onboarding request"""
    company: OnboardingCompanyData
    integrations: OnboardingIntegrationsData
    agents: OnboardingAgentsData
    policies: OnboardingPoliciesData
    team: OnboardingTeamData


@router.get("/available-integrations")
async def get_available_integrations(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get available integrations for onboarding"""
    
    return {
        "integrations": [
            {
                "id": "aws",
                "name": "AWS",
                "category": "cloud",
                "description": "Amazon Web Services integration",
                "setup_time": "< 5min",
                "difficulty": "Easy"
            },
            {
                "id": "datadog",
                "name": "Datadog",
                "category": "monitoring",
                "description": "Full-stack monitoring platform",
                "setup_time": "< 10min",
                "difficulty": "Easy"
            },
            {
                "id": "pagerduty",
                "name": "PagerDuty",
                "category": "incident",
                "description": "Digital operations management",
                "setup_time": "< 15min",
                "difficulty": "Medium"
            },
            {
                "id": "github",
                "name": "GitHub",
                "category": "ci-cd",
                "description": "Development platform",
                "setup_time": "< 5min",
                "difficulty": "Easy"
            },
            {
                "id": "slack",
                "name": "Slack",
                "category": "communication",
                "description": "Team collaboration",
                "setup_time": "< 5min",
                "difficulty": "Easy"
            },
            {
                "id": "prometheus",
                "name": "Prometheus",
                "category": "monitoring",
                "description": "Metrics collection and alerting",
                "setup_time": "< 20min",
                "difficulty": "Medium"
            },
        ]
    }


@router.get("/available-agents")
async def get_available_agents(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get available agents for onboarding"""
    
    return {
        "agents": [
            {
                "id": "ec2-healer",
                "name": "EC2 Auto-Healer",
                "layer": "Infrastructure",
                "description": "Monitors EC2 instances and auto-resolves common issues",
                "recommended": True,
                "capabilities": ["restart", "scale", "replace", "optimize"],
                "supported_services": ["EC2", "Auto Scaling", "ELB"]
            },
            {
                "id": "database-guardian",
                "name": "Database Guardian",
                "layer": "Data",
                "description": "Maintains database health and performance optimization",
                "recommended": True,
                "capabilities": ["optimize", "backup", "scale", "monitor"],
                "supported_services": ["RDS", "Aurora", "DynamoDB"]
            },
            {
                "id": "network-analyzer",
                "name": "Network Analyzer",
                "layer": "Network",
                "description": "Analyzes traffic patterns and prevents network issues",
                "recommended": True,
                "capabilities": ["route", "throttle", "block", "monitor"],
                "supported_services": ["VPC", "CloudFront", "Route 53"]
            },
            {
                "id": "security-sentinel",
                "name": "Security Sentinel",
                "layer": "Security",
                "description": "Detects and responds to security threats automatically",
                "recommended": True,
                "capabilities": ["block", "isolate", "patch", "alert"],
                "supported_services": ["GuardDuty", "Security Hub", "WAF"]
            },
            {
                "id": "log-processor",
                "name": "Log Processor",
                "layer": "Observability",
                "description": "Processes logs and extracts actionable insights",
                "recommended": False,
                "capabilities": ["aggregate", "alert", "archive", "analyze"],
                "supported_services": ["CloudWatch", "ElasticSearch", "Splunk"]
            },
            {
                "id": "container-orchestrator",
                "name": "Container Orchestrator",
                "layer": "Container",
                "description": "Manages Kubernetes pods and container lifecycle",
                "recommended": False,
                "capabilities": ["scale", "restart", "migrate", "optimize"],
                "supported_services": ["EKS", "ECS", "Fargate"]
            },
            {
                "id": "api-guardian",
                "name": "API Guardian",
                "layer": "Application",
                "description": "Monitors API health and handles rate limiting",
                "recommended": False,
                "capabilities": ["throttle", "cache", "route", "monitor"],
                "supported_services": ["API Gateway", "ALB", "CloudFront"]
            },
            {
                "id": "storage-optimizer",
                "name": "Storage Optimizer",
                "layer": "Storage",
                "description": "Optimizes storage usage and prevents disk space issues",
                "recommended": False,
                "capabilities": ["cleanup", "archive", "optimize", "monitor"],
                "supported_services": ["S3", "EBS", "EFS"]
            },
            {
                "id": "cost-optimizer",
                "name": "Cost Optimizer",
                "layer": "Infrastructure",
                "description": "Monitors and optimizes cloud resource costs",
                "recommended": False,
                "capabilities": ["rightsizing", "scheduling", "purchasing", "reporting"],
                "supported_services": ["Cost Explorer", "Trusted Advisor", "Compute Optimizer"]
            },
            {
                "id": "backup-manager",
                "name": "Backup Manager",
                "layer": "Data",
                "description": "Ensures backups are running and validates recovery processes",
                "recommended": False,
                "capabilities": ["backup", "restore", "verify", "schedule"],
                "supported_services": ["AWS Backup", "S3", "Glacier"]
            }
        ]
    }


@router.post("/complete")
async def complete_onboarding(
    onboarding_data: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Complete the onboarding process"""
    
    # Check if user already has an organization
    existing_org = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    if existing_org.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User has already completed onboarding")
    
    # Create organization
    organization = Organization(
        name=onboarding_data.company.organization_name,
        slug=onboarding_data.company.organization_name.lower().replace(" ", "-").replace("_", "-"),
        description=onboarding_data.company.description,
        timezone="UTC",
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
    
    # For demo purposes, simulate some processing time
    import asyncio
    await asyncio.sleep(0.5)
    
    return {
        "success": True,
        "message": "Onboarding completed successfully",
        "organization": {
            "name": organization.name,
            "agents_count": len(onboarding_data.agents.selected_agents),
            "integrations_count": len(onboarding_data.integrations.selected_integrations),
            "team_size": len(onboarding_data.team.team_members) + 1  # +1 for current user
        },
        "next_steps": [
            "Your selected agents are being deployed",
            "Integration connections are being established", 
            "You can now access your dashboard"
        ]
    }


@router.get("/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get onboarding status for the current user"""
    
    # Check if user has any organization memberships
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    has_organization = result.scalar_one_or_none() is not None
    
    return {
        "completed": has_organization,
        "current_step": 4 if has_organization else 1,
        "steps": [
            {"id": 1, "title": "Company Setup", "completed": has_organization},
            {"id": 2, "title": "Connect Systems", "completed": has_organization},
            {"id": 3, "title": "Choose Agents", "completed": has_organization},
            {"id": 4, "title": "Set Policies", "completed": has_organization},
        ]
    }
