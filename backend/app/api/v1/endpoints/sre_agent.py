"""
SRE Agent API endpoint for triggering autonomous incident resolution
"""

import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.services.self_healing_sre_agent import SREAgent
from app.models.sre_execution import (
    SREIncidentExecution, IncidentExecutionLog, SRETimelineEntry,
    SREHypothesis, SREVerification, SREEvidence
)
from langchain_core.messages import HumanMessage, AIMessage
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
    request: Request,
    background_tasks: BackgroundTasks
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
    try:
        # Get the raw JSON payload
        payload = await request.json()
        print("Payload is ", payload)
        
        # Handle both ServiceNow format (with result array) and direct incident format
        if "result" in payload and payload["result"]:
            # ServiceNow format: {"result": [incident_data]}
            incident_data = payload["result"][0]
            # Create proper payload dict for background task
            payload_for_task = payload
        else:
            # Direct incident format: incident_data directly
            incident_data = payload
            # Wrap in ServiceNow format for background task consistency
            payload_for_task = {"result": [incident_data]}
        
        incident_number = incident_data.get("number", f"INC{int(time.time())}")
        
        logger.info(f"Triggering SRE agent for incident {incident_number}")
        
        # Trigger background processing - no database operations here
        background_tasks.add_task(
            process_incident_with_agent,
            payload_for_task
        )
        
        return SREAgentTriggerResponse(
            message="SRE agent triggered successfully",
            incident_number=incident_number,
            status="initiated",
            execution_id=0,  # Will be set by the background agent
            dashboard_url=f"/dashboard/incident/{incident_number}"
        )
        
    except Exception as e:
        logger.error(f"Failed to trigger SRE agent: {e}")
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
    Background task to process incident with SRE agent
    """
    
    try:
        # Create a new database session for the background task
        from app.core.database import AsyncSessionLocal
        
        sre_agent = SREAgent()
        incident_number = servicenow_payload.get("result", [{}])[0].get("number", "unknown")
        incident_description = servicenow_payload.get("result", [{}])[0].get("short_description", "")
        incident = f"{incident_number}: {incident_description}"
        sre_agent.logger.start_incident_logging(incident)
        app = sre_agent.create_workflow()

        initial_input = {"messages":[HumanMessage(content=incident)]}

         # Stream the execution
        try:
            step_count = 0
            for event in app.stream(initial_input, stream_mode="values"):
                step_count += 1
                print(f"\n--- Step {step_count} ---")
                
                messages = event.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    
                    if hasattr(last_message, 'content'):
                        print(f"💭 Agent: {last_message.content}")
                    
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        for tool_call in last_message.tool_calls:
                            print(f"🔧 Executing: {tool_call['name']} with args: {tool_call['args']}")
                    
                    # If this is a tool result, show it
                    if hasattr(last_message, 'content') and isinstance(last_message.content, str):
                        if "STDOUT:" in last_message.content or "STDERR:" in last_message.content:
                            print(f"📋 Command Result:\n{last_message.content}")
                
                print("-" * 40)
            
            # Log incident completion
            sre_agent.logger.log_incident_completion("COMPLETED", "Incident resolution workflow finished")
            
            # Get incident summary
            summary = sre_agent.logger.get_incident_summary()
            
            print(f"\n✅ Incident resolution completed in {step_count} steps")
            print(f"\n📋 INCIDENT LOGGING SUMMARY")
            print(f"   Incident ID: {summary.get('incident_id', 'N/A')}")
            print(f"   Total Steps Logged: {summary.get('total_steps', 0)}")
            print(f"   Duration: {summary.get('duration_seconds', 0):.1f} seconds")
            print(f"   Log File: {summary.get('log_file', 'N/A')}")
            print(f"   Start Time: {summary.get('start_time', 'N/A')}")
            print(f"   End Time: {summary.get('end_time', 'N/A')}")
            
        except Exception as e:
            # Log error
            if 'sre_agent' in locals():
                sre_agent.logger.log_incident_completion("ERROR", f"Error during execution: {str(e)}")
            
            print(f"\n❌ Error during execution: {str(e)}")
            print("Please check your configuration and network connectivity.")

    except Exception as e:
        logger.error(f"Error in background agent processing: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


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