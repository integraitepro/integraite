#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_sre_agent_processing():
    """Test SRE agent processing directly"""
    
    # Import here to avoid circular imports
    from app.core.database import get_db
    from app.services.self_healing_sre_agent import SelfHealingSREAgent
    
    # Test payload matching what was sent to the webhook
    test_payload = {
        "result": [
            {
                "number": "INC0010031",
                "short_description": "High memory usage detected on production server",
                "description": "System monitoring alerts indicate abnormally high memory consumption on production server 13.60.250.208. Memory usage has reached 85% and continues to climb.",
                "assignment_group": {"value": "287ebd7da9fe198100f92cc8d1d2154e"},
                "business_stc": {"value": "business_value"},
                "cmdb_ci": {"value": "109562a3c611227500a7b7ff98cc0dc7"},
                "category": "software",
                "state": "2",
                "priority": "2",
                "u_ip_address": "13.60.250.208",
                "sys_created_on": "2025-10-30 10:30:00"
            }
        ]
    }
    
    print("🤖 Testing SRE Agent processing directly...")
    
    try:
        # Get database session
        async for db in get_db():
            print("📊 Database connection established")
            
            # Create SRE agent
            agent = SelfHealingSREAgent(db)
            print(f"🎯 SRE Agent created: {agent.agent_name}")
            
            # Process the incident
            print("🚀 Starting incident processing...")
            result = await agent.process_incident(test_payload)
            
            print("✅ Processing completed!")
            print(f"Result: {result}")
            
            # Check execution records after processing
            import sqlite3
            conn = sqlite3.connect('integraite.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, status, incident_number, started_at FROM sre_incident_execution ORDER BY started_at DESC')
            records = cursor.fetchall()
            print(f'\n📊 Total execution records: {len(records)}')
            for record in records:
                print(f'  ID: {record[0]}, Status: {record[1]}, Incident: {record[2]}, Started: {record[3]}')
            
            conn.close()
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sre_agent_processing())