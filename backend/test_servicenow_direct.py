#!/usr/bin/env python3
"""Test ServiceNow connection with explicit environment loading"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after loading env vars
from app.core.config import settings
from app.services.servicenow_client import ServiceNowClient

async def test_servicenow_direct():
    print(f"SERVICENOW_INSTANCE_URL: {settings.SERVICENOW_INSTANCE_URL}")
    print(f"SERVICENOW_USERNAME: {settings.SERVICENOW_USERNAME}")
    print(f"SERVICENOW_PASSWORD: {'*' * len(settings.SERVICENOW_PASSWORD) if settings.SERVICENOW_PASSWORD else 'None'}")
    
    if not all([settings.SERVICENOW_INSTANCE_URL, settings.SERVICENOW_USERNAME, settings.SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not properly loaded from environment")
        return
    
    # Create client directly
    client = ServiceNowClient(
        instance_url=settings.SERVICENOW_INSTANCE_URL,
        username=settings.SERVICENOW_USERNAME,
        password=settings.SERVICENOW_PASSWORD
    )
    
    print(f"Base URL: {client.base_url}")
    
    try:
        connected = await client.test_connection()
        print(f'ServiceNow connected: {connected}')
        
        if connected:
            incidents = await client.get_incidents(limit=5)
            print(f'Retrieved {len(incidents)} incidents from ServiceNow')
            if incidents:
                print('Sample incident fields:')
                for key in incidents[0].keys():
                    print(f'  {key}')
            else:
                print('No incidents found in ServiceNow')
        else:
            print('Cannot connect to ServiceNow - check credentials and permissions')
    except Exception as e:
        print(f'Error testing ServiceNow: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_servicenow_direct())