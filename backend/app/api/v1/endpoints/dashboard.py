"""
Dashboard endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get dashboard KPI statistics"""
    
    # Mock data for demo purposes
    return {
        "kpis": [
            {
                "title": "MTTR Delta",
                "value": "-34%",
                "description": "vs last month",
                "trend": "down",
                "color": "text-green-600",
                "details": "2.3 min avg resolution time"
            },
            {
                "title": "Auto-Resolved",
                "value": "94.7%",
                "description": "incidents handled automatically",
                "trend": "up",
                "color": "text-blue-600",
                "details": "847 of 894 total incidents"
            },
            {
                "title": "Rollback Rate",
                "value": "0.3%",
                "description": "of all deployments",
                "trend": "down",
                "color": "text-green-600",
                "details": "3 of 1,247 deployments"
            },
            {
                "title": "Error Budget Burn",
                "value": "12.4%",
                "description": "this month",
                "trend": "up",
                "color": "text-yellow-600",
                "details": "Well within SLO limits"
            },
            {
                "title": "Doc Coverage",
                "value": "89.2%",
                "description": "runbooks documented",
                "trend": "up",
                "color": "text-blue-600",
                "details": "156 of 175 procedures"
            },
            {
                "title": "Open Incidents",
                "value": "3",
                "description": "requiring attention",
                "trend": "stable",
                "color": "text-orange-600",
                "details": "2 low, 1 medium priority"
            }
        ],
        "system_status": {
            "status": "healthy",
            "message": "All Systems Operational",
            "uptime": "99.97%"
        }
    }


@router.get("/recent-actions")
async def get_recent_actions(
    current_user: User = Depends(get_current_active_user),
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get recent autonomous actions"""
    
    return [
        {
            "id": 1,
            "title": "Auto-scaled database cluster",
            "description": "CPU usage exceeded 80% threshold",
            "timestamp": "2 minutes ago",
            "status": "completed",
            "confidence": 96,
            "agent": "Database Guardian"
        },
        {
            "id": 2,
            "title": "Restarted payment service",
            "description": "Memory leak detected in payment-api-v2",
            "timestamp": "15 minutes ago",
            "status": "completed",
            "confidence": 91,
            "agent": "EC2 Auto-Healer"
        },
        {
            "id": 3,
            "title": "Applied rate limiting",
            "description": "Unusual traffic spike detected",
            "timestamp": "1 hour ago",
            "status": "completed",
            "confidence": 88,
            "agent": "Network Analyzer"
        },
        {
            "id": 4,
            "title": "Rollback deployment",
            "description": "Error rate increased after release",
            "timestamp": "3 hours ago",
            "status": "completed",
            "confidence": 94,
            "agent": "EC2 Auto-Healer"
        }
    ]


@router.get("/active-agents")
async def get_active_agents(
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Get active agents summary"""
    
    return [
        {
            "name": "EC2 Monitor",
            "type": "compute",
            "status": "active",
            "incidents": 12,
            "confidence": 94,
            "layer": "Infrastructure"
        },
        {
            "name": "Database Healer",
            "type": "database",
            "status": "active",
            "incidents": 8,
            "confidence": 91,
            "layer": "Data"
        },
        {
            "name": "Network Analyzer",
            "type": "network",
            "status": "active",
            "incidents": 15,
            "confidence": 89,
            "layer": "Network"
        },
        {
            "name": "Log Processor",
            "type": "monitoring",
            "status": "active",
            "incidents": 6,
            "confidence": 97,
            "layer": "Observability"
        }
    ]


@router.get("/agent-categories")
async def get_agent_categories(
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Get agent categories overview"""
    
    return [
        {
            "name": "Compute",
            "count": 8,
            "active": 7,
            "color": "text-blue-600"
        },
        {
            "name": "Database",
            "count": 5,
            "active": 5,
            "color": "text-green-600"
        },
        {
            "name": "Network",
            "count": 12,
            "active": 11,
            "color": "text-purple-600"
        },
        {
            "name": "Security",
            "count": 6,
            "active": 6,
            "color": "text-red-600"
        },
        {
            "name": "Monitoring",
            "count": 9,
            "active": 8,
            "color": "text-orange-600"
        }
    ]
