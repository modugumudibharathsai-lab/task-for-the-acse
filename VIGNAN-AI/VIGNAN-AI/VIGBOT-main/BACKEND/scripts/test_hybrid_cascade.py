import requests
import time
import sys
import json

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"
student_roll = "251FA04E96"
password = student_roll

print("=" * 70)
print(f"HYBRID CASCADE VERIFICATION TEST: Student {student_roll}")
print("=" * 70)

# 1. Login
t0 = time.time()
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": student_roll, "password": password}
)
if login_resp.status_code != 200:
    # Try default password if roll doesn't match
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": student_roll, "password": "student123"}
    )
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.status_code} - {login_resp.text}")
    sys.exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"1. Login successful ({time.time() - t0:.2f}s)")

# 2. Create Conversation
conv_resp = requests.post(
    f"{BASE_URL}/conversations",
    headers=headers,
    json={"title": "Hybrid Cascade Verification"}
)
if conv_resp.status_code != 200:
    print(f"Conversation creation failed: {conv_resp.text}")
    sys.exit(1)

conv_id = conv_resp.json()["conversation_id"]
print(f"2. Created conversation: {conv_id}")

test_queries = [
    "What is my registration number?",
    "Can you explain the difference between a stack and a queue simply for my computer science exam?",
    "Who is my class teacher?"
]

for idx, q in enumerate(test_queries, 1):
    print("\n" + "-" * 70)
    print(f"TEST {idx}: {q}")
    print("-" * 70)
    t_start = time.time()
    msg_resp = requests.post(
        f"{BASE_URL}/conversations/{conv_id}/messages",
        headers=headers,
        json={"content": q, "language": "en"},
        timeout=35.0
    )
    elapsed = time.time() - t_start
    if msg_resp.status_code != 200:
        print(f"Query failed ({elapsed:.2f}s): {msg_resp.status_code} - {msg_resp.text}")
        continue

    data = msg_resp.json()
    print(f"Elapsed Time : {elapsed:.2f}s")
    print(f"Source Agent : {data.get('source_agent')}")
    print(f"LLM Provider : {data.get('llm_provider')}")
    print(f"Model Used   : {data.get('model_used')}")
    print(f"Used Fallback: {data.get('used_fallback')}")
    print(f"Category     : {data.get('category')}")
    print(f"\nResponse Content:\n{data.get('content')}")
    if data.get('structured_card'):
        print(f"\nStructured Card: {data.get('structured_card').get('type')} - {data.get('structured_card').get('title')}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
