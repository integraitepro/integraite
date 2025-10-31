"""
SRE Execution service for fetching and processing SRE agent execution data
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

from app.models.sre_execution import (
    SREIncidentExecution, SRETimelineEntry, SREHypothesis,
    SREVerification, SREEvidence, SREProvenance, IncidentExecutionLog
)
from app.schemas.sre_execution import (
    SREIncidentExecutionResponse, SRETimelineEntryResponse,
    SREHypothesisResponse, SREVerificationResponse,
    SREEvidenceResponse, SREProvenanceResponse,
    IncidentExecutionLogResponse, SREExecutionAgent,
    SREExecutionSummary
)

logger = logging.getLogger(__name__)


class SREExecutionService:
    """Service for handling SRE execution data"""
    
    @staticmethod
    async def get_sre_execution_by_incident_number(
        incident_number: str, 
        db: AsyncSession
    ) -> Optional[SREIncidentExecutionResponse]:
        """Get SRE execution data by incident number"""
        
        try:
            # Query for SRE execution with all related data
            result = await db.execute(
                select(SREIncidentExecution)
                .options(
                    selectinload(SREIncidentExecution.timeline_entries),
                    selectinload(SREIncidentExecution.hypotheses),
                    selectinload(SREIncidentExecution.verifications),
                    selectinload(SREIncidentExecution.logs)
                )
                .where(SREIncidentExecution.incident_number == incident_number)
            )
            
            sre_execution = result.scalar_one_or_none()
            if not sre_execution:
                return None
            
            # Get evidence and provenance separately to avoid complex joins
            evidence_result = await db.execute(
                select(SREEvidence)
                .where(SREEvidence.incident_execution_id_ref == sre_execution.id)
            )
            evidence_items = evidence_result.scalars().all()
            
            provenance_result = await db.execute(
                select(SREProvenance)
                .where(SREProvenance.incident_execution_id_ref == sre_execution.id)
            )
            provenance_items = provenance_result.scalars().all()
            
            # Convert to response models
            timeline_entries = [
                SRETimelineEntryResponse.model_validate(entry)
                for entry in sre_execution.timeline_entries
            ]
            
            hypotheses = [
                SREHypothesisResponse.model_validate(hypothesis)
                for hypothesis in sre_execution.hypotheses
            ]
            
            verifications = [
                SREVerificationResponse.model_validate(verification)
                for verification in sre_execution.verifications
            ]
            
            evidence = [
                SREEvidenceResponse.model_validate(item)
                for item in evidence_items
            ]
            
            provenance = [
                SREProvenanceResponse.model_validate(item)
                for item in provenance_items
            ]
            
            execution_logs = [
                IncidentExecutionLogResponse.model_validate(log)
                for log in sre_execution.logs
            ]
            
            # Create agent information from execution data
            agents = []
            if sre_execution.agent_name:
                # Determine agent status based on execution status
                agent_status = "completed" if sre_execution.status == "success" else "in_progress"
                if sre_execution.status == "failed":
                    agent_status = "error"
                
                # Calculate progress based on timeline completion
                total_timeline_steps = len(timeline_entries)
                completed_timeline_steps = len([
                    entry for entry in timeline_entries 
                    if entry.status == "completed"
                ])
                progress = (completed_timeline_steps / max(total_timeline_steps, 1)) * 100
                
                # Extract findings and recommendations from logs and hypotheses
                findings = []
                recommendations = []
                
                # Get findings from execution logs
                for log in execution_logs:
                    if log.hypothesis:
                        findings.append(log.hypothesis)
                    if log.verification:
                        findings.append(f"Verification: {log.verification}")
                
                # Get findings from hypotheses
                for hypothesis in hypotheses:
                    if hypothesis.status == "confirmed":
                        findings.append(hypothesis.hypothesis_text)
                    if hypothesis.reasoning:
                        recommendations.append(hypothesis.reasoning)
                
                # Calculate confidence from hypotheses
                hypothesis_confidences = [
                    h.confidence_score for h in hypotheses 
                    if h.confidence_score is not None
                ]
                avg_confidence = (
                    sum(hypothesis_confidences) / len(hypothesis_confidences)
                    if hypothesis_confidences else 85
                )
                
                # Determine current action
                current_action = None
                active_timeline = [
                    entry for entry in timeline_entries 
                    if entry.status == "running"
                ]
                if active_timeline:
                    current_action = active_timeline[-1].title
                elif sre_execution.status == "running":
                    current_action = "Analyzing incident and developing remediation plan"
                elif sre_execution.status == "success":
                    current_action = "Incident resolution completed"
                elif sre_execution.status == "failed":
                    current_action = "Incident resolution failed - manual intervention required"
                
                agents.append(SREExecutionAgent(
                    id=f"sre-agent-{sre_execution.id}",
                    name=sre_execution.agent_name,
                    type="SRE Agent",
                    role="Lead Investigator",
                    status=agent_status,
                    current_action=current_action,
                    progress=progress,
                    confidence=int(avg_confidence),
                    findings=findings[:5],  # Limit to top 5 findings
                    recommendations=recommendations[:3],  # Limit to top 3 recommendations
                    started_at=sre_execution.started_at,
                    completed_at=sre_execution.completed_at
                ))
            
            return SREIncidentExecutionResponse(
                id=sre_execution.id,
                incident_number=sre_execution.incident_number,
                incident_title=sre_execution.incident_title,
                incident_description=sre_execution.incident_description,
                target_ip=sre_execution.target_ip,
                priority=sre_execution.priority,
                category=sre_execution.category,
                assignment_group=sre_execution.assignment_group,
                status=sre_execution.status,
                agent_name=sre_execution.agent_name,
                started_at=sre_execution.started_at,
                completed_at=sre_execution.completed_at,
                resolution_summary=sre_execution.resolution_summary,
                final_hypothesis=sre_execution.final_hypothesis,
                resolution_steps=sre_execution.resolution_steps,
                verification_results=sre_execution.verification_results,
                timeline_entries=timeline_entries,
                hypotheses=hypotheses,
                verifications=verifications,
                evidence=evidence,
                provenance=provenance,
                execution_logs=execution_logs,
                agents=agents
            )
            
        except Exception as e:
            logger.error(f"Error fetching SRE execution for incident {incident_number}: {e}")
            return None
    
    @staticmethod
    async def get_sre_execution_summary(
        incident_number: str,
        db: AsyncSession
    ) -> SREExecutionSummary:
        """Get SRE execution summary for incident list"""
        
        try:
            result = await db.execute(
                select(SREIncidentExecution)
                .where(SREIncidentExecution.incident_number == incident_number)
            )
            
            sre_execution = result.scalar_one_or_none()
            if not sre_execution:
                return SREExecutionSummary(has_sre_execution=False)
            
            # Get timeline count for progress calculation
            timeline_result = await db.execute(
                select(SRETimelineEntry)
                .where(SRETimelineEntry.incident_execution_id == sre_execution.id)
            )
            timeline_entries = timeline_result.scalars().all()
            
            # Calculate progress
            total_steps = len(timeline_entries)
            completed_steps = len([
                entry for entry in timeline_entries 
                if entry.status == "completed"
            ])
            progress = (completed_steps / max(total_steps, 1)) * 100
            
            # Get average confidence from hypotheses
            hypothesis_result = await db.execute(
                select(SREHypothesis)
                .where(SREHypothesis.incident_execution_id == sre_execution.id)
            )
            hypotheses = hypothesis_result.scalars().all()
            
            confidences = [
                h.confidence_score for h in hypotheses 
                if h.confidence_score is not None
            ]
            avg_confidence = (
                sum(confidences) / len(confidences)
                if confidences else None
            )
            
            # Get current action from active timeline
            current_action = None
            active_timeline = [
                entry for entry in timeline_entries 
                if entry.status == "running"
            ]
            if active_timeline:
                current_action = active_timeline[-1].title
            elif sre_execution.status == "running":
                current_action = "Analyzing incident"
            
            return SREExecutionSummary(
                has_sre_execution=True,
                execution_status=sre_execution.status,
                agent_count=1,  # Currently one SRE agent per incident
                progress=progress,
                confidence=int(avg_confidence) if avg_confidence else None,
                current_action=current_action,
                started_at=sre_execution.started_at
            )
            
        except Exception as e:
            logger.error(f"Error fetching SRE execution summary for incident {incident_number}: {e}")
            return SREExecutionSummary(has_sre_execution=False)
    
    @staticmethod 
    async def list_recent_sre_executions(
        db: AsyncSession,
        limit: int = 10
    ) -> List[SREIncidentExecutionResponse]:
        """List recent SRE executions"""
        
        try:
            result = await db.execute(
                select(SREIncidentExecution)
                .options(
                    selectinload(SREIncidentExecution.timeline_entries),
                    selectinload(SREIncidentExecution.hypotheses),
                    selectinload(SREIncidentExecution.verifications),
                    selectinload(SREIncidentExecution.logs)
                )
                .order_by(SREIncidentExecution.started_at.desc())
                .limit(limit)
            )
            
            executions = result.scalars().all()
            responses = []
            
            for execution in executions:
                # Convert each execution to response format
                execution_response = await SREExecutionService.get_sre_execution_by_incident_number(
                    execution.incident_number, db
                )
                if execution_response:
                    responses.append(execution_response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Error listing recent SRE executions: {e}")
            return []