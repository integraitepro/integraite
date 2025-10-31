#!/usr/bin/env python3
"""Check what incidents are in the database"""

import asyncio
import sys
import os
import sqlite3

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('integraite.db')
        cursor = conn.cursor()
        
        # Check if incidents table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Incidents table exists")
            
            # Get incident count
            cursor.execute("SELECT COUNT(*) FROM incidents;")
            count = cursor.fetchone()[0]
            print(f"Total incidents in database: {count}")
            
            if count > 0:
                # Get some sample incidents
                cursor.execute("SELECT id, title, description, severity, status, source_system, source_alert_id FROM incidents LIMIT 5;")
                incidents = cursor.fetchall()
                
                print("\nSample incidents:")
                for incident in incidents:
                    print(f"  ID: {incident[0]}")
                    print(f"  Title: {incident[1]}")
                    print(f"  Description: {incident[2][:100]}...")
                    print(f"  Severity: {incident[3]}")
                    print(f"  Status: {incident[4]}")
                    print(f"  Source System: {incident[5]}")
                    print(f"  Source Alert ID: {incident[6]}")
                    print("  ---")
            else:
                print("No incidents found in database")
        else:
            print("Incidents table does not exist")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()