"""
Self-Healing SRE Agent with database integration for real-time tracking
"""

import asyncio
import json
import logging
import os
import paramiko
import random
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings

# Import SSH configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from ssh_config import LLMIntelligentSSHConfig
except ImportError:
    # Fallback if ssh_config.py is not available
    class LLMIntelligentSSHConfig:
        def __init__(self, api_key): pass
        async def analyze_incident_with_llm(self, data): return {}
        async def generate_diagnostic_commands_with_llm(self, data, analysis): return ["uptime"]
        async def generate_remediation_commands_with_llm(self, data, analysis, results): return []
        async def generate_verification_commands_with_llm(self, data, analysis, commands): return ["uptime"]
        async def assess_verification_results_with_llm(self, data, results): return {"incident_resolved": False}
from app.core.database import get_db
from app.models.sre_execution import (
    SREIncidentExecution, IncidentExecutionLog, SRETimelineEntry,
    SREHypothesis, SREVerification, SREEvidence, SREProvenance
)

logger = logging.getLogger(__name__)


class SREAgentState:
    """State management for the SRE agent workflow"""
    
    def __init__(self):
        self.incident_number: str = ""
        self.incident_title: str = ""
        self.incident_description: str = ""
        self.target_ip: str = ""
        self.priority: str = ""
        self.category: str = ""
        self.assignment_group: str = ""
        
        self.execution_id: int = 0
        self.step_number: int = 0
        self.current_hypothesis: str = ""
        self.evidence_collected: List[Dict[str, Any]] = []
        self.commands_executed: List[Dict[str, Any]] = []
        self.verification_results: List[Dict[str, Any]] = []
        
        # LLM-powered intelligent analysis results
        self.llm_incident_analysis: Dict[str, Any] = {}
        self.detected_services: List[str] = []
        self.detected_technologies: List[str] = []
        self.detected_issue_types: List[str] = []
        self.severity_assessment: str = ""
        self.likely_root_causes: List[str] = []
        
        # LLM-generated commands
        self.generated_diagnostic_commands: List[str] = []
        self.generated_remediation_commands: List[str] = []
        self.generated_verification_commands: List[str] = []
        self.llm_verification_assessment: Dict[str, Any] = {}
        
        self.status: str = "initiated"
        self.resolution_summary: str = ""
        self.final_conclusion: str = ""
        
        # SSH connection details from settings
        self.ssh_username: str = settings.SSH_USERNAME
        self.ssh_key_path: Optional[str] = settings.SSH_PRIVATE_KEY_PATH
        self.ssh_port: int = settings.SSH_PORT
        self.ssh_timeout: int = settings.SSH_TIMEOUT



#!/usr/bin/env python3
"""
Self-Healing SRE Agent using LangGraph and Paramiko

This agent resolves IT incidents by connecting to EC2 instances via SSH
and executing diagnostic and remediation commands on the fly.
"""

import os
import paramiko
import requests
import json
import datetime
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage


class IncidentLogger:
    """Handles logging of incident resolution steps with JSON persistence"""
    
    def __init__(self, log_file_path: str = "app/api/v1/endpoints/incident_logs.json", verbose_logging: bool = False):
        self.log_file_path = log_file_path
        self.verbose_logging = verbose_logging
        self.current_incident_id = None
        self.current_session_logs = []
        
    def extract_incident_id(self, incident_description: str) -> str:
        """Extract incident ID from incident description"""
        # Look for patterns like INC0010031, INC10001, P1-2024-001, etc.
        patterns = [
            r'(INC\d+)',  # INC followed by numbers
            r'(P\d+-\d+-\d+)',  # P1-2024-001 format
            r'(INCIDENT[-_]?\d+)',  # INCIDENT123 or INCIDENT-123
            r'(TKT\d+)',  # TKT12345
        ]
        
        for pattern in patterns:
            match = re.search(pattern, incident_description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # If no pattern matches, create a timestamp-based ID
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"AUTO_{timestamp}"
    
    def start_incident_logging(self, incident_description: str):
        """Initialize logging for a new incident"""
        self.current_incident_id = self.extract_incident_id(incident_description)
        self.current_session_logs = []
        
        # Log the initial incident and save immediately
        self.log_step("INCIDENT_RECEIVED", {
            "incident_description": incident_description,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "STARTED"
        })
        
        print(f"🚀 Started logging for incident: {self.current_incident_id}")
    
    def log_step(self, step_type: str, data: Dict[str, Any]):
        """Log a step in the incident resolution process"""
        if not self.current_incident_id:
            return
            
        log_entry = {
            "step_number": len(self.current_session_logs) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": step_type,
            "data": data
        }
        
        self.current_session_logs.append(log_entry)
        
        # Save to file immediately after each step for persistence
        self._save_to_file()
        
        # Optional: Print step for debugging (only if verbose logging is enabled)
        if self.verbose_logging:
            print(f"📝 Logged Step {log_entry['step_number']}: {step_type}")
    
    def log_agent_message(self, message: str):
        """Log agent thinking/response"""
        self.log_step("AGENT_RESPONSE", {
            "message": message,
            "type": "agent_thinking"
        })
    
    def log_tool_call(self, tool_name: str, args: Dict[str, Any]):
        """Log tool execution"""
        self.log_step("TOOL_CALL", {
            "tool_name": tool_name,
            "arguments": args,
            "type": "tool_execution"
        })
    
    def log_tool_result(self, tool_name: str, result: str):
        """Log tool execution result"""
        self.log_step("TOOL_RESULT", {
            "tool_name": tool_name,
            "result": result,
            "type": "tool_output"
        })
    
    def log_incident_completion(self, status: str, summary: str):
        """Log incident completion"""
        self.log_step("INCIDENT_COMPLETED", {
            "status": status,
            "summary": summary,
            "total_steps": len(self.current_session_logs),
            "duration_seconds": self._calculate_duration()
        })
    
    def _calculate_duration(self) -> float:
        """Calculate incident resolution duration"""
        if len(self.current_session_logs) < 2:
            return 0
        
        start_time = datetime.datetime.fromisoformat(self.current_session_logs[0]["timestamp"])
        end_time = datetime.datetime.fromisoformat(self.current_session_logs[-1]["timestamp"])
        return (end_time - start_time).total_seconds()
    
    def _save_to_file(self):
        """Save logs to JSON file using array structure (called after each step)"""
        try:
            # Load existing logs (array format)
            existing_logs = []
            if os.path.exists(self.log_file_path):
                try:
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Handle both old format (dict) and new format (array)
                        if isinstance(data, dict):
                            # Convert old format to new array format
                            existing_logs = list(data.values())
                        elif isinstance(data, list):
                            existing_logs = data
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_logs = []
                except PermissionError:
                    print(f"Warning: Cannot access {self.log_file_path} - permission denied")
                    return
            
            # Find if current incident already exists in logs
            incident_exists = False
            current_incident_data = {
                "incident_id": self.current_incident_id,
                "start_time": self.current_session_logs[0]["timestamp"] if self.current_session_logs else datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "step_count": len(self.current_session_logs),
                "duration_seconds": self._calculate_duration(),
                "status": self._get_current_status(),
                "logs": self.current_session_logs
            }
            
            # Update existing incident or add new one
            for i, incident in enumerate(existing_logs):
                if incident.get("incident_id") == self.current_incident_id:
                    existing_logs[i] = current_incident_data
                    incident_exists = True
                    break
            
            if not incident_exists:
                existing_logs.append(current_incident_data)
            
            # Save back to file with atomic write (write to temp file then rename)
            temp_file = f"{self.log_file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)
            
            # Atomic rename to avoid corruption
            if os.path.exists(temp_file):
                if os.path.exists(self.log_file_path):
                    os.remove(self.log_file_path)
                os.rename(temp_file, self.log_file_path)
                
        except Exception as e:
            print(f"Warning: Failed to save logs to {self.log_file_path}: {e}")
            # Try to clean up temp file if it exists
            temp_file = f"{self.log_file_path}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def _get_current_status(self) -> str:
        """Get current incident status based on logs"""
        if not self.current_session_logs:
            return "STARTED"
        
        last_log = self.current_session_logs[-1]
        if last_log.get("step_type") == "INCIDENT_COMPLETED":
            return last_log.get("data", {}).get("status", "COMPLETED")
        else:
            return "IN_PROGRESS"
    
    def get_incident_summary(self) -> Dict[str, Any]:
        """Get summary of current incident resolution"""
        if not self.current_incident_id or not self.current_session_logs:
            return {}
        
        return {
            "incident_id": self.current_incident_id,
            "total_steps": len(self.current_session_logs),
            "duration_seconds": self._calculate_duration(),
            "start_time": self.current_session_logs[0]["timestamp"] if self.current_session_logs else None,
            "end_time": self.current_session_logs[-1]["timestamp"] if self.current_session_logs else None,
            "log_file": self.log_file_path
        }


@tool
def execute_ssh_command(ip_address: str, command: str) -> str:
    """
    Execute a command on a remote server via SSH.
    
    Args:
        ip_address: The IP address of the target server
        command: The shell command to execute
    
    Returns:
        Combined stdout and stderr output as a string
    """
    # Load credentials from settings
    ssh_username = settings.SSH_USERNAME
    ssh_key_path = settings.SSH_PRIVATE_KEY_PATH
    
    if not ssh_username or not ssh_key_path:
        return "ERROR: SSH_USERNAME or SSH_PRIVATE_KEY_PATH not configured in environment"
    
    # Expand user path for SSH key
    ssh_key_path = os.path.expanduser(ssh_key_path)
    
    if not os.path.exists(ssh_key_path):
        return f"ERROR: SSH key file not found at {ssh_key_path}"
    
    client = None
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the server
        client.connect(
            hostname=ip_address,
            username=ssh_username,
            key_filename=ssh_key_path,
            timeout=30
        )
        
        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        
        # Get both stdout and stderr
        stdout_output = stdout.read().decode('utf-8')
        stderr_output = stderr.read().decode('utf-8')
        
        # Get exit status
        exit_status = stdout.channel.recv_exit_status()
        
        # Combine outputs
        result = ""
        if stdout_output:
            result += f"STDOUT:\n{stdout_output}\n"
        if stderr_output:
            result += f"STDERR:\n{stderr_output}\n"
        result += f"EXIT_STATUS: {exit_status}"
        
        return result if result else "Command executed successfully (no output)"
        
    except paramiko.AuthenticationException:
        return f"ERROR: Authentication failed for {ssh_username}@{ip_address}"
    except paramiko.SSHException as e:
        return f"ERROR: SSH connection failed: {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected error: {str(e)}"
    finally:
        if client:
            client.close()


@tool
def close_servicenow_incident(incident_number: str, resolution_summary: str, close_code: str = "Resolved by caller") -> str:
    """
    Close a ServiceNow incident with resolution details.
    
    Args:
        incident_number: The ServiceNow incident number (e.g., INC0010001)
        resolution_summary: Summary of what was done to resolve the incident
        close_code: The resolution code for ServiceNow (default: "Resolved by caller")
                   Common values: "Resolved by caller", "Solved (Workaround)", "Not Solved (Not Reproducible)"
    
    Returns:
        Confirmation of incident closure with ServiceNow response
    """
    # Load ServiceNow credentials from settings
    snow_instance = settings.SERVICENOW_INSTANCE_URL  # e.g., "https://yourcompany.service-now.com"
    snow_username = settings.SERVICENOW_USERNAME
    snow_password = settings.SERVICENOW_PASSWORD

    # print("snow instance:", snow_instance)
    # print("snow username:", snow_username)
    # print("snow password:", snow_password)
    
    if not all([snow_instance, snow_username, snow_password]):
        return "ERROR: ServiceNow credentials not configured. Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD in environment"
    
    try:
        # ServiceNow REST API endpoint for incidents
        url = f"{snow_instance}/api/now/table/incident"
        
        # Headers for ServiceNow API
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Authentication
        auth = (snow_username, snow_password)
        
        # First, find the incident by number
        search_params = {
            "sysparm_query": f"number={incident_number}",
            "sysparm_fields": "sys_id,number,state,short_description"
        }
        
        response = requests.get(url, headers=headers, auth=auth, params=search_params)
        
        if response.status_code != 200:
            return f"ERROR: Failed to find incident {incident_number}. HTTP {response.status_code}: {response.text}"
        
        incidents = response.json().get('result', [])
        if not incidents:
            return f"ERROR: Incident {incident_number} not found in ServiceNow"
        
        incident = incidents[0]
        incident_sys_id = incident['sys_id']
        
        # Get current incident state to understand available fields
        current_state = incident.get('state', 'unknown')
        
        # Prepare update data to close the incident
        # Try multiple field name variations that ServiceNow might use
        update_data = {
            "state": "6",  # ServiceNow state 6 = Resolved
            "close_notes": resolution_summary,
            "resolved_by": snow_username,
            "resolved_at": "javascript:gs.nowDateTime()",
            "work_notes": f"Incident resolved by SRE Agent: {resolution_summary}"
        }
        
        # Add resolution code with different possible field names
        resolution_fields = ["resolution_code", "close_code", "u_resolution_code", "resolution"]
        for field in resolution_fields:
            update_data[field] = close_code
        
        # Update the incident
        update_url = f"{url}/{incident_sys_id}"
        update_response = requests.put(
            update_url, 
            headers=headers, 
            auth=auth, 
            data=json.dumps(update_data)
        )
        
        if update_response.status_code == 200:
            updated_incident = update_response.json().get('result', {})
            return f"""
✅ SERVICENOW INCIDENT CLOSED SUCCESSFULLY

Incident Number: {incident_number}
Incident Sys ID: {incident_sys_id}
Status: RESOLVED (State 6)
Resolution Code: {close_code}
Resolved By: {snow_username}

RESOLUTION SUMMARY:
{resolution_summary}

ServiceNow Response: Incident successfully updated and closed.
"""
        else:
            error_details = update_response.text
            try:
                error_json = update_response.json()
                if 'error' in error_json:
                    error_details = f"ServiceNow Error: {error_json['error'].get('message', error_json['error'])}"
                    if 'detail' in error_json['error']:
                        error_details += f"\nDetails: {error_json['error']['detail']}"
            except:
                pass
            
            return f"""ERROR: Failed to close incident {incident_number}. 
HTTP {update_response.status_code}: {error_details}

Possible solutions:
1. Check if 'resolution_code' field exists in your ServiceNow instance
2. Verify the resolution code value '{close_code}' is valid
3. Check if additional mandatory fields are required for closure
4. Ensure the user has permissions to close incidents

You may need to check your ServiceNow instance configuration for required closure fields."""
            
    except requests.exceptions.RequestException as e:
        return f"ERROR: Network error connecting to ServiceNow: {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected error closing incident: {str(e)}"


@tool
def close_incident(incident_id: str, resolution_summary: str) -> str:
    """
    Close an incident ticket with resolution details.
    
    Args:
        incident_id: The incident ID (e.g., INC10001, P1-2024-001)
        resolution_summary: Summary of what was done to resolve the incident
    
    Returns:
        Confirmation of incident closure
    """
    try:
        # In a real implementation, this would integrate with your ITSM system
        # (ServiceNow, Jira Service Management, PagerDuty, etc.)
        
        # For now, we'll simulate the incident closure
        closure_time = "2025-10-31 " + __import__('datetime').datetime.now().strftime("%H:%M:%S") + " UTC"
        
        closure_record = f"""
INCIDENT CLOSURE REPORT
======================
Incident ID: {incident_id}
Status: RESOLVED - CLOSED
Resolution Time: {closure_time}
Resolved By: SRE Autonomous Agent

RESOLUTION SUMMARY:
{resolution_summary}

INCIDENT LIFECYCLE:
- Incident Created: Auto-detected by monitoring
- Incident Assigned: SRE Autonomous Agent
- Investigation: Automated SSH diagnostics
- Resolution: Automated remediation
- Verification: Service health confirmed
- Status: CLOSED

This incident has been automatically resolved and closed by the SRE Agent.
No further action required.
        """
        
        # Log the closure (in production, this would go to your ITSM system)
        print(f"\n🎯 INCIDENT CLOSURE INITIATED")
        print(f"📋 Incident ID: {incident_id}")
        print(f"⏰ Closure Time: {closure_time}")
        print(f"✅ Status: RESOLVED - CLOSED")
        
        return f"SUCCESS: Incident {incident_id} has been successfully closed. Resolution logged in ITSM system."
        
    except Exception as e:
        return f"ERROR: Failed to close incident {incident_id}: {str(e)}"


class SREAgent:
    """Self-Healing SRE Agent powered by LangGraph"""
    
    def __init__(self, log_file_path: str = "app/api/v1/endpoints/incident_logs.json", verbose_logging: bool = False):
        # Initialize incident logger
        self.logger = IncidentLogger(log_file_path, verbose_logging)
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Bind tools to the LLM
        self.tools = [execute_ssh_command, close_servicenow_incident]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create tool node
        self.tool_node = ToolNode(self.tools)
        
        # System prompt for the agent
        self.system_prompt = """You are an expert SRE (Site Reliability Engineer) autonomous agent. 
Your sole purpose is to resolve IT incidents.

You will be given an incident description from a user.
1. First, analyze the incident to understand the problem and identify the target machine (e.g., IP address).
2. You have two tools: `execute_ssh_command` and `close_servicenow_incident`.
3. You MUST use the SSH tool to run diagnostic commands (like `systemctl status`, `grep logs`, `df -h`).
4. Based on the command output (both stdout and stderr), you must determine the root cause.
5. Then, you must generate and execute *new* commands to *fix* the problem (e.g., `systemctl start <service>`).
6. Finally, you must *verify* the fix by running another diagnostic command.
7. Generate *one command at a time*. Do not try to run multiple commands in one tool call.
8. If a command fails, read the stderr output and try to formulate a new, corrected command.
9. Once you have verified the fix is successful, you MUST use `close_servicenow_incident` to close the incident ticket.
10. When closing the incident, extract the incident ID from the original incident description and provide a comprehensive resolution summary.
Your final answer should be a report of what you found, what you did, the verified outcome, and confirmation of incident closure."""

    def agent_node(self, state: MessagesState) -> Dict[str, Any]:
        """
        Agent node that processes messages and decides on actions
        """
        messages = state["messages"]
        
        # Add system prompt as the first message if not present
        if not messages or not any(isinstance(msg, AIMessage) and "SRE" in str(msg.content) for msg in messages):
            system_message = AIMessage(content=self.system_prompt)
            messages = [system_message] + messages
        
        # Call the LLM with tools
        response = self.llm_with_tools.invoke(messages)
        
        # Log agent response
        if hasattr(response, 'content') and response.content:
            self.logger.log_agent_message(response.content)
        
        # Log tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                self.logger.log_tool_call(tool_call['name'], tool_call['args'])
        
        return {"messages": [response]}

    def executor_node(self, state: MessagesState) -> Dict[str, Any]:
        """
        Executor node that runs tools
        """
        # Use the tool node to execute tools
        result = self.tool_node.invoke(state)
        
        # Log tool results
        if 'messages' in result:
            for message in result['messages']:
                if hasattr(message, 'content') and message.content:
                    # Extract tool name from the message if possible
                    tool_name = "unknown_tool"
                    if hasattr(message, 'name'):
                        tool_name = message.name
                    
                    self.logger.log_tool_result(tool_name, str(message.content))
        
        return result

    def should_continue(self, state: MessagesState) -> str:
        """
        Conditional function to determine if we should continue or end
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, go to executor
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "executor"
        else:
            return "end"

    def create_workflow(self) -> StateGraph:
        """
        Create and configure the LangGraph workflow
        """
        # Create the graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("executor", self.executor_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edge from agent
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "executor": "executor",
                "end": "__end__"
            }
        )
        
        # Add edge from executor back to agent
        workflow.add_edge("executor", "agent")
        
        return workflow.compile()
