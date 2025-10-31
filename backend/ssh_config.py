# SRE Agent LLM-Powered Intelligence Configuration
# This file contains LLM-powered intelligent analysis and command generation

from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)

class LLMIntelligentSSHConfig:
    """
    LLM-powered intelligent SSH configuration that uses AI reasoning
    to detect services, generate diagnostic commands, and create remediation strategies
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize with OpenAI API key"""
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4",
            temperature=0.1  # Low temperature for consistent, reliable outputs
        )
    
    async def analyze_incident_with_llm(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to comprehensively analyze the incident and extract intelligence
        """
        incident_description = f"{incident_data.get('title', '')} {incident_data.get('description', '')}"
        
        analysis_prompt = f"""
        You are an expert SRE engineer analyzing a production incident. Based on the incident information below, provide a comprehensive analysis in JSON format.

        Incident Information:
        - Title: {incident_data.get('title', 'N/A')}
        - Description: {incident_data.get('description', 'N/A')}
        - Priority: {incident_data.get('priority', 'N/A')}
        - Category: {incident_data.get('category', 'N/A')}
        - Target IP: {incident_data.get('target_ip', 'N/A')}
        - Target Hostname: {incident_data.get('target', {}).get('hostname', 'N/A')}

        Analyze this incident and respond with a JSON object containing:
        
        {{
            "detected_services": ["list", "of", "likely", "affected", "services"],
            "detected_technologies": ["list", "of", "technologies", "involved"],
            "issue_types": ["list", "of", "issue", "categories"],
            "severity_assessment": "critical|high|medium|low",
            "likely_root_causes": ["list", "of", "potential", "root", "causes"],
            "impact_assessment": "description of likely impact",
            "urgency_level": "immediate|urgent|normal|low"
        }}

        Consider these common services: nginx, apache, docker, kubernetes, postgresql, mysql, redis, mongodb, elasticsearch, rabbitmq, kafka, nodejs, python, java, php, ssl/tls, dns, load balancer, cdn, monitoring systems.

        Consider these issue types: service_down, performance_degradation, high_memory_usage, high_cpu_usage, disk_space_full, network_connectivity, ssl_certificate_issues, database_connection_issues, authentication_failures, security_incidents, configuration_errors.

        Be specific and accurate in your analysis. Only include services and issues that are clearly indicated by the incident description.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert SRE engineer with deep knowledge of production systems, infrastructure, and incident analysis. Provide accurate, actionable analysis."),
                HumanMessage(content=analysis_prompt)
            ])
            
            # Parse JSON response
            analysis_result = json.loads(response.content)
            logger.info(f"LLM incident analysis completed: {analysis_result}")
            return analysis_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM analysis response: {e}")
            # Fallback to basic analysis
            return {
                "detected_services": ["unknown"],
                "detected_technologies": [],
                "issue_types": ["unknown"],
                "severity_assessment": "medium",
                "likely_root_causes": ["requires investigation"],
                "impact_assessment": "unknown impact",
                "urgency_level": "normal"
            }
        except Exception as e:
            logger.error(f"LLM incident analysis failed: {e}")
            return {}
    
    async def generate_diagnostic_commands_with_llm(self, incident_data: Dict[str, Any], 
                                                   analysis_result: Dict[str, Any]) -> List[str]:
        """
        Use LLM to generate intelligent diagnostic commands based on incident analysis
        """
        
        diagnostic_prompt = f"""
        You are an expert SRE engineer creating diagnostic commands for a production incident. Based on the incident analysis below, generate a comprehensive list of diagnostic commands.

        Incident Details:
        - Title: {incident_data.get('title', 'N/A')}
        - Description: {incident_data.get('description', 'N/A')}
        - Target IP: {incident_data.get('target_ip', 'N/A')}
        
        Analysis Results:
        - Detected Services: {analysis_result.get('detected_services', [])}
        - Technologies: {analysis_result.get('detected_technologies', [])}
        - Issue Types: {analysis_result.get('issue_types', [])}
        - Likely Root Causes: {analysis_result.get('likely_root_causes', [])}

        Generate Linux diagnostic commands that will help investigate this specific incident. Consider:
        1. Service-specific diagnostics for the detected services
        2. System-level diagnostics for the identified issue types
        3. Network and connectivity checks if relevant
        4. Log analysis commands for the affected services
        5. Resource monitoring commands (CPU, memory, disk, network)

        Provide your response as a JSON array of command strings. Each command should be:
        - Safe to execute (no destructive operations)
        - Relevant to the specific incident
        - Likely to provide useful diagnostic information
        - Properly formatted for Linux shell execution

        Example format:
        [
            "systemctl status nginx",
            "curl -I http://localhost",
            "tail -n 50 /var/log/nginx/error.log",
            "netstat -tlnp | grep :80"
        ]

        Focus on commands that are most likely to reveal the root cause of this specific incident.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert Linux system administrator and SRE engineer. Generate precise, safe diagnostic commands."),
                HumanMessage(content=diagnostic_prompt)
            ])
            
            commands = json.loads(response.content)
            logger.info(f"LLM generated {len(commands)} diagnostic commands")
            return commands
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM diagnostic commands: {e}")
            return [
                "uptime",
                "free -h", 
                "df -h",
                "ps aux --sort=-%cpu | head -10",
                "systemctl status"
            ]
        except Exception as e:
            logger.error(f"LLM diagnostic command generation failed: {e}")
            return []
    
    async def generate_remediation_commands_with_llm(self, incident_data: Dict[str, Any],
                                                   analysis_result: Dict[str, Any],
                                                   diagnostic_results: List[Dict[str, Any]]) -> List[str]:
        """
        Use LLM to generate intelligent remediation commands based on diagnostic results
        """
        
        # Format diagnostic results for LLM
        diagnostic_summary = "\n".join([
            f"Command: {result.get('command', 'N/A')}\nOutput: {result.get('output', 'N/A')[:200]}...\nSuccess: {result.get('success', False)}\n"
            for result in diagnostic_results[-10:]  # Last 10 results
        ])
        
        remediation_prompt = f"""
        You are an expert SRE engineer creating remediation commands for a production incident. Based on the incident analysis and diagnostic results below, generate safe remediation commands.

        Incident Details:
        - Title: {incident_data.get('title', 'N/A')}
        - Description: {incident_data.get('description', 'N/A')}
        - Target IP: {incident_data.get('target_ip', 'N/A')}
        
        Analysis Results:
        - Detected Services: {analysis_result.get('detected_services', [])}
        - Issue Types: {analysis_result.get('issue_types', [])}
        - Likely Root Causes: {analysis_result.get('likely_root_causes', [])}

        Diagnostic Results Summary:
        {diagnostic_summary}

        Based on the diagnostic evidence, generate remediation commands that will likely resolve this incident. Consider:
        1. Service restarts if services are down
        2. Configuration fixes if config errors are detected
        3. Resource cleanup if resource issues are found
        4. Network/connectivity fixes if network issues are present
        5. Permission fixes if permission errors are detected

        IMPORTANT SAFETY REQUIREMENTS:
        - Only suggest reversible operations
        - Prefer service restarts over system reboots
        - Include rollback considerations
        - Avoid destructive operations
        - Test connectivity before making changes

        Provide your response as a JSON array of command strings, ordered by safety (safest first):

        Example format:
        [
            "systemctl restart nginx",
            "nginx -s reload",
            "systemctl enable nginx"
        ]

        Only include commands that are directly supported by the diagnostic evidence and are safe to execute.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert SRE engineer focused on safe, effective incident remediation. Prioritize system stability and reversibility."),
                HumanMessage(content=remediation_prompt)
            ])
            
            commands = json.loads(response.content)
            logger.info(f"LLM generated {len(commands)} remediation commands")
            return commands
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM remediation commands: {e}")
            return []
        except Exception as e:
            logger.error(f"LLM remediation command generation failed: {e}")
            return []
    
    async def generate_verification_commands_with_llm(self, incident_data: Dict[str, Any],
                                                    analysis_result: Dict[str, Any],
                                                    remediation_commands: List[str]) -> List[str]:
        """
        Use LLM to generate verification commands to confirm incident resolution
        """
        
        verification_prompt = f"""
        You are an expert SRE engineer creating verification commands to confirm incident resolution. Based on the incident details and remediation actions below, generate verification commands.

        Incident Details:
        - Title: {incident_data.get('title', 'N/A')}
        - Description: {incident_data.get('description', 'N/A')}
        - Target IP: {incident_data.get('target_ip', 'N/A')}
        
        Analysis Results:
        - Detected Services: {analysis_result.get('detected_services', [])}
        - Issue Types: {analysis_result.get('issue_types', [])}

        Remediation Commands Applied:
        {', '.join(remediation_commands)}

        Generate verification commands that will confirm whether the incident has been resolved. Consider:
        1. Service status checks for affected services
        2. Functional tests (HTTP requests, database connections, etc.)
        3. Resource monitoring to ensure stability
        4. End-to-end connectivity tests
        5. Log monitoring to ensure no new errors

        Provide your response as a JSON array of command strings that will verify the fix:

        Example format:
        [
            "systemctl is-active nginx",
            "curl -s -o /dev/null -w '%{{http_code}}' http://localhost",
            "systemctl is-system-running"
        ]

        Focus on commands that directly verify the specific issues mentioned in the original incident are resolved.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert SRE engineer focused on thorough verification of incident resolution."),
                HumanMessage(content=verification_prompt)
            ])
            
            commands = json.loads(response.content)
            logger.info(f"LLM generated {len(commands)} verification commands")
            return commands
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM verification commands: {e}")
            return [
                "uptime",
                "systemctl is-system-running"
            ]
        except Exception as e:
            logger.error(f"LLM verification command generation failed: {e}")
            return []
    
    async def assess_verification_results_with_llm(self, incident_data: Dict[str, Any],
                                                 verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use LLM to assess verification results and determine if incident is resolved
        """
        
        # Format verification results for LLM
        verification_summary = "\n".join([
            f"Command: {result.get('command', 'N/A')}\nOutput: {result.get('output', 'N/A')}\nSuccess: {result.get('success', False)}\n"
            for result in verification_results
        ])
        
        assessment_prompt = f"""
        You are an expert SRE engineer assessing whether an incident has been successfully resolved. Based on the original incident and verification results below, provide your assessment.

        Original Incident:
        - Title: {incident_data.get('title', 'N/A')}
        - Description: {incident_data.get('description', 'N/A')}

        Verification Results:
        {verification_summary}

        Analyze the verification results and respond with a JSON object:

        {{
            "incident_resolved": true/false,
            "confidence_level": "high|medium|low",
            "resolution_summary": "brief description of what was resolved",
            "remaining_concerns": ["list", "of", "any", "remaining", "issues"],
            "recommended_monitoring": ["list", "of", "things", "to", "monitor"],
            "success_indicators": ["list", "of", "positive", "indicators"],
            "failure_indicators": ["list", "of", "negative", "indicators"]
        }}

        Be thorough in your analysis and conservative in declaring full resolution.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert SRE engineer with a conservative approach to incident resolution assessment."),
                HumanMessage(content=assessment_prompt)
            ])
            
            assessment = json.loads(response.content)
            logger.info(f"LLM verification assessment: {assessment.get('incident_resolved', False)}")
            return assessment
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM verification assessment: {e}")
            return {
                "incident_resolved": False,
                "confidence_level": "low",
                "resolution_summary": "Unable to assess resolution",
                "remaining_concerns": ["Assessment failed"],
                "recommended_monitoring": ["Manual verification required"],
                "success_indicators": [],
                "failure_indicators": ["LLM assessment error"]
            }
        except Exception as e:
            logger.error(f"LLM verification assessment failed: {e}")
            return {}

# For backward compatibility
def get_intelligent_config(openai_api_key: str):
    """Get the LLM-powered intelligent SSH configuration instance"""
    return LLMIntelligentSSHConfig(openai_api_key)