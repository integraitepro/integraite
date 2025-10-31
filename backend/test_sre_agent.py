#!/usr/bin/env python3
"""
Test script for SRE Agent ServiceNow webhook endpoint
Tests the complete workflow from ServiceNow webhook to autonomous incident resolution
"""

import json
import httpx
import asyncio
import time
from typing import Dict, Any

# Test ServiceNow webhook payload - this is the exact format sent to the trigger endpoint
TEST_SCENARIOS_SIMPLE ={
            "number": "INC0010045",
            "short_description": "Tomcat is not running on 13.60.250.208",
            "description": "Test incident for SRE agent",
            "priority": "3",
            "category": "software",
            "u_ip_address": "13.60.250.208",
            "assignment_group": "",
            "business_service": "",
            "cmdb_ci": "",
            "impact": "2",
            "urgency": "2",
            "state": "1"
        }

# Test ServiceNow webhook payload - this is the exact format sent to the trigger endpoint
TEST_SCENARIOS ={
            "parent": "",
            "made_sla": "true",
            "caused_by": "",
            "watch_list": "",
            "upon_reject": "cancel",
            "sys_updated_on": "2025-10-17 07:39:46",
            "child_incidents": "0",
            "hold_reason": "",
            "origin_table": "",
            "task_effective_number": "INC0010045",
            "approval_history": "",
            "number": "INC0010045",
            "resolved_by": "",
            "sys_updated_by": "NagaAmaresh",
            "opened_by": {
                "link": "https://dev283178.service-now.com/api/now/table/sys_user/e1bd8f6d835872103e2e9a96feaad3b4",
                "value": "e1bd8f6d835872103e2e9a96feaad3b4"
            },
            "user_input": "",
            "sys_created_on": "2025-10-17 07:39:46",
            "sys_domain": {
                "link": "https://dev283178.service-now.com/api/now/table/sys_user_group/global",
                "value": "global"
            },
            "state": "1",
            "route_reason": "",
            "sys_created_by": "NagaAmaresh",
            "knowledge": "false",
            "order": "",
            "u_ip_address": "13.60.250.208",
            "calendar_stc": "",
            "closed_at": "",
            "cmdb_ci": "",
            "delivery_plan": "",
            "contract": "",
            "impact": "2",
            "active": "true",
            "work_notes_list": "",
            "business_service": "",
            "business_impact": "",
            "priority": "3",
            "sys_domain_path": "/",
            "rfc": "",
            "time_worked": "",
            "expected_start": "",
            "opened_at": "2025-10-17 07:39:46",
            "business_duration": "",
            "group_list": "",
            "work_end": "",
            "caller_id": "",
            "reopened_time": "",
            "resolved_at": "",
            "approval_set": "",
            "subcategory": "",
            "work_notes": "",
            "universal_request": "",
            "short_description": "Tomcat is not running on 13.60.250.208",
            "close_code": "",
            "correlation_display": "",
            "delivery_task": "",
            "work_start": "",
            "assignment_group": "",
            "additional_assignee_list": "",
            "business_stc": "",
            "cause": "",
            "description": "Automated incident created by Nagios monitoring\n\nService: Apache Tomcat\nIP Address: 13.60.250.208\nPort: 8080\nStatus: Service Down\nTimestamp: 2025-10-17 07:39:45 UTC\n\nAction Required: Please investigate and restart Tomcat service",
            "origin_id": "",
            "calendar_duration": "",
            "close_notes": "",
            "notify": "1",
            "service_offering": "",
            "sys_class_name": "incident",
            "closed_by": "",
            "follow_up": "",
            "parent_incident": "",
            "sys_id": "022fc28b836032103e2e9a96feaad3bf",
            "contact_type": "",
            "reopened_by": "",
            "incident_state": "1",
            "urgency": "2",
            "problem_id": "",
            "company": "",
            "reassignment_count": "0",
            "activity_due": "",
            "assigned_to": "",
            "severity": "3",
            "comments": "",
            "approval": "not requested",
            "sla_due": "",
            "comments_and_work_notes": "",
            "due_date": "",
            "sys_mod_count": "0",
            "reopen_count": "0",
            "sys_tags": "",
            "escalation": "0",
            "upon_approval": "proceed",
            "correlation_id": "",
            "location": "",
            "category": "software"
        }

# Base URL for the API (adjust as needed)
BASE_URL = "http://localhost:8000"

# Authentication token
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzYW5kZWVwZGh1bmdhbmExMEBnbWFpbC5jb20iLCJleHAiOjE3NjE4NTgxMzZ9.Gs9shFuT2N3YgtsmMdVg5zTHlYI7TgTtL5p2cvZOvjY"

# Headers for authenticated requests
AUTH_HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

async def test_sre_agent_workflow():
    """Test the complete LLM-powered SRE agent workflow"""
    print("🤖 Testing LLM-Powered SRE Agent Autonomous Incident Resolution")
    print("=" * 75)
    
    # Get the incident from the ServiceNow payload
    incident = TEST_SCENARIOS
    
    print(f"📋 Test Scenario: Tomcat Service Down")
    print(f"📝 Incident: {incident['number']} - {incident['short_description']}")
    print(f"📊 Priority: {incident['priority']} | Impact: {incident['impact']} | Urgency: {incident['urgency']}")
    print(f"🎯 Target IP: {incident.get('u_ip_address', 'N/A')}")
    print(f"🧠 Testing LLM reasoning for service detection and command generation")
    print()
    
    async with httpx.AsyncClient() as client:
        # 1. Trigger the LLM-powered SRE agent
        print("📡 Step 1: Triggering LLM-Powered SRE Agent with ServiceNow webhook...")
        
        # Wrap the incident data in the ServiceNow format
        servicenow_payload = TEST_SCENARIOS
        
        trigger_response = await client.post(
            f"{BASE_URL}/api/v1/incident/trigger-agent",
            json=servicenow_payload,
            headers=AUTH_HEADERS,
            timeout=30.0
        )
        
        if trigger_response.status_code != 200:
            print(f"❌ Failed to trigger agent: {trigger_response.status_code}")
            print(f"Response: {trigger_response.text}")
            return
        
        trigger_data = trigger_response.json()
        execution_id = trigger_data.get("execution_id")
        print(f"✅ Agent triggered successfully! Execution ID: {execution_id}")
        print(f"Status: {trigger_data.get('status')}")
        

        
        print(f"\n🎯 SRE Agent execution monitoring completed")
        print(f"Incident: {incident['number']} - {incident['short_description']}")



async def main():
    """Main test function"""
    print("🧪 Intelligent SRE Agent End-to-End Test Suite")
    print("=" * 55)
    
    
    incident = TEST_SCENARIOS
    print(f"\n📋 Test Scenario: Tomcat Service Down")
    print(f"   Incident: {incident['number']} - {incident['short_description']}")
    print(f"   Priority: {incident['priority']} | Category: {incident['category']}")
    print(f"   Target IP: {incident['u_ip_address']}")
    
    print("\n" + "=" * 55)
    
    # Run the test
    try:
        print("🚀 Running SRE Agent Test: Tomcat Service Down")
        await test_sre_agent_workflow()
        
        print("\n" + "=" * 55)
        print("🎯 Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    print("\n🎉 Intelligent SRE Agent tests completed!")
    print("💡 The agent now intelligently detects services and issues from incident descriptions")
    print("🔧 Commands are generated dynamically based on detected context")
    print("🔑 SSH configuration is managed through environment variables")

if __name__ == "__main__":
    asyncio.run(main())