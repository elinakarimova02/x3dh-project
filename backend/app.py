from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB = 'x3dh.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                ik TEXT,
                spk TEXT,
                spk_sig TEXT
            );
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prekeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                opk TEXT
            );
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                receiver TEXT,
                payload TEXT,
                timestamp TEXT
            );
        ''')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    ik = data['ik']
    spk = data['spk']
    spk_sig = data['spk_sig']
    opks = data['opks']

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)", (username, ik, spk, spk_sig))
        for opk in opks:
            c.execute("INSERT INTO prekeys (username, opk) VALUES (?, ?)", (username, opk))
        conn.commit()
    return jsonify({'status': 'registered'})

@app.route('/get-prekey/<username>', methods=['GET'])
def get_prekey(username):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT ik, spk, spk_sig FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        c.execute("SELECT id, opk FROM prekeys WHERE username = ? LIMIT 1", (username,))
        opk = c.fetchone()
        if opk:
            c.execute("DELETE FROM prekeys WHERE id = ?", (opk[0],))
            opk_val = opk[1]
        else:
            opk_val = None

        conn.commit()
    return jsonify({
        'ik': user[0],
        'spk': user[1],
        'spk_sig': user[2],
        'opk': opk_val
    })

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    sender = data['sender']
    receiver = data['receiver']
    payload = data['payload']
    timestamp = datetime.utcnow().isoformat()

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (sender, receiver, payload, timestamp) VALUES (?, ?, ?, ?)",
                  (sender, receiver, payload, timestamp))
        conn.commit()
    return jsonify({'status': 'message stored'})

@app.route('/receive/<username>', methods=['GET'])
def receive(username):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Fetch pending messages
        c.execute("""
            SELECT id, sender, receiver, payload, timestamp
            FROM messages
            WHERE receiver = ?
            ORDER BY timestamp ASC
        """, (username,))

        messages = c.fetchall()

        # Convert rows to dicts
        messages_list = [
            {
                "id": row["id"],
                "sender": row["sender"],
                "receiver": row["receiver"],
                "payload": row["payload"],
                "timestamp": row["timestamp"]
            }
            for row in messages
        ]

    return jsonify({"messages": messages_list})


@app.route('/ack/<msg_id>', methods=['POST'])
def ack(msg_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        conn.commit()
    return jsonify({'status': 'deleted'})

@app.route('/')
def dashboard():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Users table
        c.execute("SELECT username, ik, spk, spk_sig FROM users")
        users = c.fetchall()

        # Prekeys table
        c.execute("SELECT username, opk FROM prekeys")
        prekeys_raw = c.fetchall()
        prekeys = {}
        for row in prekeys_raw:
            prekeys.setdefault(row["username"], []).append(row["opk"])

        # Pending message count per receiver
        c.execute("SELECT receiver, COUNT(*) as count FROM messages GROUP BY receiver")
        queues = {row["receiver"]: row["count"] for row in c.fetchall()}

        # Last 10 messages
        c.execute("SELECT id, sender, receiver, payload, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10")
        logs = [
            f"[{row['timestamp']}] From {row['sender']} to {row['receiver']}: {row['payload']}"
            for row in c.fetchall()
        ]

    return render_template(
        'dashboard.html',
        users=users,
        prekeys=prekeys,
        queues=queues,
        logs=logs
    )

@app.route('/api/dashboard-data')
def dashboard_data():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Users
        c.execute("SELECT username, ik, spk, spk_sig FROM users")
        users = [
            {"username": row["username"], "ik": row["ik"], "spk": row["spk"], "sig": row["spk_sig"]}
            for row in c.fetchall()
        ]

        # Prekeys
        c.execute("SELECT username, opk FROM prekeys")
        prekeys = [
            {"username": row["username"], "opk": row["opk"]}
            for row in c.fetchall()
        ]

        # Pending messages per receiver
        c.execute("SELECT receiver, COUNT(*) as count FROM messages GROUP BY receiver")
        pending = [
            {"receiver": row["receiver"], "count": row["count"]}
            for row in c.fetchall()
        ]

        # Last 10 messages
        c.execute("SELECT id, sender, receiver, payload, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10")
        recent = [
            {"id": row["id"], "timestamp": row["timestamp"], "sender": row["sender"],
             "receiver": row["receiver"], "payload": row["payload"]}
            for row in c.fetchall()
        ]

    return jsonify({
        "users": users,
        "prekeys": prekeys,
        "pending": pending,
        "recent": recent
    })



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
