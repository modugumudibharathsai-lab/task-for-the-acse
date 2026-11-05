import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
student_roll = "251FA04F90" # Kishan Kumar
password = "student123" # usually the roll no or student123

print(f"Logging in as {student_roll}...")
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": student_roll, "password": student_roll}
)
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    sys.exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login OK.")

conv_resp = requests.post(
    f"{BASE_URL}/conversations",
    headers=headers,
    json={"title": "Test Session"}
)
if conv_resp.status_code != 200:
    print(f"Conversation creation failed: {conv_resp.text}")
    sys.exit(1)
conv_id = conv_resp.json()["conversation_id"]
print(f"Created Conversation: {conv_id}")

query = "What is the syllabus for the upcoming Database Management Systems exam?"
print(f"\nSending Query: {query}")
msg_resp = requests.post(
    f"{BASE_URL}/conversations/{conv_id}/messages",
    headers=headers,
    json={"content": query, "language": "en"}
)

if msg_resp.status_code != 200:
    print(f"Message failed: {msg_resp.text}")
    sys.exit(1)

data = msg_resp.json()
print(f"\n--- AI RESPONSE ---")
print(data.get("content"))
print(f"-------------------")
print(f"Category: {data.get('category')}")
print(f"Source Agent: {data.get('source_agent')}")

print("\nChecking training_data.jsonl for new entry...")
with open("C:/StudentHelpdesk/scratch/../BACKEND/training_data.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()
    if len(lines) > 0:
        last_line = lines[-1]
        print(f"Last training data entry length: {len(last_line)} characters.")
        if "Database Management Systems exam" in last_line:
            print("SUCCESS: The prompt was recorded in the training data.")
        else:
            print("WARNING: The prompt might not have been recorded in the last line.")
