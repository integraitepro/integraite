
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import random
import json

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.models.agent import Agent, AgentExecution, AgentType, ExecutionStatus
from app.models.incident import (
    Incident, IncidentTimeline, IncidentHypothesis, 
    IncidentSeverity, IncidentStatus
)
from app.models.incident_extended import (
    InfrastructureComponent, VerificationGate, IncidentExecution, 
    PreExecutionCheck
)
from app.models.integration import (
    IntegrationProvider, IntegrationConfigurationField, UserIntegration,
    IntegrationCategory, IntegrationStatus, ConfigurationFieldType
)
from app.core.security import get_password_hash


async def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


async def seed_dummy_data(db: AsyncSession = None):
    """Seed the database with comprehensive dummy data"""
    print("🌱 Seeding database with dummy data...")
    
    if db is None:
        async with AsyncSessionLocal() as db:
            await _seed_data_with_session(db)
    else:
        await _seed_data_with_session(db)


async def _seed_data_with_session(db: AsyncSession):
    """Internal function to seed data with provided session"""
    # Check if data already exists
    result = await db.execute(select(User))
    if result.scalars().first():
        print("ℹ️  Database already contains data, skipping seeding")
        return
    
    # Create organizations
    print("📋 Creating organizations...")
    organizations = [
            Organization(
                name="TechCorp Solutions",
                slug="techcorp-solutions",
                domain="techcorp.com",
                logo_url="https://via.placeholder.com/100x100?text=TC",
                description="Leading technology solutions provider",
                timezone="America/New_York"
            ),
            Organization(
                name="Digital Innovations Inc",
                slug="digital-innovations-inc",
                domain="digitalinnovations.com", 
                logo_url="https://via.placeholder.com/100x100?text=DI",
                description="Cutting-edge digital transformation company",
                timezone="America/Los_Angeles"
            ),
            Organization(
                name="CloudFirst Enterprise",
                slug="cloudfirst-enterprise",
                domain="cloudfirst.com",
                logo_url="https://via.placeholder.com/100x100?text=CF",
                description="Cloud-native enterprise solutions",
                timezone="Europe/London"
            )
        ]
    
    for org in organizations:
        db.add(org)
    await db.commit()
    
    # Refresh to get IDs
    for org in organizations:
        await db.refresh(org)
    
    # Create users
    print("👤 Creating users...")
    users = [
        User(
                email="admin@techcorp.com",
                first_name="John",
                last_name="Doe", 
                hashed_password=get_password_hash("password123"),
                is_active=True,
            ),
            User(
                email="sarah.wilson@techcorp.com",
                first_name="Sarah",
                last_name="Wilson",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            ),
            User(
                email="mike.chen@digitalinnovations.com", 
                first_name="Mike",
                last_name="Chen",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            ),
            User(
                email="emily.rodriguez@cloudfirst.com",
                first_name="Emily",
                last_name="Rodriguez",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            ),
            User(
                email="david.kim@techcorp.com",
                first_name="David",
                last_name="Kim",
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
        ]
        
    for user in users:
        db.add(user)
    await db.commit()
    
    # Refresh to get IDs
    for user in users:
        await db.refresh(user)
    
    # Create organization memberships
    print("🏢 Creating organization memberships...")
    memberships = [
        # TechCorp Solutions
        OrganizationMember(
            created_by_id=users[0].id,
            organization_id=organizations[0].id,
            role=UserRole.ADMIN.value
        ),
        OrganizationMember(
            created_by_id=users[1].id,
            organization_id=organizations[0].id,
            role=UserRole.MEMBER.value
        ),
        OrganizationMember(
            user_id=users[4].id,
            organization_id=organizations[0].id,
            role=UserRole.MEMBER.value
        ),
        # Digital Innovations Inc
        OrganizationMember(
            user_id=users[2].id,
            organization_id=organizations[1].id,
            role=UserRole.ADMIN.value
        ),
        # CloudFirst Enterprise
        OrganizationMember(
            user_id=users[3].id,
            organization_id=organizations[2].id,
            role=UserRole.ADMIN.value
        )
    ]
    
    for membership in memberships:
        db.add(membership)
    await db.commit()
    
    # Create agents
    print("🤖 Creating agents...")
    agents = [
        # TechCorp Solutions agents
        Agent(
            name="EC2 Auto-Healer",
            description="Monitors and automatically heals EC2 instances",
            type=AgentType.COMPUTE.value,
            organization_id=organizations[0].id,
            config={
                "auto_restart": True,
                "health_check_interval": 60,
                "max_restart_attempts": 3,
                "notification_channels": ["slack", "email"]
            },
            is_active=True
        ),
        Agent(
            name="Database Performance Optimizer",
            description="Optimizes database queries and connection pools",
            type=AgentType.DATABASE.value,
            organization_id=organizations[0].id,
            config={
                "query_optimization": True,
                "connection_pool_size": 50,
                "slow_query_threshold": 1000,
                "index_recommendations": True
            },
            is_active=True
        ),
        Agent(
            name="Network Security Monitor",
            description="Monitors network traffic for security threats",
            type=AgentType.NETWORK.value,
            organization_id=organizations[0].id,
            config={
                "ddos_protection": True,
                "intrusion_detection": True,
                "traffic_analysis": True,
                "auto_block": False
            },
            is_active=True
        ),
        Agent(
            name="Application Response Monitor",
            description="Monitors application response times and errors",
            type=AgentType.API.value,
            organization_id=organizations[0].id,
            config={
                "response_time_threshold": 2000,
                "error_rate_threshold": 5,
                "auto_scaling": True,
                "circuit_breaker": True
            },
            is_active=True
        ),
        # Digital Innovations agents
        Agent(
            name="Kubernetes Pod Manager",
            description="Manages Kubernetes pod health and scaling",
            type=AgentType.COMPUTE.value,
            organization_id=organizations[1].id,
            config={
                "auto_scaling": True,
                "pod_restart": True,
                "resource_optimization": True,
                "namespace_monitoring": True
            },
            is_active=True
        ),
        Agent(
            name="API Gateway Monitor",
            description="Monitors API gateway performance and routing",
            type=AgentType.API.value,
            organization_id=organizations[1].id,
            config={
                "rate_limiting": True,
                "request_routing": True,
                "health_checks": True,
                "error_tracking": True
            },
            is_active=True
        )
    ]
    
    for agent in agents:
        db.add(agent)
    await db.commit()
    
    # Refresh to get IDs
    for agent in agents:
        await db.refresh(agent)
    
    # Create incidents
    print("🚨 Creating incidents...")
    incidents = [
        Incident(
            title="High CPU Usage on Production Servers",
            description="Multiple production servers showing sustained high CPU usage above 85%",
            severity=IncidentSeverity.HIGH.value,
            status=IncidentStatus.INVESTIGATING.value,
            organization_id=organizations[0].id,
            assigned_to_id=users[0].id,
            metadata={
                "affected_services": ["api-gateway", "user-service", "payment-service"],
                "affected_regions": ["us-east-1", "us-west-2"],
                "estimated_impact": "25% performance degradation"
            }
        ),
        Incident(
            title="Database Connection Pool Exhaustion",
            description="Application unable to acquire database connections, causing timeouts",
            severity=IncidentSeverity.CRITICAL.value,
            status=IncidentStatus.RESOLVING.value,
            organization_id=organizations[0].id,
            assigned_to_id=users[0].id,
            metadata={
                "affected_services": ["user-service", "auth-service"],
                "connection_pool_size": 20,
                "current_connections": 20,
                "wait_time": "30s"
            }
        ),
        Incident(
            title="Network Latency Spike in EU Region",
            description="Increased network latency affecting European users",
            severity=IncidentSeverity.MEDIUM.value,
            status=IncidentStatus.RESOLVED.value,
            organization_id=organizations[1].id,
            assigned_to_id=users[2].id,
            resolved_at=datetime.now() - timedelta(hours=2),
            metadata={
                "affected_region": "eu-west-1",
                "latency_increase": "150ms",
                "affected_users": 1250
            }
        ),
        Incident(
            title="SSL Certificate Expiration Warning",
            description="SSL certificates for multiple domains expiring within 7 days",
            severity=IncidentSeverity.LOW.value,
            status=IncidentStatus.OPEN.value,
            organization_id=organizations[2].id,
            assigned_to_id=users[3].id,
            metadata={
                "domains": ["api.cloudfirst.com", "app.cloudfirst.com", "admin.cloudfirst.com"],
                "expiry_dates": ["2024-01-08", "2024-01-10", "2024-01-12"],
                "auto_renewal": False
            }
        )
    ]
    
    for incident in incidents:
        db.add(incident)
    await db.commit()
    
    # Refresh to get IDs
    for incident in incidents:
        await db.refresh(incident)
    
    # Create incident timeline entries
    print("📅 Creating incident timeline...")
    timeline_entries = []
    
    # Timeline for first incident (High CPU)
    base_time = datetime.now() - timedelta(hours=4)
    timeline_entries.extend([
        IncidentTimeline(
            incident_id=incidents[0].id,
            created_by_id=users[1].id,
            action="incident_created",
            description="Incident reported due to high CPU alerts from monitoring",
            entry_metadata={"alert_source": "datadog", "threshold": "85%"},
            created_at=base_time
        ),
        IncidentTimeline(
            incident_id=incidents[0].id,
            created_by_id=users[0].id,
            action="status_change",
            description="Status changed to Investigating",
            entry_metadata={"from": "open", "to": "investigating"},
            created_at=base_time + timedelta(minutes=5)
        ),
        IncidentTimeline(
            incident_id=incidents[0].id,
            created_by_id=None,
            action="agent_action",
            description="EC2 Auto-Healer initiated performance analysis",
            entry_metadata={"agent": "EC2 Auto-Healer", "action": "performance_analysis"},
            created_at=base_time + timedelta(minutes=10)
        ),
        IncidentTimeline(
            incident_id=incidents[0].id,
            created_by_id=None,
            action="agent_action", 
            description="Identified memory leak in user-service causing CPU spike",
            entry_metadata={"agent": "Application Response Monitor", "finding": "memory_leak"},
            created_at=base_time + timedelta(minutes=30)
        )
    ])
    
    # Timeline for database incident
    base_time = datetime.now() - timedelta(hours=2)
    timeline_entries.extend([
        IncidentTimeline(
            incident_id=incidents[1].id,
            user_id=users[4].id,
            action="incident_created",
            description="Database connection timeouts reported by application monitoring",
            entry_metadata={"error_rate": "25%", "timeout_duration": "30s"},
            created_at=base_time
        ),
        IncidentTimeline(
            incident_id=incidents[1].id,
            created_by_id=None,
            action="agent_action",
            description="Database Performance Optimizer increased connection pool size to 50",
            entry_metadata={"agent": "Database Performance Optimizer", "action": "pool_resize", "from": 20, "to": 50},
            created_at=base_time + timedelta(minutes=15)
        )
    ])
    
    for entry in timeline_entries:
        db.add(entry)
    await db.commit()
    
    # Create incident hypotheses
    print("🔬 Creating incident hypotheses...")
    hypotheses = [
        IncidentHypothesis(
            incident_id=incidents[0].id,
            title="Memory leak in user-service",
            description="Recent deployment may have introduced a memory leak causing GC pressure and high CPU",
            confidence=85,
            status="investigating",
            evidence=json.dumps([
                "Memory usage trending upward since last deployment",
                "GC frequency increased by 300%",
                "CPU spikes correlate with memory allocation patterns"
            ]),
            created_by=users[0].id
        ),
        IncidentHypothesis(
            incident_id=incidents[0].id,
            title="Database query inefficiency",
            description="New feature may be causing inefficient database queries",
            confidence=60,
            status="pending",
            evidence=json.dumps([
                "Slow query log shows 15% increase in query time",
                "New user analytics feature deployed yesterday"
            ]),
            created_by=users[1].id
        ),
        IncidentHypothesis(
            incident_id=incidents[1].id,
            title="Connection pool too small",
            description="Current connection pool size insufficient for peak load",
            confidence=90,
            status="confirmed",
            evidence=json.dumps([
                "Pool exhaustion coincides with traffic spike",
                "Connection wait time exceeds timeout threshold",
                "No connection leaks detected"
            ]),
            created_by=users[0].id
        )
    ]
    
    for hypothesis in hypotheses:
        db.add(hypothesis)
    await db.commit()
    
    # Create agent executions
    print("⚡ Creating agent executions...")
    executions = [
        # EC2 Auto-Healer executions
        AgentExecution(
            agent_id=agents[0].id,
            incident_id=incidents[0].id,
            agent_external_id="agent-ec2-auto-healer",
            agent_name="EC2 Auto-Healer",
            agent_type="Infrastructure",
            role="Lead Investigator",
            status="in_progress",
            current_action="Analyzing memory usage patterns across affected instances",
            progress=75.0,
            confidence=85.0,
            action_type="analysis",
            description="Investigating high CPU usage on production servers",
            trigger_reason="High CPU alert triggered automatic investigation",
            confidence_score=85.0,
            findings=json.dumps([
                "Memory usage increased 40% since last deployment",
                "GC frequency up 300% on user-service instances",
                "CPU spikes correlate with memory allocation patterns"
            ]),
            recommendations=json.dumps([
                "Restart user-service instances to clear memory leak",
                "Scale out additional instances to distribute load",
                "Rollback to previous deployment if pattern continues"
            ]),
            started_at=datetime.now() - timedelta(hours=3, minutes=50),
            created_at=datetime.now() - timedelta(hours=3, minutes=50)
        ),
        AgentExecution(
            agent_id=agents[1].id,
            incident_id=incidents[1].id,
            agent_external_id="agent-database-performance-optimizer",
            agent_name="Database Performance Optimizer", 
            agent_type="Database",
            role="Lead Investigator",
            status="completed",
            current_action="Connection pool optimization completed",
            progress=100.0,
            confidence=95.0,
            action_type="optimization",
            description="Resolved database connection pool exhaustion",
            trigger_reason="Database connection timeout alerts",
            confidence_score=95.0,
            success=True,
            findings=json.dumps([
                "Connection pool size was insufficient for peak load",
                "No connection leaks detected",
                "Average connection hold time within normal range"
            ]),
            recommendations=json.dumps([
                "Increase base connection pool size to 50",
                "Implement dynamic scaling for connection pool",
                "Add connection pool monitoring dashboards"
            ]),
            started_at=datetime.now() - timedelta(hours=1, minutes=45),
            completed_at=datetime.now() - timedelta(hours=1, minutes=30),
            duration_seconds=900,
            created_at=datetime.now() - timedelta(hours=1, minutes=45)
        ),
        AgentExecution(
            agent_id=agents[3].id,
            incident_id=incidents[0].id,
            agent_external_id="agent-application-response-monitor",
            agent_name="Application Response Monitor",
            agent_type="Application",
            role="Supporting Analyst",
            status="in_progress",
            current_action="Monitoring application response times and error rates",
            progress=60.0,
            confidence=80.0,
            action_type="monitoring",
            description="Tracking application performance during incident",
            trigger_reason="Incident escalation for application monitoring",
            confidence_score=80.0,
            findings=json.dumps([
                "Response times increased 25% on affected services",
                "Error rate elevated to 3.2% (normal: 0.5%)",
                "Memory leak pattern confirmed in user-service"
            ]),
            recommendations=json.dumps([
                "Implement circuit breaker for user-service",
                "Scale out user-service replicas",
                "Enable memory profiling for debugging"
            ]),
            started_at=datetime.now() - timedelta(hours=3, minutes=20),
            created_at=datetime.now() - timedelta(hours=3, minutes=20)
        )
    ]
    
    for execution in executions:
        db.add(execution)
    await db.commit()
    
    # Create infrastructure components
    print("🏗️ Creating infrastructure components...")
    infra_components = [
        InfrastructureComponent(
            incident_id=incidents[0].id,
            name="api-prod-01",
            component_type="EC2 Instance",
            status="degraded",
            health_score=65.0,
            metadata_=json.dumps({
                "instance_type": "m5.2xlarge",
                "availability_zone": "us-east-1a",
                "cpu_utilization": "87%",
                "memory_utilization": "92%",
                "network_io": "high"
            })
        ),
        InfrastructureComponent(
            incident_id=incidents[0].id,
            name="api-prod-02",
            component_type="EC2 Instance", 
            status="degraded",
            health_score=70.0,
            metadata_=json.dumps({
                "instance_type": "m5.2xlarge",
                "availability_zone": "us-east-1b",
                "cpu_utilization": "83%",
                "memory_utilization": "89%",
                "network_io": "normal"
            })
        ),
        InfrastructureComponent(
            incident_id=incidents[1].id,
            name="postgres-primary",
            component_type="RDS Instance",
            status="critical",
            health_score=45.0,
            metadata_=json.dumps({
                "instance_class": "db.r5.2xlarge",
                "engine": "PostgreSQL 14.9",
                "connection_count": "50/50",
                "cpu_utilization": "45%",
                "freeable_memory": "2.1 GB"
            })
        )
    ]
    
    for component in infra_components:
        db.add(component)
    await db.commit()
    
    # Create verification gates
    print("✅ Creating verification gates...")
    verification_gates = [
        VerificationGate(
            incident_id=incidents[0].id,
            name="CPU Usage Normalization",
            description="Verify CPU usage returns to normal levels (<70%)",
            gate_type="metric_threshold",
            status="pending",
            criteria=json.dumps({
                "metric": "cpu_utilization",
                "threshold": 70,
                "operator": "less_than",
                "duration": "5m"
            })
        ),
        VerificationGate(
            incident_id=incidents[0].id,
            name="Memory Leak Resolution",
            description="Confirm memory usage stabilizes after restart",
            gate_type="trend_analysis",
            status="pending", 
            criteria=json.dumps({
                "metric": "memory_utilization",
                "trend": "stable",
                "duration": "15m",
                "tolerance": "5%"
            })
        ),
        VerificationGate(
            incident_id=incidents[1].id,
            name="Database Connection Health",
            description="Verify database connections are stable and available",
            gate_type="health_check",
            status="passed",
            criteria=json.dumps({
                "metric": "connection_pool_utilization",
                "threshold": 80,
                "operator": "less_than"
            }),
            verified_at=datetime.now() - timedelta(minutes=30)
        )
    ]
    
    for gate in verification_gates:
        db.add(gate)
    await db.commit()
    
    # Create incident executions
    print("🔄 Creating incident executions...")
    incident_executions = [
        IncidentExecution(
            incident_id=incidents[0].id,
            execution_type="investigation",
            title="Memory Usage Analysis",
            description="Comprehensive analysis of memory patterns to identify leak source",
            status="in_progress",
            progress=75.0,
            execution_data=json.dumps({
                "analysis_type": "memory_profiling",
                "tools": ["jvm_profiler", "memory_analyzer"],
                "findings": ["heap_dump_analysis", "gc_log_review"],
                "next_steps": ["code_review", "deployment_analysis"]
            })
        ),
        IncidentExecution(
            incident_id=incidents[1].id,
            execution_type="mitigation",
            title="Database Connection Pool Scaling",
            description="Increase connection pool size and implement monitoring",
            status="completed",
            progress=100.0,
            completed_at=datetime.now() - timedelta(minutes=30),
            execution_data=json.dumps({
                "action": "connection_pool_resize",
                "old_size": 20,
                "new_size": 50,
                "monitoring_added": True,
                "performance_impact": "positive"
            })
        )
    ]
    
    for execution in incident_executions:
        db.add(execution)
    await db.commit()
    
    print("✅ Database seeded successfully with comprehensive dummy data!")
    print(f"   📊 Created {len(organizations)} organizations")
    print(f"   👥 Created {len(users)} users")
    print(f"   🤖 Created {len(agents)} agents")
    print(f"   🚨 Created {len(incidents)} incidents")
    print(f"   📅 Created {len(timeline_entries)} timeline entries")
    print(f"   🔬 Created {len(hypotheses)} hypotheses")
    print(f"   ⚡ Created {len(executions)} agent executions")
    print(f"   🏗️ Created {len(infra_components)} infrastructure components")
    print(f"   ✅ Created {len(verification_gates)} verification gates")
    print(f"   🔄 Created {len(incident_executions)} incident executions")


async def seed_integration_providers(db: AsyncSession):
    """Seed integration providers and their configuration fields"""
    print("🔗 Seeding integration providers...")
    
    # Check if providers already exist
    result = await db.execute(select(IntegrationProvider).limit(1))
    if result.scalar_one_or_none():
        print("Integration providers already exist, clearing and re-seeding with new providers...")
        # Clear existing providers and their fields
        await db.execute(delete(IntegrationConfigurationField))
        await db.execute(delete(IntegrationProvider))
        await db.commit()
    
    # Define integration providers with their configuration fields
    providers_data = [
        # Cloud Infrastructure
        {
            "provider": {
                "name": "aws",
                "display_name": "Amazon Web Services",
                "description": "Connect to AWS for cloud infrastructure monitoring and management",
                "category": IntegrationCategory.CLOUD_INFRASTRUCTURE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/amazonaws.svg",
                "brand_color": "#FF9900",
                "documentation_url": "https://docs.aws.amazon.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/aws",
                "tags": ["cloud", "infrastructure", "monitoring", "compute", "storage"],
                "supported_features": ["resource_monitoring", "cost_tracking", "alerts", "automation"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "access_key_id",
                    "display_label": "Access Key ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Your AWS Access Key ID",
                    "placeholder": "AKIAIOSFODNN7EXAMPLE",
                    "is_required": True,
                    "is_sensitive": False,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "secret_access_key",
                    "display_label": "Secret Access Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Your AWS Secret Access Key",
                    "placeholder": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "region",
                    "display_label": "Default Region",
                    "field_type": ConfigurationFieldType.SELECT.value,
                    "description": "Default AWS region for operations",
                    "is_required": True,
                    "field_options": [
                        {"value": "us-east-1", "label": "US East (N. Virginia)"},
                        {"value": "us-west-2", "label": "US West (Oregon)"},
                        {"value": "eu-west-1", "label": "Europe (Ireland)"},
                        {"value": "ap-southeast-1", "label": "Asia Pacific (Singapore)"}
                    ],
                    "default_value": "us-east-1",
                    "sort_order": 3,
                    "field_group": "configuration"
                }
            ]
        },
        {
            "provider": {
                "name": "azure",
                "display_name": "Microsoft Azure",
                "description": "Connect to Azure for cloud infrastructure and application monitoring",
                "category": IntegrationCategory.CLOUD_INFRASTRUCTURE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/microsoftazure.svg",
                "brand_color": "#0078D4",
                "documentation_url": "https://docs.microsoft.com/azure/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/azure",
                "tags": ["cloud", "infrastructure", "monitoring", "microsoft"],
                "supported_features": ["resource_monitoring", "cost_tracking", "alerts", "automation"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "tenant_id",
                    "display_label": "Tenant ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Your Azure Active Directory Tenant ID",
                    "placeholder": "12345678-1234-1234-1234-123456789012",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "client_id",
                    "display_label": "Client ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Application (Client) ID from Azure App Registration",
                    "placeholder": "87654321-4321-4321-4321-210987654321",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "client_secret",
                    "display_label": "Client Secret",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Client Secret from Azure App Registration",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        {
            "provider": {
                "name": "servicenow",
                "display_name": "ServiceNow",
                "description": "Connect to ServiceNow for incident and change management",
                "category": IntegrationCategory.INCIDENT_MANAGEMENT.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/servicenow.svg",
                "brand_color": "#62D84E",
                "documentation_url": "https://docs.servicenow.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/servicenow",
                "tags": ["itsm", "incident", "change", "workflow"],
                "supported_features": ["incident_sync", "change_management", "alerts", "workflows"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "instance_url",
                    "display_label": "Instance URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Your ServiceNow instance URL",
                    "placeholder": "https://yourcompany.service-now.com",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "ServiceNow username",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "password",
                    "display_label": "Password",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "ServiceNow password",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        {
            "provider": {
                "name": "slack",
                "display_name": "Slack",
                "description": "Connect to Slack for notifications and team communication",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/slack.svg",
                "brand_color": "#4A154B",
                "documentation_url": "https://api.slack.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/slack",
                "tags": ["communication", "notifications", "collaboration"],
                "supported_features": ["notifications", "interactive_messages", "workflows"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "bot_token",
                    "display_label": "Bot User OAuth Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Slack Bot User OAuth Token (starts with xoxb-)",
                    "placeholder": "xoxb-your-slack-bot-token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                }
            ]
        },
        # Google Cloud Platform
        {
            "provider": {
                "name": "gcp",
                "display_name": "Google Cloud Platform",
                "description": "Connect to GCP for cloud infrastructure monitoring and management",
                "category": IntegrationCategory.CLOUD_INFRASTRUCTURE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googlecloud.svg",
                "brand_color": "#4285F4",
                "documentation_url": "https://cloud.google.com/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/gcp",
                "tags": ["cloud", "infrastructure", "monitoring", "google"],
                "supported_features": ["resource_monitoring", "cost_tracking", "alerts", "automation"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "project_id",
                    "display_label": "Project ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Your GCP Project ID",
                    "placeholder": "my-project-12345",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "service_account_key",
                    "display_label": "Service Account Key",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "JSON key for service account",
                    "placeholder": "{\n  \"type\": \"service_account\",\n  \"project_id\": \"...\"\n}",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Datadog
        {
            "provider": {
                "name": "datadog",
                "display_name": "Datadog",
                "description": "Connect to Datadog for infrastructure and application monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/datadog.svg",
                "brand_color": "#632CA6",
                "documentation_url": "https://docs.datadoghq.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/datadog",
                "tags": ["monitoring", "metrics", "logs", "apm"],
                "supported_features": ["metrics_collection", "log_aggregation", "alerts", "dashboards"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Datadog API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "app_key",
                    "display_label": "Application Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Datadog Application Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # New Relic
        {
            "provider": {
                "name": "newrelic",
                "display_name": "New Relic",
                "description": "Connect to New Relic for application performance monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/newrelic.svg",
                "brand_color": "#008C99",
                "documentation_url": "https://docs.newrelic.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/newrelic",
                "tags": ["monitoring", "apm", "performance", "alerts"],
                "supported_features": ["apm", "infrastructure_monitoring", "alerts", "dashboards"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "New Relic API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "account_id",
                    "display_label": "Account ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "New Relic Account ID",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Grafana
        {
            "provider": {
                "name": "grafana",
                "display_name": "Grafana",
                "description": "Connect to Grafana for visualization and monitoring dashboards",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/grafana.svg",
                "brand_color": "#F46800",
                "documentation_url": "https://grafana.com/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/grafana",
                "tags": ["visualization", "monitoring", "dashboards", "metrics"],
                "supported_features": ["dashboard_sync", "alerts", "metrics_collection"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "url",
                    "display_label": "Grafana URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Your Grafana instance URL",
                    "placeholder": "https://your-org.grafana.net",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Grafana API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Prometheus
        {
            "provider": {
                "name": "prometheus",
                "display_name": "Prometheus",
                "description": "Connect to Prometheus for metrics collection and monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/prometheus.svg",
                "brand_color": "#E6522C",
                "documentation_url": "https://prometheus.io/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/prometheus",
                "tags": ["metrics", "monitoring", "time-series", "alerts"],
                "supported_features": ["metrics_collection", "alerts", "time_series"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "endpoint_url",
                    "display_label": "Prometheus Endpoint",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Prometheus server endpoint URL",
                    "placeholder": "http://prometheus:9090",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Basic auth username (if required)",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # GitHub
        {
            "provider": {
                "name": "github",
                "display_name": "GitHub",
                "description": "Connect to GitHub for repository and workflow monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg",
                "brand_color": "#181717",
                "documentation_url": "https://docs.github.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/github",
                "tags": ["git", "repository", "ci/cd", "workflows"],
                "supported_features": ["repository_monitoring", "workflow_tracking", "issue_sync"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "access_token",
                    "display_label": "Personal Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "GitHub Personal Access Token",
                    "placeholder": "ghp_xxxxxxxxxxxxxxxxxxxx",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "organization",
                    "display_label": "Organization",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "GitHub organization name (optional)",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # GitLab
        {
            "provider": {
                "name": "gitlab",
                "display_name": "GitLab",
                "description": "Connect to GitLab for repository and CI/CD monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/gitlab.svg",
                "brand_color": "#FC6D26",
                "documentation_url": "https://docs.gitlab.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/gitlab",
                "tags": ["git", "repository", "ci/cd", "pipelines"],
                "supported_features": ["repository_monitoring", "pipeline_tracking", "issue_sync"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "access_token",
                    "display_label": "Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "GitLab Personal Access Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "base_url",
                    "display_label": "GitLab URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "GitLab instance URL",
                    "default_value": "https://gitlab.com",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                }
            ]
        },
        # Jenkins
        {
            "provider": {
                "name": "jenkins",
                "display_name": "Jenkins",
                "description": "Connect to Jenkins for CI/CD pipeline monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/jenkins.svg",
                "brand_color": "#D33833",
                "documentation_url": "https://www.jenkins.io/doc/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/jenkins",
                "tags": ["ci/cd", "automation", "builds", "pipelines"],
                "supported_features": ["build_monitoring", "pipeline_tracking", "job_alerts"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "base_url",
                    "display_label": "Jenkins URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Your Jenkins instance URL",
                    "placeholder": "https://jenkins.company.com",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Jenkins username",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Jenkins API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        # Docker Hub
        {
            "provider": {
                "name": "dockerhub",
                "display_name": "Docker Hub",
                "description": "Connect to Docker Hub for container registry monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/docker.svg",
                "brand_color": "#2496ED",
                "documentation_url": "https://docs.docker.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/docker",
                "tags": ["containers", "registry", "docker", "images"],
                "supported_features": ["image_monitoring", "vulnerability_scanning", "webhooks"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Docker Hub username",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "access_token",
                    "display_label": "Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Docker Hub Access Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Kubernetes
        {
            "provider": {
                "name": "kubernetes",
                "display_name": "Kubernetes",
                "description": "Connect to Kubernetes for cluster monitoring and management",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/kubernetes.svg",
                "brand_color": "#326CE5",
                "documentation_url": "https://kubernetes.io/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/kubernetes",
                "tags": ["orchestration", "containers", "cluster", "monitoring"],
                "supported_features": ["cluster_monitoring", "pod_management", "resource_tracking"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "kubeconfig",
                    "display_label": "Kubeconfig",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Kubernetes configuration file content",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "namespace",
                    "display_label": "Default Namespace",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Default namespace to monitor",
                    "default_value": "default",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Terraform
        {
            "provider": {
                "name": "terraform",
                "display_name": "Terraform Cloud",
                "description": "Connect to Terraform Cloud for infrastructure as code monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/terraform.svg",
                "brand_color": "#7B42BC",
                "documentation_url": "https://www.terraform.io/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/terraform",
                "tags": ["iac", "infrastructure", "automation", "provisioning"],
                "supported_features": ["plan_monitoring", "state_tracking", "run_alerts"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Terraform Cloud API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "organization",
                    "display_label": "Organization",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Terraform Cloud organization name",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Jira
        {
            "provider": {
                "name": "jira",
                "display_name": "Jira",
                "description": "Connect to Jira for issue tracking and project management",
                "category": IntegrationCategory.INCIDENT_MANAGEMENT.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/jira.svg",
                "brand_color": "#0052CC",
                "documentation_url": "https://support.atlassian.com/jira/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/jira",
                "tags": ["issue tracking", "project management", "agile", "tickets"],
                "supported_features": ["issue_sync", "project_tracking", "workflow_automation"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "base_url",
                    "display_label": "Jira URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Your Jira instance URL",
                    "placeholder": "https://yourcompany.atlassian.net",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "email",
                    "display_label": "Email",
                    "field_type": ConfigurationFieldType.EMAIL.value,
                    "description": "Your Jira account email",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Jira API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        # Confluence
        {
            "provider": {
                "name": "confluence",
                "display_name": "Confluence",
                "description": "Connect to Confluence for documentation and knowledge management",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/confluence.svg",
                "brand_color": "#172B4D",
                "documentation_url": "https://support.atlassian.com/confluence/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/confluence",
                "tags": ["documentation", "knowledge base", "collaboration", "wiki"],
                "supported_features": ["content_sync", "search", "page_monitoring"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "base_url",
                    "display_label": "Confluence URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Your Confluence instance URL",
                    "placeholder": "https://yourcompany.atlassian.net/wiki",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Confluence API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Microsoft Teams
        {
            "provider": {
                "name": "teams",
                "display_name": "Microsoft Teams",
                "description": "Connect to Microsoft Teams for collaboration and notifications",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/microsoftteams.svg",
                "brand_color": "#6264A7",
                "documentation_url": "https://docs.microsoft.com/en-us/microsoftteams/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/teams",
                "tags": ["communication", "notifications", "collaboration", "chat"],
                "supported_features": ["notifications", "interactive_messages", "bot_integration"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "webhook_url",
                    "display_label": "Webhook URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Teams channel webhook URL",
                    "placeholder": "https://outlook.office.com/webhook/...",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                }
            ]
        },
        # Discord
        {
            "provider": {
                "name": "discord",
                "display_name": "Discord",
                "description": "Connect to Discord for team communication and notifications",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/discord.svg",
                "brand_color": "#5865F2",
                "documentation_url": "https://discord.com/developers/docs",
                "setup_guide_url": "https://docs.integraite.pro/integrations/discord",
                "tags": ["communication", "notifications", "chat", "gaming"],
                "supported_features": ["notifications", "bot_commands", "webhooks"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "webhook_url",
                    "display_label": "Webhook URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Discord channel webhook URL",
                    "placeholder": "https://discord.com/api/webhooks/...",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                }
            ]
        },
        # PagerDuty
        {
            "provider": {
                "name": "pagerduty",
                "display_name": "PagerDuty",
                "description": "Connect to PagerDuty for incident management and alerting",
                "category": IntegrationCategory.INCIDENT_MANAGEMENT.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/pagerduty.svg",
                "brand_color": "#06AC38",
                "documentation_url": "https://developer.pagerduty.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/pagerduty",
                "tags": ["incident management", "alerting", "on-call", "escalation"],
                "supported_features": ["incident_sync", "alert_routing", "escalation_policies"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "PagerDuty API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "service_key",
                    "display_label": "Service Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "PagerDuty Service Integration Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Opsgenie
        {
            "provider": {
                "name": "opsgenie",
                "display_name": "Opsgenie",
                "description": "Connect to Opsgenie for incident management and alerting",
                "category": IntegrationCategory.INCIDENT_MANAGEMENT.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/opsgenie.svg",
                "brand_color": "#172B4D",
                "documentation_url": "https://docs.opsgenie.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/opsgenie",
                "tags": ["incident management", "alerting", "on-call", "atlassian"],
                "supported_features": ["alert_management", "incident_tracking", "escalation"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Opsgenie API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "eu_instance",
                    "display_label": "EU Instance",
                    "field_type": ConfigurationFieldType.BOOLEAN.value,
                    "description": "Use EU instance (api.eu.opsgenie.com)",
                    "default_value": "false",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Splunk
        {
            "provider": {
                "name": "splunk",
                "display_name": "Splunk",
                "description": "Connect to Splunk for log analysis and security monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/splunk.svg",
                "brand_color": "#000000",
                "documentation_url": "https://docs.splunk.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/splunk",
                "tags": ["logging", "security", "analysis", "siem"],
                "supported_features": ["log_analysis", "search", "alerts", "dashboards"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "host",
                    "display_label": "Splunk Host",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Splunk server hostname or IP",
                    "placeholder": "splunk.company.com",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "port",
                    "display_label": "Port",
                    "field_type": ConfigurationFieldType.NUMBER.value,
                    "description": "Splunk management port",
                    "default_value": "8089",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Splunk username",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                },
                {
                    "field_name": "password",
                    "display_label": "Password",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Splunk password",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 4,
                    "field_group": "credentials"
                }
            ]
        },
        # Elasticsearch
        {
            "provider": {
                "name": "elasticsearch",
                "display_name": "Elasticsearch",
                "description": "Connect to Elasticsearch for search and log analysis",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/elasticsearch.svg",
                "brand_color": "#005571",
                "documentation_url": "https://www.elastic.co/guide/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/elasticsearch",
                "tags": ["search", "logging", "analytics", "elk"],
                "supported_features": ["log_search", "analytics", "monitoring"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "host",
                    "display_label": "Elasticsearch Host",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Elasticsearch cluster endpoint",
                    "placeholder": "elasticsearch.company.com",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "port",
                    "display_label": "Port",
                    "field_type": ConfigurationFieldType.NUMBER.value,
                    "description": "Elasticsearch port",
                    "default_value": "9200",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Elasticsearch username (if auth enabled)",
                    "is_required": False,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        # PostgreSQL
        {
            "provider": {
                "name": "postgresql",
                "display_name": "PostgreSQL",
                "description": "Connect to PostgreSQL database for monitoring and management",
                "category": IntegrationCategory.DATABASE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/postgresql.svg",
                "brand_color": "#336791",
                "documentation_url": "https://www.postgresql.org/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/postgresql",
                "tags": ["database", "sql", "relational", "postgres"],
                "supported_features": ["performance_monitoring", "query_analysis", "health_checks"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "host",
                    "display_label": "Host",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "PostgreSQL server hostname",
                    "placeholder": "localhost",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "port",
                    "display_label": "Port",
                    "field_type": ConfigurationFieldType.NUMBER.value,
                    "description": "PostgreSQL port",
                    "default_value": "5432",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                },
                {
                    "field_name": "database",
                    "display_label": "Database",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Database name",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Database username",
                    "is_required": True,
                    "sort_order": 4,
                    "field_group": "credentials"
                },
                {
                    "field_name": "password",
                    "display_label": "Password",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Database password",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 5,
                    "field_group": "credentials"
                }
            ]
        },
        # MySQL
        {
            "provider": {
                "name": "mysql",
                "display_name": "MySQL",
                "description": "Connect to MySQL database for monitoring and management",
                "category": IntegrationCategory.DATABASE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/mysql.svg",
                "brand_color": "#4479A1",
                "documentation_url": "https://dev.mysql.com/doc/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/mysql",
                "tags": ["database", "sql", "relational", "mysql"],
                "supported_features": ["performance_monitoring", "query_analysis", "replication_monitoring"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "host",
                    "display_label": "Host",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "MySQL server hostname",
                    "placeholder": "localhost",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "port",
                    "display_label": "Port",
                    "field_type": ConfigurationFieldType.NUMBER.value,
                    "description": "MySQL port",
                    "default_value": "3306",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                },
                {
                    "field_name": "database",
                    "display_label": "Database",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Database name",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Database username",
                    "is_required": True,
                    "sort_order": 4,
                    "field_group": "credentials"
                },
                {
                    "field_name": "password",
                    "display_label": "Password",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Database password",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 5,
                    "field_group": "credentials"
                }
            ]
        },
        # MongoDB
        {
            "provider": {
                "name": "mongodb",
                "display_name": "MongoDB",
                "description": "Connect to MongoDB for NoSQL database monitoring",
                "category": IntegrationCategory.DATABASE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/mongodb.svg",
                "brand_color": "#47A248",
                "documentation_url": "https://docs.mongodb.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/mongodb",
                "tags": ["database", "nosql", "document", "mongodb"],
                "supported_features": ["performance_monitoring", "replica_set_monitoring", "sharding_analytics"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "connection_string",
                    "display_label": "Connection String",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "MongoDB connection string",
                    "placeholder": "mongodb://localhost:27017/mydb",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "database",
                    "display_label": "Database",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Database name to monitor",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                }
            ]
        },
        # Redis
        {
            "provider": {
                "name": "redis",
                "display_name": "Redis",
                "description": "Connect to Redis for cache and data structure monitoring",
                "category": IntegrationCategory.DATABASE.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/redis.svg",
                "brand_color": "#DC382D",
                "documentation_url": "https://redis.io/documentation",
                "setup_guide_url": "https://docs.integraite.pro/integrations/redis",
                "tags": ["cache", "in-memory", "key-value", "redis"],
                "supported_features": ["performance_monitoring", "memory_analysis", "slowlog_tracking"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "host",
                    "display_label": "Host",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Redis server hostname",
                    "placeholder": "localhost",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "port",
                    "display_label": "Port",
                    "field_type": ConfigurationFieldType.NUMBER.value,
                    "description": "Redis port",
                    "default_value": "6379",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "connection"
                },
                {
                    "field_name": "password",
                    "display_label": "Password",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Redis password (if auth enabled)",
                    "is_required": False,
                    "is_sensitive": True,
                    "sort_order": 3,
                    "field_group": "credentials"
                }
            ]
        },
        # Nginx
        {
            "provider": {
                "name": "nginx",
                "display_name": "Nginx",
                "description": "Connect to Nginx for web server monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/nginx.svg",
                "brand_color": "#009639",
                "documentation_url": "https://nginx.org/en/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/nginx",
                "tags": ["web server", "proxy", "load balancer", "http"],
                "supported_features": ["request_monitoring", "performance_tracking", "error_analysis"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "status_url",
                    "display_label": "Status URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Nginx status module endpoint",
                    "placeholder": "http://localhost/nginx_status",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "log_path",
                    "display_label": "Access Log Path",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Path to Nginx access log file",
                    "placeholder": "/var/log/nginx/access.log",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Apache
        {
            "provider": {
                "name": "apache",
                "display_name": "Apache HTTP Server",
                "description": "Connect to Apache for web server monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/apache.svg",
                "brand_color": "#D22128",
                "documentation_url": "https://httpd.apache.org/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/apache",
                "tags": ["web server", "http", "apache", "monitoring"],
                "supported_features": ["request_monitoring", "performance_tracking", "module_monitoring"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "status_url",
                    "display_label": "Server Status URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Apache server-status endpoint",
                    "placeholder": "http://localhost/server-status?auto",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "log_path",
                    "display_label": "Access Log Path",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Path to Apache access log file",
                    "placeholder": "/var/log/apache2/access.log",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Sentry
        {
            "provider": {
                "name": "sentry",
                "display_name": "Sentry",
                "description": "Connect to Sentry for error tracking and performance monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/sentry.svg",
                "brand_color": "#362D59",
                "documentation_url": "https://docs.sentry.io/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/sentry",
                "tags": ["error tracking", "performance", "monitoring", "debugging"],
                "supported_features": ["error_tracking", "performance_monitoring", "release_tracking"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "auth_token",
                    "display_label": "Auth Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Sentry API Auth Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "organization",
                    "display_label": "Organization",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Sentry organization slug",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                },
                {
                    "field_name": "project",
                    "display_label": "Project",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Sentry project slug",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "configuration"
                }
            ]
        },
        # Rollbar
        {
            "provider": {
                "name": "rollbar",
                "display_name": "Rollbar",
                "description": "Connect to Rollbar for error tracking and monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/rollbar.svg",
                "brand_color": "#F25A3F",
                "documentation_url": "https://docs.rollbar.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/rollbar",
                "tags": ["error tracking", "monitoring", "debugging", "logging"],
                "supported_features": ["error_tracking", "deploy_tracking", "real_time_alerts"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "access_token",
                    "display_label": "Read Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Rollbar Read Access Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                }
            ]
        },
        # Bugsnag
        {
            "provider": {
                "name": "bugsnag",
                "display_name": "Bugsnag",
                "description": "Connect to Bugsnag for error monitoring and stability tracking",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/bugsnag.svg",
                "brand_color": "#4949E7",
                "documentation_url": "https://docs.bugsnag.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/bugsnag",
                "tags": ["error tracking", "stability", "monitoring", "crashes"],
                "supported_features": ["error_tracking", "release_tracking", "user_tracking"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "auth_token",
                    "display_label": "Auth Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Bugsnag API Auth Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "project_id",
                    "display_label": "Project ID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Bugsnag Project ID",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Honeycomb
        {
            "provider": {
                "name": "honeycomb",
                "display_name": "Honeycomb",
                "description": "Connect to Honeycomb for observability and performance monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/honeycomb.svg",
                "brand_color": "#F2B632",
                "documentation_url": "https://docs.honeycomb.io/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/honeycomb",
                "tags": ["observability", "tracing", "performance", "distributed systems"],
                "supported_features": ["distributed_tracing", "custom_metrics", "query_analysis"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Honeycomb API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "dataset",
                    "display_label": "Dataset",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Honeycomb dataset name",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Jaeger
        {
            "provider": {
                "name": "jaeger",
                "display_name": "Jaeger",
                "description": "Connect to Jaeger for distributed tracing and monitoring",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/jaeger.svg",
                "brand_color": "#60D0E4",
                "documentation_url": "https://www.jaegertracing.io/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/jaeger",
                "tags": ["tracing", "distributed systems", "microservices", "observability"],
                "supported_features": ["distributed_tracing", "service_map", "performance_analysis"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "query_endpoint",
                    "display_label": "Query Endpoint",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Jaeger Query service endpoint",
                    "placeholder": "http://jaeger-query:16686",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "username",
                    "display_label": "Username",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Basic auth username (if required)",
                    "is_required": False,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Zipkin
        {
            "provider": {
                "name": "zipkin",
                "display_name": "Zipkin",
                "description": "Connect to Zipkin for distributed tracing",
                "category": IntegrationCategory.MONITORING.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/zipkin.svg",
                "brand_color": "#FF6B35",
                "documentation_url": "https://zipkin.io/pages/documentation_v1.html",
                "setup_guide_url": "https://docs.integraite.pro/integrations/zipkin",
                "tags": ["tracing", "distributed systems", "latency", "debugging"],
                "supported_features": ["distributed_tracing", "latency_analysis", "dependency_tracking"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "base_url",
                    "display_label": "Zipkin URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Zipkin server base URL",
                    "placeholder": "http://zipkin:9411",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                }
            ]
        },
        # CircleCI
        {
            "provider": {
                "name": "circleci",
                "display_name": "CircleCI",
                "description": "Connect to CircleCI for CI/CD pipeline monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/circleci.svg",
                "brand_color": "#343434",
                "documentation_url": "https://circleci.com/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/circleci",
                "tags": ["ci/cd", "automation", "builds", "testing"],
                "supported_features": ["build_monitoring", "workflow_tracking", "test_results"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "CircleCI API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "organization",
                    "display_label": "Organization",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "CircleCI organization name",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Travis CI
        {
            "provider": {
                "name": "travisci",
                "display_name": "Travis CI",
                "description": "Connect to Travis CI for continuous integration monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/travisci.svg",
                "brand_color": "#3EAAAF",
                "documentation_url": "https://docs.travis-ci.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/travisci",
                "tags": ["ci/cd", "automation", "builds", "github"],
                "supported_features": ["build_monitoring", "repository_tracking", "build_alerts"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_token",
                    "display_label": "API Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Travis CI API Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "github_owner",
                    "display_label": "GitHub Owner",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "GitHub repository owner/organization",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # GitHub Actions
        {
            "provider": {
                "name": "github_actions",
                "display_name": "GitHub Actions",
                "description": "Connect to GitHub Actions for workflow and CI/CD monitoring",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/githubactions.svg",
                "brand_color": "#2088FF",
                "documentation_url": "https://docs.github.com/en/actions",
                "setup_guide_url": "https://docs.integraite.pro/integrations/github-actions",
                "tags": ["ci/cd", "automation", "workflows", "github"],
                "supported_features": ["workflow_monitoring", "job_tracking", "artifact_management"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "access_token",
                    "display_label": "GitHub Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "GitHub Personal Access Token with Actions scope",
                    "placeholder": "ghp_xxxxxxxxxxxxxxxxxxxx",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "repository",
                    "display_label": "Repository",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Repository in format owner/repo",
                    "placeholder": "company/project",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Azure DevOps
        {
            "provider": {
                "name": "azure_devops",
                "display_name": "Azure DevOps",
                "description": "Connect to Azure DevOps for CI/CD and project management",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/azuredevops.svg",
                "brand_color": "#0078D7",
                "documentation_url": "https://docs.microsoft.com/en-us/azure/devops/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/azure-devops",
                "tags": ["ci/cd", "project management", "microsoft", "pipelines"],
                "supported_features": ["pipeline_monitoring", "work_item_tracking", "repository_monitoring"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "organization_url",
                    "display_label": "Organization URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "Azure DevOps organization URL",
                    "placeholder": "https://dev.azure.com/yourorg",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "personal_access_token",
                    "display_label": "Personal Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Azure DevOps Personal Access Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "project",
                    "display_label": "Project",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Azure DevOps project name",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "configuration"
                }
            ]
        },
        # Sonar
        {
            "provider": {
                "name": "sonarqube",
                "display_name": "SonarQube",
                "description": "Connect to SonarQube for code quality and security analysis",
                "category": IntegrationCategory.CI_CD.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/sonarqube.svg",
                "brand_color": "#4E9BCD",
                "documentation_url": "https://docs.sonarqube.org/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/sonarqube",
                "tags": ["code quality", "security", "static analysis", "technical debt"],
                "supported_features": ["quality_gates", "security_hotspots", "technical_debt_tracking"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "server_url",
                    "display_label": "SonarQube URL",
                    "field_type": ConfigurationFieldType.URL.value,
                    "description": "SonarQube server URL",
                    "placeholder": "https://sonarqube.company.com",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "connection"
                },
                {
                    "field_name": "token",
                    "display_label": "User Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "SonarQube user token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                },
                {
                    "field_name": "project_key",
                    "display_label": "Project Key",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "SonarQube project key",
                    "is_required": True,
                    "sort_order": 3,
                    "field_group": "configuration"
                }
            ]
        },
        # Stripe
        {
            "provider": {
                "name": "stripe",
                "display_name": "Stripe",
                "description": "Connect to Stripe for payment processing and financial monitoring",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/stripe.svg",
                "brand_color": "#635BFF",
                "documentation_url": "https://stripe.com/docs",
                "setup_guide_url": "https://docs.integraite.pro/integrations/stripe",
                "tags": ["payments", "billing", "subscriptions", "fintech"],
                "supported_features": ["transaction_monitoring", "subscription_tracking", "webhook_processing"],
                "is_featured": True
            },
            "fields": [
                {
                    "field_name": "secret_key",
                    "display_label": "Secret Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Stripe Secret Key (sk_...)",
                    "placeholder": "sk_test_...",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "webhook_secret",
                    "display_label": "Webhook Secret",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Stripe Webhook Endpoint Secret",
                    "placeholder": "whsec_...",
                    "is_required": False,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # Twilio
        {
            "provider": {
                "name": "twilio",
                "display_name": "Twilio",
                "description": "Connect to Twilio for SMS, voice, and communication monitoring",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/twilio.svg",
                "brand_color": "#F22F46",
                "documentation_url": "https://www.twilio.com/docs",
                "setup_guide_url": "https://docs.integraite.pro/integrations/twilio",
                "tags": ["sms", "voice", "communication", "messaging"],
                "supported_features": ["message_tracking", "call_monitoring", "webhook_processing"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "account_sid",
                    "display_label": "Account SID",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Twilio Account SID",
                    "placeholder": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "is_required": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "auth_token",
                    "display_label": "Auth Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Twilio Auth Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        },
        # SendGrid
        {
            "provider": {
                "name": "sendgrid",
                "display_name": "SendGrid",
                "description": "Connect to SendGrid for email delivery monitoring",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/sendgrid.svg",
                "brand_color": "#1A82E2",
                "documentation_url": "https://docs.sendgrid.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/sendgrid",
                "tags": ["email", "delivery", "marketing", "transactional"],
                "supported_features": ["delivery_tracking", "bounce_monitoring", "engagement_analytics"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "SendGrid API Key",
                    "placeholder": "SG.xxxxxxxxxxxxxxxx",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                }
            ]
        },
        # Mailgun
        {
            "provider": {
                "name": "mailgun",
                "display_name": "Mailgun",
                "description": "Connect to Mailgun for email service monitoring",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/mailgun.svg",
                "brand_color": "#F56500",
                "documentation_url": "https://documentation.mailgun.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/mailgun",
                "tags": ["email", "delivery", "api", "messaging"],
                "supported_features": ["delivery_tracking", "bounce_handling", "analytics"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Mailgun API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "domain",
                    "display_label": "Domain",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Mailgun domain name",
                    "placeholder": "mg.example.com",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Segment
        {
            "provider": {
                "name": "segment",
                "display_name": "Segment",
                "description": "Connect to Segment for customer data platform monitoring",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/segment.svg",
                "brand_color": "#52BD95",
                "documentation_url": "https://segment.com/docs/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/segment",
                "tags": ["analytics", "customer data", "tracking", "cdp"],
                "supported_features": ["event_tracking", "user_analytics", "destination_monitoring"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "access_token",
                    "display_label": "Access Token",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Segment API Access Token",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "workspace_slug",
                    "display_label": "Workspace Slug",
                    "field_type": ConfigurationFieldType.TEXT.value,
                    "description": "Segment workspace slug",
                    "is_required": True,
                    "sort_order": 2,
                    "field_group": "configuration"
                }
            ]
        },
        # Amplitude
        {
            "provider": {
                "name": "amplitude",
                "display_name": "Amplitude",
                "description": "Connect to Amplitude for product analytics and user behavior tracking",
                "category": IntegrationCategory.COMMUNICATION.value,
                "status": IntegrationStatus.AVAILABLE.value,
                "icon_url": "https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/amplitude.svg",
                "brand_color": "#2E5BFF",
                "documentation_url": "https://developers.amplitude.com/",
                "setup_guide_url": "https://docs.integraite.pro/integrations/amplitude",
                "tags": ["analytics", "product", "user behavior", "events"],
                "supported_features": ["event_analytics", "user_segmentation", "funnel_analysis"],
                "is_featured": False
            },
            "fields": [
                {
                    "field_name": "api_key",
                    "display_label": "API Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Amplitude API Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 1,
                    "field_group": "credentials"
                },
                {
                    "field_name": "secret_key",
                    "display_label": "Secret Key",
                    "field_type": ConfigurationFieldType.PASSWORD.value,
                    "description": "Amplitude Secret Key",
                    "is_required": True,
                    "is_sensitive": True,
                    "sort_order": 2,
                    "field_group": "credentials"
                }
            ]
        }
    ]
    
    # Create providers and their configuration fields
    for provider_data in providers_data:
        # Create provider
        provider = IntegrationProvider(**provider_data["provider"])
        db.add(provider)
        await db.flush()  # Get the ID without committing
        
        # Create configuration fields
        for field_data in provider_data["fields"]:
            field = IntegrationConfigurationField(
                provider_id=provider.id,
                **field_data
            )
            db.add(field)
    
    await db.commit()
    print(f"   🔗 Created {len(providers_data)} integration providers")


async def init_database():
    """Initialize database with tables and seed data"""
    try:
        await create_tables()
        
        # Get database session for seeding
        async with AsyncSessionLocal() as db:
            # await seed_dummy_data()
            await seed_integration_providers(db)
        
        print("🎉 Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    # Run the database initialization
    asyncio.run(init_database())
