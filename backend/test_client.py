import requests

BASE_URL = "http://127.0.0.1:5050"

# Register Alice
alice = {
    "username": "alice",
    "ik": "ik-alice",
    "spk": "spk-alice",
    "spk_sig": "sig-alice",
    "opks": ["opk-alice-1", "opk-alice-2", "opk-alice-3", "opk-alice-4"]
}
print("Registering Alice:", requests.post(f"{BASE_URL}/register", json=alice).json())

# Register Bob
bob = {
    "username": "bob",
    "ik": "ik-bob",
    "spk": "spk-bob",
    "spk_sig": "sig-bob",
    "opks": ["opk-bob-1", "opk-bob-2", "opk-bob-3", "opk-bob-4"]
}
print("Registering Bob:", requests.post(f"{BASE_URL}/register", json=bob).json())

# Register Charlie
charlie = {
    "username": "charlie",
    "ik": "ik-charlie",
    "spk": "spk-charlie",
    "spk_sig": "sig-charlie",
    "opks": ["opk-charlie-0", "opk-charlie-1", "opk-charlie-2", "opk-charlie-3", "opk-charlie-4"]
}
print("Registering Charlie:", requests.post(f"{BASE_URL}/register", json=charlie).json())

# Send a message from Alice to Bob
message = {
    "sender": "alice",
    "receiver": "bob",
    "payload": "Hello from Alice!"
}
print("Sending message:", requests.post(f"{BASE_URL}/send", json=message).json())

# Fetch Bob's messages
print("Bob's inbox:", requests.get(f"{BASE_URL}/receive/bob").json())
