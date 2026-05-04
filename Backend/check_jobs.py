import sqlite3

conn = sqlite3.connect('jobspy.db')
cursor = conn.cursor()

# Check what tables exist
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print(f'Tables in database: {tables}')

if 'jobs' in tables:
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total = cursor.fetchone()[0]
    print(f'\nTotal jobs in database: {total}')

    if total > 0:
        cursor.execute('SELECT id, title, company, location FROM jobs LIMIT 5')
        print('\nFirst 5 jobs:')
        for row in cursor.fetchall():
            print(f'  - {row[1]} at {row[2]}')
            print(f'    Location: {row[3]}')
else:
    print('\nNo jobs table found. Database needs to be initialized.')

conn.close()
