#!/usr/bin/env python3
"""Test basic ServiceNow instance accessibility"""

import asyncio
import aiohttp
from aiohttp import BasicAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

INSTANCE_URL = os.getenv('SERVICENOW_INSTANCE_URL')
USERNAME = os.getenv('SERVICENOW_USERNAME')
PASSWORD = os.getenv('SERVICENOW_PASSWORD')

async def test_basic_access():
    print(f"Testing basic access to: {INSTANCE_URL}")
    
    auth = BasicAuth(USERNAME, PASSWORD)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints_to_test = [
        f"{INSTANCE_URL}",  # Base instance
        f"{INSTANCE_URL}/api/now",  # API base
        f"{INSTANCE_URL}/api/now/table",  # Table API
        f"{INSTANCE_URL}/api/now/table/incident",  # Incident table
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            try:
                print(f"\nTesting endpoint: {endpoint}")
                async with session.get(endpoint, auth=auth, headers=headers) as response:
                    print(f"Status: {response.status}")
                    if response.status == 200:
                        print("✅ Success!")
                        try:
                            data = await response.json()
                            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        except:
                            text = await response.text()
                            print(f"Response (first 200 chars): {text[:200]}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error: {error_text[:200]}")
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_access())