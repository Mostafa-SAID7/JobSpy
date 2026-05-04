import sqlite3
import os

db_path = 'Backend/jobspy.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    email = "m.ssaid356@gmail.com"
    cursor.execute("SELECT email, hashed_password, is_active FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    if row:
        print(f"User found: {row[0]}")
        print(f"Hashed password: {row[1]}")
        print(f"Is active: {row[2]}")
    else:
        print(f"User NOT found: {email}")
    conn.close()
