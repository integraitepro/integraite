"""
Templated SRE Agent System using LangGraph and Database Configuration
"""

import os
import asyncio
import json
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import paramiko
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.database import get_db
from app.models.agent_execution import (
    Agent, AgentExecution, AgentTimelineEntry, 
    AgentHypothesis, AgentVerification, AgentEvidence, AgentProvenance
)
from app.models.incident import Incident


class DatabaseSREAgent:
    """Database-configured SRE Agent powered by LangGraph"""
    
    def __init__(self, agent_id: int, db: AsyncSession):
        self.agent_id = agent_id
        self.db = db
        self.agent_config = None
        self.current_execution = None
        self.step_counter = 0
        
        # Initialize after loading config
        self.llm = None
        self.tools = []
        self.workflow = None
        
    async def initialize(self):
        """Load agent configuration from database"""
        result = await self.db.execute(select(Agent).where(Agent.id == self.agent_id))
        self.agent_config = result.scalar_one_or_none()
        
        if not self.agent_config:
            raise ValueError(f"Agent {self.agent_id} not found")
        
        # Initialize OpenAI LLM with environment or agent config
        openai_key = self.agent_config.environment_variables.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found in agent config or environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=openai_key
        )
        
        # Create tools
        self.tools = [self._create_ssh_tool()]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create workflow
        self.workflow = self._create_workflow()
        
    def _create_ssh_tool(self):
        """Create SSH tool with agent's configuration"""
        agent_config = self.agent_config
        
        @tool
        async def execute_ssh_command(ip_address: str, command: str) -> str:
            """
            Execute a command on a remote server via SSH using agent configuration.
            
            Args:
                ip_address: The IP address of the target server
                command: The shell command to execute
            
            Returns:
                Combined stdout and stderr output as a string
            """
            return await self._execute_ssh_command_impl(ip_address, command)
        
        return execute_ssh_command
    
    async def _execute_ssh_command_impl(self, ip_address: str, command: str) -> str:
        """Implementation of SSH command execution"""
        try:
            # Get SSH configuration
            ssh_config = self.agent_config.configuration.get('ssh', {})
            username = ssh_config.get('username')
            key_data = ssh_config.get('private_key')  # Base64 encoded key
            port = ssh_config.get('port', 22)
            
            if not username or not key_data:
                return "ERROR: SSH configuration incomplete in agent settings"
            
            # Create temporary key file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as key_file:
                import base64
                key_content = base64.b64decode(key_data).decode('utf-8')
                key_file.write(key_content)
                key_file_path = key_file.name
            
            try:
                # Set correct permissions
                os.chmod(key_file_path, 0o600)
                
                # Create SSH client
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Connect to the server
                client.connect(
                    hostname=ip_address,
                    username=username,
                    key_filename=key_file_path,
                    port=port,
                    timeout=30
                )
                
                # Record the command in timeline
                await self._add_timeline_entry(
                    action_type="command",
                    title=f"Executing SSH command on {ip_address}",
                    description=f"Running: {command}",
                    command=command,
                    target_host=ip_address
                )
                
                # Execute the command
                start_time = datetime.now()
                stdin, stdout, stderr = client.exec_command(command)
                
                # Get outputs
                stdout_output = stdout.read().decode('utf-8')
                stderr_output = stderr.read().decode('utf-8')
                exit_code = stdout.channel.recv_exit_status()
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Update timeline entry with results
                await self._update_latest_timeline_entry(
                    success=exit_code == 0,
                    stdout=stdout_output,
                    stderr=stderr_output,
                    exit_code=exit_code,
                    duration_ms=duration_ms
                )
                
                # Combine outputs
                result = ""
                if stdout_output:
                    result += f"STDOUT:\n{stdout_output}\n"
                if stderr_output:
                    result += f"STDERR:\n{stderr_output}\n"
                result += f"EXIT_STATUS: {exit_code}"
                
                return result if result else "Command executed successfully (no output)"
                
            finally:
                client.close()
                os.unlink(key_file_path)  # Clean up temp file
                
        except Exception as e:
            # Record error in timeline
            await self._update_latest_timeline_entry(
                success=False,
                stderr=str(e),
                exit_code=-1
            )
            return f"ERROR: {str(e)}"
    
    async def _add_timeline_entry(self, action_type: str, title: str, description: str = None, 
                                command: str = None, target_host: str = None) -> AgentTimelineEntry:
        """Add a new timeline entry"""
        self.step_counter += 1
        
        entry = AgentTimelineEntry(
            execution_id=self.current_execution.id,
            step_number=self.step_counter,
            action_type=action_type,
            title=title,
            description=description,
            command=command,
            target_host=target_host,
            timestamp=datetime.now(timezone.utc)
        )
        
        self.db.add(entry)
        await self.db.commit()
        return entry
    
    async def _update_latest_timeline_entry(self, **kwargs):
        """Update the most recent timeline entry"""
        if hasattr(self, '_latest_entry_id'):
            result = await self.db.execute(
                select(AgentTimelineEntry).where(
                    AgentTimelineEntry.execution_id == self.current_execution.id,
                    AgentTimelineEntry.step_number == self.step_counter
                )
            )
            entry = result.scalar_one_or_none()
            if entry:
                for key, value in kwargs.items():
                    setattr(entry, key, value)
                await self.db.commit()
    
    async def _add_hypothesis(self, hypothesis_text: str, confidence_score: float, 
                            category: str = None) -> AgentHypothesis:
        """Add a new hypothesis"""
        hypothesis = AgentHypothesis(
            execution_id=self.current_execution.id,
            hypothesis_text=hypothesis_text,
            confidence_score=confidence_score,
            category=category,
            status="proposed"
        )
        
        self.db.add(hypothesis)
        await self.db.commit()
        return hypothesis
    
    async def _add_verification(self, verification_type: str, title: str, 
                              expected_result: str = None) -> AgentVerification:
        """Add a verification step"""
        verification = AgentVerification(
            execution_id=self.current_execution.id,
            verification_type=verification_type,
            title=title,
            expected_result=expected_result,
            status="pending",
            started_at=datetime.now(timezone.utc)
        )
        
        self.db.add(verification)
        await self.db.commit()
        return verification
    
    async def _add_evidence(self, evidence_type: str, title: str, content: str, 
                          source: str = None, relevance_score: float = 0.5) -> AgentEvidence:
        """Add evidence collected during execution"""
        evidence = AgentEvidence(
            execution_id=self.current_execution.id,
            evidence_type=evidence_type,
            title=title,
            content=content,
            source=source,
            relevance_score=relevance_score
        )
        
        self.db.add(evidence)
        await self.db.commit()
        return evidence
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on agent configuration"""
        agent_type = self.agent_config.agent_type
        capabilities = self.agent_config.capabilities or []
        
        base_prompt = f"""You are an expert {agent_type.upper()} autonomous agent named "{self.agent_config.name}".
{self.agent_config.description}

Your capabilities include: {', '.join(capabilities)}

CRITICAL INSTRUCTIONS:
1. You will be given an incident description.
2. Analyze the incident and identify target machine(s) from the incident details or ask for clarification.
3. Use the execute_ssh_command tool to run diagnostic commands one at a time.
4. Based on command outputs, form hypotheses about the root cause.
5. Test your hypotheses with additional commands.
6. Once you identify the root cause, execute remediation commands.
7. Verify the fix by running validation commands.
8. Provide a comprehensive summary of findings, actions taken, and results.

WORKFLOW:
- Start with diagnostic commands (systemctl status, ps aux, df -h, etc.)
- Analyze outputs to understand the problem
- Form and test hypotheses
- Apply fixes based on confirmed root cause
- Verify the resolution
- Document everything clearly

Execute ONE command at a time and wait for results before proceeding."""

        return base_prompt
    
    async def agent_node(self, state: MessagesState) -> Dict[str, Any]:
        """Agent node that processes messages and decides on actions"""
        messages = state["messages"]
        
        # Add system prompt if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            system_message = SystemMessage(content=self._get_system_prompt())
            messages = [system_message] + messages
        
        # Call the LLM with tools
        response = self.llm_with_tools.invoke(messages)
        
        # Log agent decision
        await self._add_timeline_entry(
            action_type="analysis",
            title="Agent Decision",
            description=str(response.content)[:500] + "..." if len(str(response.content)) > 500 else str(response.content)
        )
        
        return {"messages": [response]}
    
    async def executor_node(self, state: MessagesState) -> Dict[str, Any]:
        """Executor node that runs tools"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Execute tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_responses = []
            
            for tool_call in last_message.tool_calls:
                if tool_call['name'] == 'execute_ssh_command':
                    result = await self._execute_ssh_command_impl(
                        tool_call['args']['ip_address'],
                        tool_call['args']['command']
                    )
                    
                    # Create tool response message
                    from langchain_core.messages import ToolMessage
                    tool_response = ToolMessage(
                        content=result,
                        tool_call_id=tool_call['id']
                    )
                    tool_responses.append(tool_response)
        
        return {"messages": tool_responses}
    
    def should_continue(self, state: MessagesState) -> str:
        """Determine if we should continue or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, go to executor
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "executor"
        
        # Check if agent is indicating completion
        content = str(last_message.content).lower()
        completion_indicators = [
            "incident resolved", "resolution completed", "task completed",
            "fix verified", "problem solved", "issue resolved"
        ]
        
        if any(indicator in content for indicator in completion_indicators):
            return "end"
        
        # Continue if we haven't reached max steps
        if self.step_counter < 20:  # Safety limit
            return "agent"
        else:
            return "end"
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("executor", self.executor_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "executor": "executor",
                "agent": "agent",
                "end": "__end__"
            }
        )
        
        # Add edge from executor back to agent
        workflow.add_edge("executor", "agent")
        
        return workflow.compile()
    
    async def create_execution(self, incident_id: Optional[int] = None, 
                             trigger_type: str = "manual", 
                             triggered_by: Optional[int] = None,
                             input_data: Dict[str, Any] = None) -> AgentExecution:
        """Create a new agent execution"""
        execution = AgentExecution(
            agent_id=self.agent_id,
            incident_id=incident_id,
            organization_id=self.agent_config.organization_id,
            execution_id=str(uuid.uuid4()),
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            status="running",
            input_data=input_data or {},
            started_at=datetime.now(timezone.utc)
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        self.current_execution = execution
        return execution
    
    async def execute_incident_resolution(self, incident_description: str, 
                                        incident_id: Optional[int] = None,
                                        triggered_by: Optional[int] = None) -> AgentExecution:
        """Execute incident resolution workflow"""
        try:
            # Create execution record
            execution = await self.create_execution(
                incident_id=incident_id,
                trigger_type="incident",
                triggered_by=triggered_by,
                input_data={"incident_description": incident_description}
            )
            
            # Add initial timeline entry
            await self._add_timeline_entry(
                action_type="start",
                title="Agent Execution Started",
                description=f"Beginning incident resolution for: {incident_description[:100]}..."
            )
            
            # Create initial input
            initial_input = {
                "messages": [HumanMessage(content=incident_description)]
            }
            
            # Execute the workflow
            step_count = 0
            final_messages = []
            
            async for event in self.workflow.astream(initial_input):
                step_count += 1
                
                if "messages" in event:
                    final_messages = event["messages"]
                
                # Update execution progress
                execution.progress_percentage = min(step_count * 5, 95)  # Max 95% until completion
                await self.db.commit()
                
                # Safety limit
                if step_count > 50:
                    break
            
            # Mark execution as completed
            execution.status = "completed"
            execution.final_status = "success"
            execution.completed_at = datetime.now(timezone.utc)
            execution.progress_percentage = 100
            
            # Extract summary from final messages
            if final_messages:
                last_message = final_messages[-1]
                execution.summary = str(last_message.content)[:1000]
            
            # Calculate duration
            if execution.started_at and execution.completed_at:
                duration = execution.completed_at - execution.started_at
                execution.duration_seconds = int(duration.total_seconds())
            
            await self.db.commit()
            
            # Add completion timeline entry
            await self._add_timeline_entry(
                action_type="completion",
                title="Agent Execution Completed",
                description=f"Incident resolution completed in {step_count} steps"
            )
            
            return execution
            
        except Exception as e:
            # Mark execution as failed
            if self.current_execution:
                self.current_execution.status = "failed"
                self.current_execution.final_status = "failure"
                self.current_execution.error_message = str(e)
                self.current_execution.completed_at = datetime.now(timezone.utc)
                await self.db.commit()
            
            raise e


async def execute_agent_for_incident(agent_id: int, incident_id: int, 
                                   triggered_by: int, db: AsyncSession) -> AgentExecution:
    """Execute an agent for a specific incident"""
    # Get incident details
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise ValueError(f"Incident {incident_id} not found")
    
    # Create agent instance
    agent = DatabaseSREAgent(agent_id, db)
    await agent.initialize()
    
    # Build incident description
    incident_description = f"""
Incident Details:
- ID: {incident.source_alert_id or f"INC-{incident.id}"}
- Title: {incident.title}
- Description: {incident.description}
- Severity: {incident.severity}
- Status: {incident.status}
- Category: {incident.category or 'N/A'}
- Affected Services: {', '.join(incident.affected_services or ['N/A'])}
- Detection Time: {incident.detection_time}

Please investigate and resolve this incident.
"""
    
    # Execute the agent
    return await agent.execute_incident_resolution(
        incident_description=incident_description,
        incident_id=incident_id,
        triggered_by=triggered_by
    )