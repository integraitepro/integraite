"""
ServiceNow API client for fetching incidents
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import base64
import json
import logging
from aiohttp import BasicAuth

from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceNowClient:
    """ServiceNow REST API client"""
    
    def __init__(self, instance_url: str, username: str, password: str):
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.base_url = f"{self.instance_url}/api/now/table"
        
        # Create auth object and headers
        self.auth = BasicAuth(username, password)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    @classmethod
    def from_settings(cls) -> Optional['ServiceNowClient']:
        """Create client from application settings"""
        if not all([
            settings.SERVICENOW_INSTANCE_URL,
            settings.SERVICENOW_USERNAME,
            settings.SERVICENOW_PASSWORD
        ]):
            logger.warning("ServiceNow credentials not configured")
            return None
        
        return cls(
            instance_url=settings.SERVICENOW_INSTANCE_URL,
            username=settings.SERVICENOW_USERNAME,
            password=settings.SERVICENOW_PASSWORD
        )
    
    async def test_connection(self) -> bool:
        """Test connection to ServiceNow instance"""
        try:
            url = f"{self.base_url}/{settings.SERVICENOW_TABLE}"
            params = {
                'sysparm_limit': 1,
                'sysparm_fields': 'number'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=self.auth, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        logger.info("ServiceNow connection test successful")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"ServiceNow connection test failed: {response.status}")
                        logger.error(f"Error response: {error_text}")
                        print(f"ServiceNow connection test failed: {response.status}")
                        print(f"Error response: {error_text}")
                        print(f"Request URL: {url}")
                        print(f"Request auth: {self.auth}")
                        print(f"Request headers: {self.headers}")
                        return False
        except Exception as e:
            logger.error(f"ServiceNow connection test error: {e}")
            print(f"ServiceNow connection test error: {e}")
            return False
    
    async def get_incidents(
        self,
        limit: int = 100,
        offset: int = 0,
        state: Optional[str] = None,
        priority: Optional[str] = None,
        opened_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch incidents from ServiceNow
        
        Args:
            limit: Maximum number of incidents to fetch
            offset: Number of incidents to skip
            state: Filter by state (1=New, 2=In Progress, 6=Resolved, 7=Closed)
            priority: Filter by priority (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning)
            opened_since: Filter incidents opened since this datetime
        """
        try:
            url = f"{self.base_url}/{settings.SERVICENOW_TABLE}"
            
            # Build query parameters
            params = {
                'sysparm_limit': limit,
                'sysparm_offset': offset,
                'sysparm_display_value': 'all',
                'sysparm_fields': (
                    'number,short_description,description,state,priority,urgency,'
                    'impact,assigned_to,assignment_group,category,subcategory,'
                    'opened_at,resolved_at,closed_at,sys_updated_on,sys_created_on,'
                    'caller_id,company,location,business_service,cmdb_ci'
                )
            }
            
            # Build query filter
            query_filters = []
            
            if state:
                query_filters.append(f"state={state}")
            
            if priority:
                query_filters.append(f"priority={priority}")
            
            if opened_since:
                # Format datetime for ServiceNow (YYYY-MM-DD HH:MM:SS)
                formatted_date = opened_since.strftime('%Y-%m-%d %H:%M:%S')
                query_filters.append(f"opened_at>={formatted_date}")
            
            if query_filters:
                params['sysparm_query'] = '^'.join(query_filters)
            
            # Order by most recent first
            params['sysparm_query'] = (
                params.get('sysparm_query', '') + '^ORDERBYDESCsys_updated_on'
            ).lstrip('^')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=self.auth, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        incidents = data.get('result', [])
                        logger.info(f"Retrieved {len(incidents)} incidents from ServiceNow")
                        return incidents
                    else:
                        error_text = await response.text()
                        logger.error(f"ServiceNow API error {response.status}: {error_text}")
                        return []
        
        except Exception as e:
            logger.error(f"Error fetching incidents from ServiceNow: {e}")
            return []
    
    async def get_incident_by_number(self, incident_number: str) -> Optional[Dict[str, Any]]:
        """Get a specific incident by its number"""
        try:
            url = f"{self.base_url}/{settings.SERVICENOW_TABLE}"
            params = {
                'sysparm_query': f"number={incident_number}",
                'sysparm_display_value': 'all',
                'sysparm_fields': (
                    'number,short_description,description,state,priority,urgency,'
                    'impact,assigned_to,assignment_group,category,subcategory,'
                    'opened_at,resolved_at,closed_at,sys_updated_on,sys_created_on,'
                    'caller_id,company,location,business_service,cmdb_ci'
                )
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=self.auth, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        incidents = data.get('result', [])
                        if incidents:
                            return incidents[0]
                        else:
                            logger.warning(f"Incident {incident_number} not found")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"ServiceNow API error {response.status}: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error fetching incident {incident_number} from ServiceNow: {e}")
            return None
    
    def map_servicenow_to_internal(self, servicenow_incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map ServiceNow incident fields to internal incident format
        """
        # Map ServiceNow states to internal statuses
        state_mapping = {
            '1': 'investigating',  # New
            '2': 'investigating',  # In Progress
            '3': 'resolving',      # On Hold
            '6': 'resolved',       # Resolved
            '7': 'closed',         # Closed
            '8': 'closed'          # Canceled
        }
        
        # Map ServiceNow priorities to internal severities
        priority_mapping = {
            '1': 'critical',   # Critical
            '2': 'high',       # High
            '3': 'medium',     # Moderate
            '4': 'low',        # Low
            '5': 'low'         # Planning
        }
        
        # Extract values (ServiceNow returns both value and display_value)
        def get_value(field_data):
            if isinstance(field_data, dict):
                return field_data.get('value', '') or field_data.get('display_value', '')
            return field_data or ''
        
        def get_safe_value(field_data, default='N/A'):
            """Get value from ServiceNow field with safe fallback"""
            if isinstance(field_data, dict):
                return field_data.get('display_value', '') or field_data.get('value', '') or default
            return str(field_data) if field_data else default
        
        # Core incident data
        incident_number = get_safe_value(servicenow_incident.get('number', ''))
        state = get_value(servicenow_incident.get('state', ''))
        priority = get_value(servicenow_incident.get('priority', ''))
        
        # Parse dates
        def parse_servicenow_date(date_str):
            if not date_str or date_str == 'N/A':
                return None
            try:
                # ServiceNow date format: YYYY-MM-DD HH:MM:SS
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                return None
        
        opened_at = parse_servicenow_date(get_value(servicenow_incident.get('opened_at', '')))
        resolved_at = parse_servicenow_date(get_value(servicenow_incident.get('resolved_at', '')))
        closed_at = parse_servicenow_date(get_value(servicenow_incident.get('closed_at', '')))
        updated_at = parse_servicenow_date(get_value(servicenow_incident.get('sys_updated_on', '')))
        
        # Extract affected services from business_service and cmdb_ci
        affected_services = []
        business_service = get_safe_value(servicenow_incident.get('business_service', {}))
        if business_service and business_service != 'N/A':
            affected_services.append(business_service)
        
        cmdb_ci = get_safe_value(servicenow_incident.get('cmdb_ci', {}))
        if cmdb_ci and cmdb_ci != 'N/A' and cmdb_ci not in affected_services:
            affected_services.append(cmdb_ci)
        
        # Extract assignment information
        assigned_to = get_safe_value(servicenow_incident.get('assigned_to', {}))
        assignment_group = get_safe_value(servicenow_incident.get('assignment_group', {}))
        
        # Extract caller and company information
        caller_id = get_safe_value(servicenow_incident.get('caller_id', {}))
        company = get_safe_value(servicenow_incident.get('company', {}))
        
        # Build comprehensive incident data
        return {
            'source_alert_id': incident_number,
            'title': get_safe_value(servicenow_incident.get('short_description', '')),
            'description': get_safe_value(servicenow_incident.get('description', '')),
            'short_description': get_safe_value(servicenow_incident.get('short_description', '')),
            'severity': priority_mapping.get(priority, 'medium'),
            'status': state_mapping.get(state, 'investigating'),
            'category': get_safe_value(servicenow_incident.get('category', '')),
            'subcategory': get_safe_value(servicenow_incident.get('subcategory', '')),
            'source_system': 'ServiceNow',
            'affected_services': affected_services if affected_services else ['N/A'],
            'customer_impact': priority in ['1', '2'],  # Critical and High priority
            'estimated_affected_users': None,  # Not provided in ServiceNow by default
            'detection_time': opened_at,
            'resolution_time': resolved_at,
            'closed_time': closed_at,
            'updated_at': updated_at,
            'assigned_to': assigned_to,
            'assignment_group': assignment_group,
            'caller_id': caller_id,
            'company': company,
            'impact': get_safe_value(servicenow_incident.get('impact', '')),
            'urgency': get_safe_value(servicenow_incident.get('urgency', '')),
            'contact_type': get_safe_value(servicenow_incident.get('contact_type', '')),
            'close_code': get_safe_value(servicenow_incident.get('close_code', '')),
            'close_notes': get_safe_value(servicenow_incident.get('close_notes', '')),
            'resolution_notes': get_safe_value(servicenow_incident.get('close_notes', '')),
            'work_notes': get_safe_value(servicenow_incident.get('work_notes', '')),
            'servicenow_data': servicenow_incident  # Store original data
        }


class ServiceNowService:
    """Service layer for ServiceNow operations"""
    
    def __init__(self):
        self.client = ServiceNowClient.from_settings()
    
    async def sync_incidents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Sync incidents from ServiceNow and return in internal format
        """
        if not self.client:
            logger.warning("ServiceNow client not configured")
            return []
        
        # Test connection first
        if not await self.client.test_connection():
            logger.error("ServiceNow connection test failed")
            return []
        
        try:
            # Fetch all incidents (no date filtering for now)
            servicenow_incidents = await self.client.get_incidents(
                limit=limit
            )
            
            # Convert to internal format
            internal_incidents = []
            for sn_incident in servicenow_incidents:
                internal_incident = self.client.map_servicenow_to_internal(sn_incident)
                internal_incidents.append(internal_incident)
            
            logger.info(f"Synchronized {len(internal_incidents)} incidents from ServiceNow")
            return internal_incidents
        
        except Exception as e:
            logger.error(f"Error syncing incidents from ServiceNow: {e}")
            return []
    
    async def get_incident(self, incident_number: str) -> Optional[Dict[str, Any]]:
        """Get a specific incident by number"""
        if not self.client:
            return None
        
        servicenow_incident = await self.client.get_incident_by_number(incident_number)
        if servicenow_incident:
            return self.client.map_servicenow_to_internal(servicenow_incident)
        return None


# Global instance
servicenow_service = ServiceNowService()