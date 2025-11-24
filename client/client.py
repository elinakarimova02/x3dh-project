import os
import requests
import time
import random

USERNAME = os.getenv("USERNAME", "unknown")
BACKEND = os.getenv("BACKEND", "http://backend:5000")
PEERS = os.getenv("PEERS", "")
PEER_LIST = [p for p in PEERS.split(",") if p and p != USERNAME]


# Simulated key generation
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


def pick_random_peer():
    if not PEER_LIST:
        print(f"[{USERNAME}] No peers available")
        return None
    return random.choice(PEER_LIST)


def get_peer_bundle(peer):
    res = requests.get(f"{BACKEND}/get-prekey/{peer}")
    if res.status_code != 200:
        print(f"[{USERNAME}] Could not fetch {peer}'s keys")
        return None
    print(f"[{USERNAME}] Got {peer}'s bundle: {res.json()}")
    return res.json()


def send_message():
    peer = pick_random_peer()
    if peer is None:
        return

    payload = f"Hello from {USERNAME} to {peer} - {random.randint(100,999)}"

    res = requests.post(f"{BACKEND}/send", json={
        "sender": USERNAME,
        "receiver": peer,
        "payload": payload
    })

    print(f"[{USERNAME}] Sent to {peer}: {res.status_code}")


def receive_messages():
    res = requests.get(f"{BACKEND}/receive/{USERNAME}")

    if res.status_code != 200:
        return

    data = res.json()

    messages = data.get("messages", [])
    if not isinstance(messages, list):
        return

    for msg in messages:
        if not isinstance(msg, dict):
            continue  

        print(f"[{USERNAME}] Received from {msg['sender']}: {msg['payload']}")
        requests.post(f"{BACKEND}/ack/{msg['id']}")



def main():
    register()

    # Every few seconds: fetch new messages + send a random message
    while True:
        receive_messages()
        send_message()
        time.sleep(random.randint(3, 6))


if __name__ == "__main__":
    main()
