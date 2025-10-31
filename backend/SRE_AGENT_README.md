# 🤖 Autonomous SRE Agent System

This document describes the autonomous Self-Healing SRE (Site Reliability Engineering) Agent system that can automatically diagnose and resolve incidents from ServiceNow webhooks.

## 🏗️ Architecture Overview

The SRE Agent system consists of several key components:

### Core Components

1. **ServiceNow Webhook Receiver** (`/api/v1/incident/trigger-agent`)
   - Receives incident data from ServiceNow webhooks
   - Validates incoming payloads
   - Triggers autonomous agent execution

2. **Self-Healing SRE Agent** (`app/services/self_healing_sre_agent.py`)
   - LangGraph-powered autonomous workflow
   - ChatOpenAI integration for intelligent reasoning
   - SSH command execution for system remediation
   - Real-time database tracking

3. **Database Tracking System** (`app/models/sre_execution.py`)
   - Comprehensive audit trail
   - Real-time execution monitoring
   - Evidence collection and provenance tracking

4. **Monitoring APIs** (`app/api/v1/endpoints/sre_agent.py`)
   - Execution status monitoring
   - Detailed log retrieval
   - Active execution tracking

### Workflow States

The autonomous agent follows a structured workflow:

```
📊 Analyze → 🔬 Hypothesize → 🩺 Diagnose → 🔧 Remediate → ✅ Verify → 🏁 Finalize
```

Each state includes:
- **Analyze**: Initial incident assessment and evidence collection
- **Hypothesize**: Generate potential root causes using AI reasoning
- **Diagnose**: Execute diagnostic commands to validate hypotheses
- **Remediate**: Apply targeted fixes based on diagnosis results
- **Verify**: Confirm resolution through verification checks
- **Finalize**: Complete execution with summary and audit trail

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- OpenAI API key
- ServiceNow instance (for live integration)

### 2. Environment Setup

```bash
# Set required environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SERVICENOW_INSTANCE_URL="https://your-instance.service-now.com"
export SERVICENOW_USERNAME="your-username"  
export SERVICENOW_PASSWORD="your-password"

# For real SSH execution (optional)
export ENABLE_REAL_SSH="true"
```

### 3. Start the Server

```bash
# Option 1: Use the startup script
python start_server.py

# Option 2: Manual startup
pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the System

```bash
# Run the comprehensive test suite
python test_sre_agent.py
```

## 📡 API Endpoints

### Webhook Endpoint

**POST** `/api/v1/incident/trigger-agent`

Trigger autonomous incident resolution from ServiceNow webhook:

```json
{
  "incident_number": "INC0010001",
  "short_description": "Web server down - 500 errors",
  "description": "The main web server is returning 500 internal server errors.",
  "priority": "1 - Critical",
  "category": "Software",
  "assignment_group": "SRE Team",
  "state": "2",
  "target": {
    "ip_address": "10.0.1.100",
    "hostname": "web-prod-01.company.com",
    "service": "nginx"
  }
}
```

Response:
```json
{
  "message": "SRE Agent triggered successfully",
  "execution_id": 123,
  "incident_number": "INC0010001",
  "status": "running"
}
```

### Monitoring Endpoints

**GET** `/api/v1/incident/execution/{execution_id}`

Get detailed execution status and real-time progress:

```json
{
  "execution_id": 123,
  "incident_number": "INC0010001",
  "status": "running",
  "current_step": "diagnose",
  "started_at": "2025-10-30T10:00:00Z",
  "timeline": [
    {
      "step_number": 1,
      "action_type": "analyze",
      "title": "Analyzing incident data",
      "status": "completed",
      "duration_seconds": 5
    }
  ],
  "hypotheses": [
    {
      "hypothesis_text": "Nginx service may be down",
      "confidence_score": 85,
      "status": "validated"
    }
  ]
}
```

**GET** `/api/v1/incident/execution/{execution_id}/logs`

Get detailed execution logs:

```json
{
  "execution_id": 123,
  "logs": [
    {
      "step": 1,
      "action_type": "analyze",
      "command_executed": "systemctl status nginx",
      "command_output": "● nginx.service - active (running)",
      "status": "completed"
    }
  ]
}
```

**GET** `/api/v1/incident/executions/active`

Get all currently active executions:

```json
{
  "executions": [
    {
      "execution_id": 123,
      "incident_number": "INC0010001",
      "status": "running",
      "started_at": "2025-10-30T10:00:00Z"
    }
  ]
}
```

## 🔧 SSH Configuration

Configure target systems in `ssh_config.py`:

```python
DEVELOPMENT_TARGETS = {
    "web-prod-01.company.com": {
        "ip": "10.0.1.100",
        "username": "sre-agent",
        "port": 22,
        "ssh_key_path": "/etc/sre-agent/keys/sre-agent-key",
        "services": ["nginx", "apache2", "docker"],
        "description": "Main web server"
    }
}
```

### SSH Key Setup

1. Generate SSH key pair:
```bash
ssh-keygen -t rsa -b 4096 -f /etc/sre-agent/keys/sre-agent-key -N ""
```

2. Add public key to target servers:
```bash
ssh-copy-id -i /etc/sre-agent/keys/sre-agent-key.pub sre-agent@target-server
```

3. Set proper permissions:
```bash
chmod 600 /etc/sre-agent/keys/sre-agent-key
chmod 644 /etc/sre-agent/keys/sre-agent-key.pub
```

## 🗄️ Database Schema

The system uses 7 tables to track autonomous agent executions:

1. **sre_incident_execution** - Main execution tracking
2. **incident_execution_log** - Detailed step-by-step logs
3. **sre_timeline_entry** - Action timeline for UI
4. **sre_hypothesis** - AI-generated hypotheses
5. **sre_verification** - Resolution verification results
6. **sre_evidence** - Collected diagnostic evidence
7. **sre_provenance** - Reasoning chain tracking

## 🔍 Monitoring & Debugging

### Real-time Monitoring

The system provides comprehensive real-time monitoring:

- **Execution Status**: Track agent progress through workflow states
- **Timeline Tracking**: See detailed action timeline with durations
- **Hypothesis Evolution**: Monitor AI reasoning and confidence scores
- **Command Execution**: Audit all SSH commands and outputs
- **Verification Results**: Track resolution verification status

### Debugging Tips

1. **Check Agent Logs**: Use execution logs endpoint for detailed debugging
2. **Monitor Timeline**: Track where agent execution might be stuck
3. **Verify SSH Config**: Ensure target systems are properly configured
4. **Test Connectivity**: Use test script to validate end-to-end flow

### Log Levels

Set logging level via environment variable:
```bash
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## 🔒 Security Considerations

### Production Deployment

1. **SSH Key Management**: Use secure key storage (HashiCorp Vault, AWS Secrets Manager)
2. **Network Security**: Restrict SSH access to SRE agent systems only
3. **Audit Logging**: All commands and actions are logged for compliance
4. **Access Control**: Implement proper API authentication and authorization
5. **Secret Management**: Never commit SSH keys or passwords to version control

### Safety Features

1. **Command Validation**: All SSH commands are validated before execution
2. **Simulation Mode**: Default behavior simulates commands for safety
3. **Rollback Capability**: Track changes for potential rollback scenarios
4. **Human Oversight**: All actions are logged for human review

## 🎯 Supported Incident Types

The agent currently handles:

- **Service Outages**: Nginx, Apache, Docker, databases
- **Performance Issues**: High CPU, memory, disk usage
- **Network Connectivity**: Port availability, DNS resolution
- **Application Errors**: HTTP errors, service failures

### Diagnostic Commands

- Service status checks (`systemctl status`)
- Resource monitoring (`top`, `df`, `ps`)
- Network diagnostics (`curl`, `ping`, `netstat`)
- Log analysis (`tail`, `grep`, custom parsing)

### Remediation Actions

- Service restarts (`systemctl restart`)
- Resource cleanup (log rotation, cache clearing)
- Process management (kill runaway processes)
- Configuration fixes (nginx config, permissions)

## 📊 Dashboard Integration

The system integrates with the frontend dashboard for:

- **Real-time Execution Monitoring**: Live updates of agent progress
- **Historical Incident Tracking**: Review past autonomous resolutions
- **Performance Metrics**: Success rates, resolution times, patterns
- **Alert Management**: Notifications for failed or stuck executions

## 🔄 Continuous Improvement

The autonomous agent learns and improves through:

1. **Evidence Collection**: Systematic gathering of diagnostic data
2. **Hypothesis Tracking**: AI reasoning validation and refinement
3. **Success Pattern Recognition**: Identifying effective remediation strategies
4. **Failure Analysis**: Learning from unsuccessful resolution attempts

## 📞 Support & Troubleshooting

### Common Issues

1. **Agent Not Triggering**: Check webhook endpoint and payload format
2. **SSH Failures**: Verify target configuration and connectivity
3. **AI Reasoning Issues**: Ensure OpenAI API key is valid and has sufficient quota
4. **Database Errors**: Run migrations and check database connectivity

### Getting Help

- Check execution logs for detailed error information
- Use test script to validate system components
- Review database records for audit trail
- Enable debug logging for detailed troubleshooting

---

The Autonomous SRE Agent represents a significant advancement in automated incident response, providing intelligent, traceable, and safe resolution of common infrastructure issues while maintaining comprehensive audit trails for compliance and continuous improvement.