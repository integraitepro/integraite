import sqlite3

conn = sqlite3.connect('integraite.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

# Check for SRE execution records specifically
try:
    cursor.execute('SELECT COUNT(*) FROM sre_executions')
    count = cursor.fetchone()[0]
    print(f'SRE executions count: {count}')
    
    if count > 0:
        cursor.execute('SELECT id, status, incident_id, created_at FROM sre_executions ORDER BY created_at DESC LIMIT 3')
        records = cursor.fetchall()
        print('Recent SRE executions:')
        for record in records:
            print(f'  ID: {record[0]}, Status: {record[1]}, Incident: {record[2]}, Created: {record[3]}')
except Exception as e:
    print(f'Error checking sre_executions: {e}')

conn.close()