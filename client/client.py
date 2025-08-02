import os
import requests
import time
import json
import random

USERNAME = os.getenv("USERNAME", "unknown")
PEER = os.getenv("PEER", "bob")
BACKEND = os.getenv("BACKEND", "http://backend:5000")

# Simulate key generation
def generate_keys(username):
    return {
        "ik": f"ik-{username}",
        "spk": f"spk-{username}",
        "spk_sig": f"sig-{username}",
        "opks": [f"opk-{username}-{i}" for i in range(5)]
    }

def register():
    bundle = generate_keys(USERNAME)
    res = requests.post(f"{BACKEND}/register", json={"username": USERNAME, **bundle})
    print(f"[{USERNAME}] Registered: {res.status_code}")

def get_peer_bundle():
    res = requests.get(f"{BACKEND}/get-prekey/{PEER}")
    if res.status_code != 200:
        print(f"[{USERNAME}] Could not fetch {PEER}'s keys")
        return None
    print(f"[{USERNAME}] Got {PEER}'s bundle: {res.json()}")
    return res.json()

def send_message():
    payload = f"Hello from {USERNAME} to {PEER} - {random.randint(100, 999)}"
    res = requests.post(f"{BACKEND}/send", json={
        "sender": USERNAME,
        "receiver": PEER,
        "payload": payload
    })
    print(f"[{USERNAME}] Message sent: {res.status_code}")

def receive_messages():
    res = requests.get(f"{BACKEND}/receive/{USERNAME}")
    if res.status_code != 200:
        return
    messages = res.json().get("messages", [])
    for msg in messages:
        print(f"[{USERNAME}] Received from {msg['sender']}: {msg['payload']}")
        requests.post(f"{BACKEND}/ack/{msg['id']}")

def main():
    register()
    get_peer_bundle()
    send_message()
    for _ in range(3):
        receive_messages()
        time.sleep(5)

if __name__ == '__main__':
    main()
