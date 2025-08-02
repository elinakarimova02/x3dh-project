# import time
# import json
# import requests
# import paho.mqtt.client as mqtt

# USERNAME = "alice"
# RECIPIENT = "bob"

# BACKEND_URL = "http://backend:5000"
# MQTT_BROKER = "mqtt"
# TOPIC = f"/messages/{RECIPIENT}"

# # Simulated Key Bundle
# def register():
#     payload = {
#         "username": USERNAME,
#         "ik": "ik-alice",
#         "spk": "spk-alice",
#         "spk_sig": "sig-alice",
#         "opks": ["opk-a1", "opk-a2"]
#     }
#     r = requests.post(f"{BACKEND_URL}/register", json=payload)
#     print("[Alice] Registered:", r.status_code)

# def fetch_recipient_bundle():
#     r = requests.get(f"{BACKEND_URL}/get-prekey/{RECIPIENT}")
#     print("[Alice] Got Bob's bundle:", r.json())
#     return r.json()

# def encrypt_message(msg):
#     return f"X3DH_ENCRYPTED({msg})"

# def send_message():
#     encrypted = encrypt_message("Hello Bob! This is Alice.")
#     payload = {
#         "sender": USERNAME,
#         "receiver": RECIPIENT,
#         "payload": encrypted
#     }
#     r = requests.post(f"{BACKEND_URL}/send", json=payload)
#     print("[Alice] Message sent:", r.status_code)

# if __name__ == '__main__':
#     time.sleep(5)
#     register()
#     fetch_recipient_bundle()
#     send_message()
