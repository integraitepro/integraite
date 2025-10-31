"""
SRE Agent API endpoint for triggering autonomous incident resolution
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.services.self_healing_sre_agent import SelfHealingSREAgent
from app.models.sre_execution import (
    SREIncidentExecution, IncidentExecutionLog, SRETimelineEntry,
    SREHypothesis, SREVerification, SREEvidence
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceNowIncidentPayload(BaseModel):
    """ServiceNow incident payload structure"""
    result: List[Dict[str, Any]] = Field(..., description="Array of incident records from ServiceNow")


class SREAgentTriggerResponse(BaseModel):
    """Response from triggering the SRE agent"""
    message: str
    incident_number: str
    status: str
    execution_id: int
    dashboard_url: str


class SREExecutionStatusResponse(BaseModel):
    """Response for execution status queries"""
    execution_id: int
    incident_number: str
    status: str
    agent_name: str
    started_at: str
    completed_at: Optional[str] = None
    resolution_summary: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0


class SRETimelineResponse(BaseModel):
    """Timeline entry response"""
    id: int
    step_number: int
    timestamp: str
    action_type: str
    title: str
    description: str
    status: str
    duration_seconds: Optional[int] = None


class SREExecutionDetailResponse(BaseModel):
    """Detailed execution information"""
    execution: SREExecutionStatusResponse
    timeline: List[SRETimelineResponse]
    hypotheses: List[Dict[str, Any]]
    verifications: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    logs: List[Dict[str, Any]]


@router.post("/trigger-agent", response_model=SREAgentTriggerResponse)
async def trigger_sre_agent(
    payload: ServiceNowIncidentPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> SREAgentTriggerResponse:
    """
    Trigger the Self-Healing SRE Agent for autonomous incident resolution
    
    This endpoint receives ServiceNow incident data and triggers an autonomous
    SRE agent that will:
    1. Analyze the incident
    2. Generate hypotheses about root causes
    3. Execute diagnostic commands
    4. Attempt remediation
    5. Verify resolution
    6. Log all actions for real-time dashboard tracking
    """
    print("Inside the triggering whole")
    print("Payload is ", payload)
    try:
        # Validate payload
        if not payload.result:
            raise HTTPException(
                status_code=400,
                detail="No incident data provided in ServiceNow payload"
            )
        
        incident_data = payload.result[0]
        incident_number = incident_data.get("number", "")
        
        if not incident_number:
            raise HTTPException(
                status_code=400,
                detail="Incident number is required"
            )
        
        # Check if incident is already being processed
        existing_execution = await db.execute(
            select(SREIncidentExecution)
            .where(SREIncidentExecution.incident_number == incident_number)
        )
        existing = existing_execution.scalar_one_or_none()
        
        if existing:
            if existing.status in ["running", "initiated"]:
                return SREAgentTriggerResponse(
                    message="SRE agent already processing this incident",
                    incident_number=incident_number,
                    status=existing.status,
                    execution_id=existing.id,
                    dashboard_url=f"/dashboard/incident/{incident_number}"
                )
            else:
                # Reset the existing execution for reprocessing
                existing.status = "initiated"
                existing.agent_name = "SelfHealingSRE-v1.0"
                existing.completed_at = None
                existing.resolution_summary = None
                existing.final_hypothesis = None
                existing.servicenow_payload = payload.dict()
                
                await db.flush()
                await db.commit()
                
                # Trigger background processing
                background_tasks.add_task(
                    process_incident_with_agent,
                    payload.dict()
                )
                
                return SREAgentTriggerResponse(
                    message="SRE agent triggered successfully (reprocessing)",
                    incident_number=incident_number,
                    status="initiated",
                    execution_id=existing.id,
                    dashboard_url=f"/dashboard/incident/{incident_number}"
                )
        
        print("triggering sre agent for incident")
        
        logger.info(f"Triggering SRE agent for incident {incident_number}")
        
        # Create SRE agent and trigger processing in background
        background_tasks.add_task(
            process_incident_with_agent,
            payload.dict()
        )
        
        # Create initial execution record for immediate response
        # Handle assignment_group which can be either a dict with 'value' key or a string
        assignment_group_value = ""
        assignment_group_data = incident_data.get("assignment_group", "")
        if isinstance(assignment_group_data, dict):
            assignment_group_value = assignment_group_data.get("value", "")
        elif isinstance(assignment_group_data, str):
            assignment_group_value = assignment_group_data
        
        initial_execution = SREIncidentExecution(
            incident_number=incident_number,
            incident_title=incident_data.get("short_description", ""),
            incident_description=incident_data.get("description", ""),
            target_ip=incident_data.get("u_ip_address", ""),
            priority=incident_data.get("priority", "3"),
            category=incident_data.get("category", "unknown"),
            assignment_group=assignment_group_value,
            agent_name="SelfHealingSRE-v1.0",
            status="initiated",
            servicenow_payload=payload.dict()
        )
        
        db.add(initial_execution)
        await db.flush()
        await db.commit()
        
        return SREAgentTriggerResponse(
            message="SRE agent triggered successfully",
            incident_number=incident_number,
            status="initiated",
            execution_id=initial_execution.id,
            dashboard_url=f"/dashboard/incident/{incident_number}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering SRE agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger SRE agent: {str(e)}"
        )


@router.get("/execution/{execution_id}", response_model=SREExecutionDetailResponse)
async def get_execution_details(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
) -> SREExecutionDetailResponse:
    """
    Get detailed information about an SRE agent execution
    including timeline, hypotheses, verifications, and evidence
    """
    
    try:
        # Get execution with all related data
        result = await db.execute(
            select(SREIncidentExecution)
            .options(
                selectinload(SREIncidentExecution.timeline_entries),
                selectinload(SREIncidentExecution.hypotheses),
                selectinload(SREIncidentExecution.verifications),
                selectinload(SREIncidentExecution.logs)
            )
            .where(SREIncidentExecution.id == execution_id)
        )
        
        execution = result.scalar_one_or_none()
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Get evidence separately (no direct relationship defined)
        evidence_result = await db.execute(
            select(SREEvidence)
            .where(SREEvidence.incident_execution_id == execution_id)
            .order_by(SREEvidence.collected_at)
        )
        evidence_records = evidence_result.scalars().all()
        
        # Build response
        execution_response = SREExecutionStatusResponse(
            execution_id=execution.id,
            incident_number=execution.incident_number,
            status=execution.status,
            agent_name=execution.agent_name,
            started_at=execution.started_at.isoformat(),
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            resolution_summary=execution.resolution_summary if execution.resolution_summary else None,
            current_step=len(execution.timeline_entries),
            total_steps=len(execution.timeline_entries)
        )
        
        timeline = [
            SRETimelineResponse(
                id=entry.id,
                step_number=entry.step_number,
                timestamp=entry.timestamp.isoformat(),
                action_type=entry.action_type,
                title=entry.title,
                description=entry.description or "",
                status=entry.status,
                duration_seconds=entry.duration_seconds
            )
            for entry in execution.timeline_entries
        ]
        
        hypotheses = [
            {
                "id": h.id,
                "hypothesis_text": h.hypothesis_text,
                "confidence_score": h.confidence_score,
                "reasoning": h.reasoning,
                "status": h.status,
                "created_at": h.created_at.isoformat(),
                "supporting_evidence": h.supporting_evidence
            }
            for h in execution.hypotheses
        ]
        
        verifications = [
            {
                "id": v.id,
                "verification_type": v.verification_type,
                "description": v.description,
                "command_executed": v.command_executed,
                "expected_result": v.expected_result,
                "actual_result": v.actual_result,
                "success": v.success,
                "timestamp": v.timestamp.isoformat(),
                "metadata": v.verification_metadata
            }
            for v in execution.verifications
        ]
        
        evidence = [
            {
                "id": e.id,
                "evidence_type": e.evidence_type,
                "source": e.source,
                "content": e.content,
                "metadata": e.evidence_metadata,
                "collected_at": e.collected_at.isoformat(),
                "relevance_score": e.relevance_score
            }
            for e in evidence_records
        ]
        
        logs = [
            {
                "id": log.id,
                "step": log.step,
                "timestamp": log.timestamp.isoformat(),
                "action_type": log.action_type,
                "hypothesis": log.hypothesis,
                "command_executed": log.command_executed,
                "command_output": log.command_output,
                "verification": log.verification,
                "status": log.status,
                "evidence": log.evidence,
                "provenance": log.provenance
            }
            for log in execution.logs
        ]
        
        return SREExecutionDetailResponse(
            execution=execution_response,
            timeline=timeline,
            hypotheses=hypotheses,
            verifications=verifications,
            evidence=evidence,
            logs=logs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching execution details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch execution details: {str(e)}"
        )


@router.get("/execution/{execution_id}/status", response_model=SREExecutionStatusResponse)
async def get_execution_status(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
) -> SREExecutionStatusResponse:
    """
    Get the current status of an SRE agent execution
    (Lightweight endpoint for real-time dashboard polling)
    """
    
    try:
        result = await db.execute(
            select(SREIncidentExecution)
            .where(SREIncidentExecution.id == execution_id)
        )
        
        execution = result.scalar_one_or_none()
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Get current step count
        timeline_count_result = await db.execute(
            select(SRETimelineEntry)
            .where(SRETimelineEntry.incident_execution_id == execution_id)
        )
        timeline_entries = timeline_count_result.scalars().all()
        current_step = len(timeline_entries)
        
        return SREExecutionStatusResponse(
            execution_id=execution.id,
            incident_number=execution.incident_number,
            status=execution.status,
            agent_name=execution.agent_name,
            started_at=execution.started_at.isoformat(),
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            resolution_summary=execution.resolution_summary if execution.resolution_summary else None,
            current_step=current_step,
            total_steps=current_step
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching execution status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch execution status: {str(e)}"
        )


@router.get("/incident/{incident_number}/executions")
async def get_incident_executions(
    incident_number: str,
    db: AsyncSession = Depends(get_db)
) -> List[SREExecutionStatusResponse]:
    """
    Get all SRE agent executions for a specific incident number
    """
    
    try:
        result = await db.execute(
            select(SREIncidentExecution)
            .where(SREIncidentExecution.incident_number == incident_number)
            .order_by(SREIncidentExecution.started_at.desc())
        )
        
        executions = result.scalars().all()
        
        return [
            SREExecutionStatusResponse(
                execution_id=exec.id,
                incident_number=exec.incident_number,
                status=exec.status,
                agent_name=exec.agent_name,
                started_at=exec.started_at.isoformat(),
                completed_at=exec.completed_at.isoformat() if exec.completed_at else None,
                resolution_summary=exec.resolution_summary if exec.resolution_summary else None,
                current_step=0,  # Would need to calculate
                total_steps=0
            )
            for exec in executions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching incident executions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch incident executions: {str(e)}"
        )


async def process_incident_with_agent(servicenow_payload: Dict[str, Any]):
    """
    Background task to process incident with LangGraph SRE agent
    """
    
    try:
        # Import the LangGraph SRE agent components
        import os
        import asyncio
        from typing import Dict, Any, List
        from langchain_openai import ChatOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage, AIMessage
        from langgraph.graph import StateGraph, MessagesState
        from langgraph.prebuilt import ToolNode
        import paramiko
        import json
        import datetime
        
        # Create a new database session for the background task
        from app.core.database import AsyncSessionLocal
        from app.core.config import settings
        
        async with AsyncSessionLocal() as db_session:
            # Extract incident data
            incident_data = servicenow_payload.get("result", [{}])[0]
            incident_number = incident_data.get("number", "")
            incident_title = incident_data.get("short_description", "")
            incident_description = incident_data.get("description", "")
            target_ip = incident_data.get("u_ip_address", "")
            
            # Create or update execution record
            from sqlalchemy import select
            result = await db_session.execute(
                select(SREIncidentExecution)
                .where(SREIncidentExecution.incident_number == incident_number)
            )
            execution = result.scalar_one_or_none()
            
            if execution:
                execution.status = "running"
                execution.agent_name = "LangGraph-SRE-v2.0"
            else:
                execution = SREIncidentExecution(
                    incident_number=incident_number,
                    incident_title=incident_title,
                    incident_description=incident_description,
                    target_ip=target_ip,
                    priority=incident_data.get("priority", "3"),
                    category=incident_data.get("category", "unknown"),
                    assignment_group="",
                    agent_name="LangGraph-SRE-v2.0",
                    status="running",
                    servicenow_payload=servicenow_payload
                )
                db_session.add(execution)
            
            await db_session.flush()
            await db_session.commit()
            
            # Define SSH execution tool for the agent
            @tool
            def execute_ssh_command(ip_address: str, command: str) -> str:
                """Execute a command on a remote server via SSH."""
                try:
                    # Use environment-based SSH configuration
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Prepare connection parameters from settings
                    connect_kwargs = {
                        "hostname": ip_address,
                        "username": settings.SSH_USERNAME,
                        "port": settings.SSH_PORT,
                        "timeout": settings.SSH_TIMEOUT
                    }
                    
                    # Use SSH key authentication if configured
                    if settings.SSH_PRIVATE_KEY_PATH and os.path.exists(settings.SSH_PRIVATE_KEY_PATH):
                        connect_kwargs["key_filename"] = settings.SSH_PRIVATE_KEY_PATH
                        logger.info(f"Using SSH key authentication from {settings.SSH_PRIVATE_KEY_PATH}")
                    else:
                        logger.warning(f"No SSH key configured, simulating execution")
                        return f"Command '{command}' executed successfully (simulated - no SSH key configured)"
                    
                    # Check if real SSH is enabled
                    if not settings.ENABLE_REAL_SSH:
                        logger.info(f"Simulating SSH command on {ip_address}: {command}")
                        return f"Command '{command}' executed successfully (simulated - ENABLE_REAL_SSH=False)"
                    
                    # Real SSH execution
                    logger.info(f"Executing real SSH command on {ip_address}: {command}")
                    ssh_client.connect(**connect_kwargs)
                    stdin, stdout, stderr = ssh_client.exec_command(command)
                    
                    # Read output and error
                    stdout_output = stdout.read().decode('utf-8').strip()
                    stderr_output = stderr.read().decode('utf-8').strip()
                    exit_code = stdout.channel.recv_exit_status()
                    
                    ssh_client.close()
                    
                    # Format response
                    result = ""
                    if stdout_output:
                        result += f"STDOUT:\n{stdout_output}\n"
                    if stderr_output:
                        result += f"STDERR:\n{stderr_output}\n"
                    result += f"EXIT_STATUS: {exit_code}"
                    
                    return result if result else "Command executed successfully (no output)"
                    
                except Exception as e:
                    logger.error(f"SSH execution failed: {e}")
                    return f"ERROR: SSH execution failed: {str(e)}"
            
            @tool
            def close_servicenow_incident(incident_number: str, resolution_summary: str) -> str:
                """Close the ServiceNow incident with resolution details."""
                try:
                    # Update the execution record in database
                    execution.status = "completed"
                    execution.completed_at = datetime.datetime.utcnow()
                    execution.resolution_summary = resolution_summary
                    
                    # In a real implementation, this would call ServiceNow API
                    logger.info(f"Incident {incident_number} resolved: {resolution_summary}")
                    return f"SUCCESS: Incident {incident_number} has been successfully closed with resolution: {resolution_summary}"
                    
                except Exception as e:
                    logger.error(f"Failed to close incident: {e}")
                    return f"ERROR: Failed to close incident: {str(e)}"
            
            # Initialize LangGraph SRE Agent
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                api_key=settings.OPENAI_API_KEY
            )
            
            tools = [execute_ssh_command, close_servicenow_incident]
            llm_with_tools = llm.bind_tools(tools)
            tool_node = ToolNode(tools)
            
            system_prompt = """You are an expert SRE (Site Reliability Engineer) autonomous agent. 
Your sole purpose is to resolve IT incidents.

You will be given an incident description.
1. First, analyze the incident to understand the problem and identify the target machine.
2. You have two tools: `execute_ssh_command` and `close_servicenow_incident`.
3. You MUST use the SSH tool to run diagnostic commands (like `systemctl status`, `grep logs`, `df -h`).
4. Based on the command output, determine the root cause.
5. Generate and execute commands to fix the problem (e.g., `systemctl start <service>`).
6. Verify the fix by running diagnostic commands.
7. Generate one command at a time. Do not try to run multiple commands in one tool call.
8. Once you have verified the fix is successful, you MUST use `close_servicenow_incident` to close the incident.
Your final answer should be a report of what you found, what you did, and the verified outcome."""
            
            def agent_node(state: MessagesState) -> Dict[str, Any]:
                messages = state["messages"]
                if not messages or not any("SRE" in str(msg.content) for msg in messages):
                    system_message = AIMessage(content=system_prompt)
                    messages = [system_message] + messages
                
                response = llm_with_tools.invoke(messages)
                return {"messages": [response]}
            
            def should_continue(state: MessagesState) -> str:
                messages = state["messages"]
                last_message = messages[-1]
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    return "executor"
                else:
                    return "end"
            
            # Create workflow
            workflow = StateGraph(MessagesState)
            workflow.add_node("agent", agent_node)
            workflow.add_node("executor", tool_node)
            workflow.set_entry_point("agent")
            workflow.add_conditional_edges("agent", should_continue, {
                "executor": "executor",
                "end": "__end__"
            })
            workflow.add_edge("executor", "agent")
            
            app = workflow.compile()
            
            # Prepare incident description for the agent
            full_incident_description = f"""
INCIDENT REPORT
===============
Incident Number: {incident_number}
Title: {incident_title}
Description: {incident_description}
Target IP: {target_ip}
Priority: {incident_data.get('priority', 'Unknown')}
Category: {incident_data.get('category', 'Unknown')}

Please analyze this incident and take appropriate action to resolve it.
"""
            
            # Run the agent
            logger.info(f"Starting LangGraph SRE agent for incident {incident_number}")
            
            # Execute the workflow
            result = await asyncio.create_task(
                app.ainvoke({"messages": [HumanMessage(content=full_incident_description)]})
            )
            
            # Update execution record with final status
            if execution.status == "running":
                execution.status = "completed" if "SUCCESS" in str(result) else "failed"
                execution.completed_at = datetime.datetime.utcnow()
            
            await db_session.commit()
            
            logger.info(f"LangGraph SRE agent completed processing for incident {incident_number}")
            
    except Exception as e:
        logger.error(f"Error in LangGraph SRE agent processing: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update execution status to failed
        try:
            async with AsyncSessionLocal() as db_session:
                incident_data = servicenow_payload.get("result", [{}])[0]
                incident_number = incident_data.get("number", "")
                
                result = await db_session.execute(
                    select(SREIncidentExecution)
                    .where(SREIncidentExecution.incident_number == incident_number)
                )
                execution = result.scalar_one_or_none()
                if execution:
                    execution.status = "failed"
                    execution.completed_at = datetime.datetime.utcnow()
                    await db_session.commit()
        except Exception as db_error:
            logger.error(f"Failed to update execution status: {db_error}")


# Test endpoint for development
@router.post("/test-trigger")
async def test_trigger_sre_agent(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> SREAgentTriggerResponse:
    """
    Test endpoint with sample ServiceNow data for development
    """
    
    test_payload = {
        "result": [
            {
                "number": "INC0000060",
                "short_description": "Tomcat service down on production server",
                "description": "Tomcat web service is not responding on the production server. Users cannot access the application.",
                "assignment_group": {"value": "287ebd7da9fe198100f92cc8d1d2154e"},
                "category": "software",
                "state": "2",
                "priority": "2",
                "cmdb_ci": {"value": "109562a3c611227500a7b7ff98cc0dc7"},
                "u_ip_address": "13.60.250.208",
                "sys_created_on": "2025-10-30 10:30:00",
                "sys_updated_on": "2025-10-30 10:35:00"
            }
        ]
    }
    
    payload = ServiceNowIncidentPayload(**test_payload)
    
    return await trigger_sre_agent(payload, background_tasks, db)