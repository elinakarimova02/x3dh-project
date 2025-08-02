# import time
# import requests

# USERNAME = "bob"
# BACKEND_URL = "http://backend:5000"

# # Register Bob
# def register():
#     payload = {
#         "username": USERNAME,
#         "ik": "ik-bob",
#         "spk": "spk-bob",
#         "spk_sig": "sig-bob",
#         "opks": ["opk-b1", "opk-b2"]
#     }
#     r = requests.post(f"{BACKEND_URL}/register", json=payload)
#     print("[Bob] Registered:", r.status_code)

# # Poll messages from backend
# def poll_messages():
#     r = requests.get(f"{BACKEND_URL}/receive/{USERNAME}")
#     messages = r.json().get("messages", [])
#     for msg in messages:
#         print(f"[Bob] Received from {msg['sender']}: {msg['payload']}")
#         ack = requests.post(f"{BACKEND_URL}/ack/{msg['id']}")

# if __name__ == '__main__':
#     time.sleep(5)
#     register()
#     while True:
#         poll_messages()
#         time.sleep(10)
