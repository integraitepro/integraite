"""
Agent management endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User, OrganizationMember
from app.core.database import get_db
import asyncio
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for deployed agents (in production, this would be in database)
deployed_agents = []


class DeployAgentRequest(BaseModel):
    """Agent deployment request schema"""
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=200)
    category: str = Field(..., pattern="^(compute|database|network|security|monitoring|application|container|storage)$")
    layer: str = Field(..., pattern="^(presentation|application|data|infrastructure)$")
    autoStart: bool = Field(default=True)
    alertThreshold: int = Field(default=85, ge=1, le=100)
    retryAttempts: int = Field(default=3, ge=1, le=10)
    monitoringInterval: int = Field(default=30, ge=1, le=300)
    capabilities: List[str] = Field(default=[])
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    tags: List[str] = Field(default=[])


class AgentStatusUpdate(BaseModel):
    """Agent status update request"""
    status: str = Field(..., pattern="^(active|inactive|paused)$")


@router.get("/")
async def list_agents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all agents for the current organization"""
    
    # Get user's current organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    org_member = result.scalar_one_or_none()
    if not org_member:
        return []
    
    # Combine default mock agents with deployed agents
    default_agents = [
        {
            "id": 1,
            "name": "EC2 Auto-Healer",
            "type": "compute",
            "status": "active",
            "description": "Monitors EC2 instances and auto-resolves common issues",
            "layer": "Infrastructure",
            "confidence": 94,
            "incidents": 23,
            "lastAction": "2 minutes ago",
            "actions": [
                {"type": "restart", "description": "Restarted unresponsive instance i-abc123", "time": "2 min ago"},
                {"type": "scale", "description": "Auto-scaled ASG due to CPU spike", "time": "15 min ago"},
                {"type": "replace", "description": "Replaced failed instance", "time": "1 hour ago"}
            ],
            "metrics": {"cpu": 45, "memory": 67, "network": 32}
        },
        {
            "id": 2,
            "name": "Database Guardian",
            "type": "database",
            "status": "active",
            "description": "Maintains database health and performance optimization",
            "layer": "Data",
            "confidence": 91,
            "incidents": 18,
            "lastAction": "5 minutes ago",
            "actions": [
                {"type": "optimize", "description": "Optimized slow query on orders table", "time": "5 min ago"},
                {"type": "cleanup", "description": "Cleaned up temporary tables", "time": "30 min ago"},
                {"type": "index", "description": "Added missing index on user_id", "time": "2 hours ago"}
            ],
            "metrics": {"connections": 156, "queries": 2341, "storage": 78}
        },
        {
            "id": 3,
            "name": "Network Analyzer",
            "type": "network",
            "status": "active",
            "description": "Analyzes traffic patterns and prevents network issues",
            "layer": "Network",
            "confidence": 89,
            "incidents": 31,
            "lastAction": "1 minute ago",
            "actions": [
                {"type": "throttle", "description": "Applied rate limiting to API endpoints", "time": "1 min ago"},
                {"type": "route", "description": "Rerouted traffic around failed node", "time": "10 min ago"},
                {"type": "block", "description": "Blocked suspicious IP ranges", "time": "45 min ago"}
            ],
            "metrics": {"bandwidth": 234, "latency": 12, "packets": 98567}
        }
    ]
    
    # Filter deployed agents for current organization
    org_deployed_agents = [agent for agent in deployed_agents if agent.get("organization_id") == org_member.organization_id]
    
    # Combine default agents with deployed agents
    all_agents = default_agents + org_deployed_agents
    
    return all_agents


@router.get("/{agent_id}")
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific agent details"""
    
    # Get user's current organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # TODO: Get actual agent from database
    return {
        "agent_id": agent_id, 
        "message": "Agent details",
        "organization_id": org_member.organization_id
    }


@router.post("/deploy")
async def deploy_agent(
    agent_data: DeployAgentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Deploy a new agent"""
    
    # Get user's current organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization to deploy agents"
        )
    
    # Simulate deployment process
    await asyncio.sleep(1)  # Simulate deployment time
    
    # Generate agent ID
    agent_id = f"agent-{str(uuid.uuid4())[:8]}"
    
    # Create agent object in the format expected by frontend
    new_agent = {
        "id": agent_id,
        "name": agent_data.name,
        "type": agent_data.category,
        "status": "deploying" if agent_data.autoStart else "inactive",
        "description": agent_data.description,
        "layer": agent_data.layer.title(),
        "confidence": 0,  # Will increase as agent starts learning
        "incidents": 0,
        "lastAction": "Just deployed",
        "actions": [
            {"type": "deploy", "description": f"Agent {agent_data.name} deployed successfully", "time": "just now"}
        ],
        "metrics": {"cpu": 0, "memory": 0, "network": 0},
        "organization_id": org_member.organization_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "config": {
            "alertThreshold": agent_data.alertThreshold,
            "retryAttempts": agent_data.retryAttempts,
            "autoStart": agent_data.autoStart,
            "capabilities": agent_data.capabilities,
            "priority": agent_data.priority,
            "tags": agent_data.tags,
            "monitoringInterval": agent_data.monitoringInterval
        }
    }
    
    # Store the agent in memory (in production, this would be saved to database)
    deployed_agents.append(new_agent)
    
    deployment_result = {
        "success": True,
        "message": "Agent deployed successfully",
        "agent": new_agent,
        "estimatedReadyTime": "2-5 minutes",
        "nextSteps": [
            "Agent is initializing and learning your environment",
            "Initial health checks are being performed",
            "You'll receive a notification when the agent is fully operational"
        ]
    }
    
    return deployment_result


@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status_update: AgentStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update agent status (start/stop/pause)"""
    
    # Get user's current organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # TODO: Update actual agent status in database
    # For now, simulate status update
    
    return {
        "success": True,
        "message": f"Agent {agent_id} status updated to {status_update.status}",
        "agentId": agent_id,
        "newStatus": status_update.status,
        "updatedAt": datetime.utcnow().isoformat()
    }


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Delete an agent"""
    
    # Get user's current organization
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .limit(1)
    )
    
    org_member = result.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # TODO: Remove actual agent from database
    # For now, simulate deletion
    
    return {
        "success": True,
        "message": f"Agent {agent_id} has been deleted",
        "agentId": agent_id,
        "deletedAt": datetime.utcnow().isoformat()
    }


@router.get("/templates/")
async def get_agent_templates(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get available agent templates"""
    
    templates = {
        "compute": [
            {
                "id": "ec2-healer",
                "name": "EC2 Auto-Healer",
                "description": "Monitors EC2 instances and automatically resolves common issues",
                "category": "compute",
                "layer": "infrastructure",
                "capabilities": ["Instance monitoring", "Auto-restart", "Health checks", "Resource optimization"],
                "estimatedSetupTime": "5 minutes",
                "complexity": "Easy"
            },
            {
                "id": "container-orchestrator",
                "name": "Container Orchestrator",
                "description": "Manages Kubernetes pods, handles scaling, and ensures container health",
                "category": "container",
                "layer": "infrastructure",
                "capabilities": ["Pod management", "Auto-scaling", "Health monitoring", "Resource allocation"],
                "estimatedSetupTime": "8 minutes",
                "complexity": "Medium"
            }
        ],
        "database": [
            {
                "id": "db-guardian",
                "name": "Database Guardian",
                "description": "Maintains database health, optimizes queries, and prevents performance degradation",
                "category": "database",
                "layer": "data",
                "capabilities": ["Query optimization", "Connection pooling", "Index management", "Backup monitoring"],
                "estimatedSetupTime": "7 minutes",
                "complexity": "Medium"
            }
        ],
        "security": [
            {
                "id": "security-sentinel",
                "name": "Security Sentinel",
                "description": "Detects security threats, blocks malicious activities, and ensures compliance",
                "category": "security",
                "layer": "infrastructure",
                "capabilities": ["Threat detection", "Intrusion prevention", "Vulnerability scanning", "Compliance monitoring"],
                "estimatedSetupTime": "12 minutes",
                "complexity": "Advanced"
            }
        ],
        "monitoring": [
            {
                "id": "performance-monitor",
                "name": "Performance Monitor",
                "description": "Tracks application performance metrics and automatically optimizes resource usage",
                "category": "monitoring",
                "layer": "application",
                "capabilities": ["Performance tracking", "Resource monitoring", "Alert management", "Trend analysis"],
                "estimatedSetupTime": "6 minutes",
                "complexity": "Easy"
            }
        ]
    }
    
    return templates