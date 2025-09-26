import sqlite3

DB = 'x3dh.db'  # Or use the full path if needed: './backend/x3dh.db'

with sqlite3.connect(DB) as conn:
    c = conn.cursor()

    # Drop and recreate the messages table
    c.execute("DROP TABLE IF EXISTS messages")

    c.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            payload TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)

    print("✅ Messages table created.")
