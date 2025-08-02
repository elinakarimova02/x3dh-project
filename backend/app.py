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
        c = conn.cursor()
        c.execute("SELECT id, sender, payload FROM messages WHERE receiver = ?", (username,))
        msgs = [{'id': row[0], 'sender': row[1], 'payload': row[2]} for row in c.fetchall()]
    return jsonify({'messages': msgs})

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
        c = conn.cursor()

        # Get users
        c.execute("SELECT username, ik, spk, spk_sig FROM users")
        users = [
            {'username': row[0], 'ik': row[1], 'spk': row[2], 'spk_sig': row[3]}
            for row in c.fetchall()
        ]

        # Prekeys (assume table: prekeys with username and opk)
        c.execute("SELECT username, opk FROM prekeys")
        rows = c.fetchall()
        prekeys = {}
        for username, opk in rows:
            prekeys.setdefault(username, []).append(opk)
        
        # Queues (how many messages are waiting per user)
        c.execute("SELECT receiver, COUNT(*) FROM messages GROUP BY receiver")
        queues = {row[0]: row[1] for row in c.fetchall()}

        # Recent messages
        c.execute("SELECT id, sender, receiver, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10")
        logs = [
            f"[{row[3]}] From {row[1]} to {row[2]} (msg id: {row[0]})"
            for row in c.fetchall()
        ]
    return render_template('dashboard.html', users=users, prekeys=prekeys, queues=queues, logs=logs)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
