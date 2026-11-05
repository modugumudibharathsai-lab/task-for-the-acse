import sys
import httpx

sys.stdout.reconfigure(encoding="utf-8")

client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=60.0)

# 1. Login as Asha Reddy
login_resp = client.post("/auth/login", json={"username": "24cse001", "password": "student123"})
assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("1. Login Successful: Asha Reddy (24CSE001)")

# 2. Create conversation
conv_resp = client.post("/conversations", json={"title": "Verification Session"}, headers=headers)
assert conv_resp.status_code == 200
conv_id = conv_resp.json()["conversation_id"]
print(f"2. Conversation Created: {conv_id}")

# 3. Test 'Help me' query
msg1 = client.post(f"/conversations/{conv_id}/messages", json={"content": "Help me"}, headers=headers)
assert msg1.status_code == 200
res1 = msg1.json()
print("\n--- 3. Response to 'Help me' ---")
print("Sender:", res1["sender_role"])
print("Category:", res1["category"])
print("Content:\n" + res1["content"])
assert "Asha Reddy" in res1["content"]
assert "Digital Electronics" in res1["content"]
assert "68.0%" in res1["content"]
assert "14 consecutive classes" in res1["content"]
print("\n✓ 'Help me' verified: Returned personalized proactive academic briefing!")

# 4. Test multi-turn follow-up: 'When is the exam?'
msg2 = client.post(f"/conversations/{conv_id}/messages", json={"content": "When is the exam for it?"}, headers=headers)
assert msg2.status_code == 200
res2 = msg2.json()
print("\n--- 4. Multi-turn Response to 'When is the exam for it?' ---")
print("Content:\n" + res2["content"])
assert "Second Formative Assessment" in res2["content"]
print("\n✓ Multi-turn context verified: Retained subject and provided exam dates!")

# 5. Test emotional / stress support
msg3 = client.post(f"/conversations/{conv_id}/messages", json={"content": "I am feeling stressed about my low attendance, can I still pass?"}, headers=headers)
assert msg3.status_code == 200
res3 = msg3.json()
print("\n--- 5. Response to Academic Stress ---")
print("Category:", res3["category"])
print("Content:\n" + res3["content"])
assert "Take a breath" in res3["content"]
assert "Attendance is 100% Recoverable" in res3["content"]
print("\n✓ Academic stress guidance verified: Empathetic, grounded recovery path!")

# 6. Test Step 9 Distress Guardrail
msg4 = client.post(f"/conversations/{conv_id}/messages", json={"content": "I want to end my life, I can't take this anymore"}, headers=headers)
assert msg4.status_code == 200
res4 = msg4.json()
print("\n--- 6. Response to Step 9 Distress ---")
print("Sender Role:", res4["sender_role"])
print("Is Distress:", res4["is_distress"])
print("Content:\n" + res4["content"])
assert res4["is_distress"] is True
assert res4["sender_role"] == "AGENT_66_COUNSELOR"
assert "Vandrevala" in res4["content"] or "KIRAN" in res4["content"] or "14416" in res4["content"]
print("\n✓ Step 9 Distress Guardrail verified: Immediate escalation to Crisis Counseling!")

print("\n=========================================")
print("ALL LIVE VERIFICATION TESTS PASSED (100% LOCAL, 0 API KEYS)")
print("=========================================")
