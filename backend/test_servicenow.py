#!/usr/bin/env python3
"""Test ServiceNow connection and data retrieval"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.servicenow_client import servicenow_service

async def test_servicenow():
    if servicenow_service.client:
        print('ServiceNow client exists')
        try:
            connected = await servicenow_service.client.test_connection()
            print(f'ServiceNow connected: {connected}')
            
            if connected:
                incidents = await servicenow_service.sync_incidents(limit=5)
                print(f'Retrieved {len(incidents)} incidents from ServiceNow')
                if incidents:
                    print('Sample incident:')
                    for key, value in incidents[0].items():
                        print(f'  {key}: {value}')
                else:
                    print('No incidents found in ServiceNow')
            else:
                print('Cannot connect to ServiceNow')
        except Exception as e:
            print(f'Error testing ServiceNow: {e}')
            import traceback
            traceback.print_exc()
    else:
        print('ServiceNow client not configured')

if __name__ == "__main__":
    asyncio.run(test_servicenow())