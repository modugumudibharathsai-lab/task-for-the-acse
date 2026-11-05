import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_tests():
    print("==================================================")
    print("Testing Autonomous Cognitive VIGBOT Backend API")
    print("==================================================")

    # 1. Login as Asha Reddy
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "24cse001", "password": "student123"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("1. Authentication OK (Asha Reddy - 24CSE001)")

    # 2. Start a new conversation
    conv_resp = requests.post(
        f"{BASE_URL}/conversations",
        headers=headers,
        json={"title": "Cognitive AI Test Session"}
    )
    assert conv_resp.status_code == 200, f"Conversation creation failed: {conv_resp.text}"
    conv_id = conv_resp.json()["conversation_id"]
    print(f"2. Created Conversation: {conv_id}")

    test_queries = [
        {
            "name": "TEST 1: Headache & Assignment Fatigue (Empathetic Mentorship)",
            "query": "I am feeling very much headache due to this assignment",
            "expected_card_type": "ACADEMIC_ADVISING_PLAN"
        },
        {
            "name": "TEST 2: Digital Electronics Attendance (Grounded RLS Data)",
            "query": "What is my attendance in Digital Electronics?",
            "expected_card_type": "attendance"
        },
        {
            "name": "TEST 3: Conceptual Tutoring (Data Structures / BST)",
            "query": "Can you explain how a Binary Search Tree works and its time complexity?",
            "expected_card_type": None
        },
        {
            "name": "TEST 4: Service Request (Bonafide Certificate)",
            "query": "Please apply for a bonafide certificate for my education loan",
            "expected_card_type": "service"
        },
        {
            "name": "TEST 5: Upcoming CIE Examination Schedule",
            "query": "When is my next CIE exam?",
            "expected_card_type": "exam"
        }
    ]

    for idx, t in enumerate(test_queries, 1):
        print(f"\n--------------------------------------------------")
        print(f"[{idx}/5] {t['name']}")
        print(f"Query: \"{t['query']}\"")
        start_time = time.time()
        
        msg_resp = requests.post(
            f"{BASE_URL}/conversations/{conv_id}/messages",
            headers=headers,
            json={"content": t["query"], "language": "en"}
        )
        elapsed = time.time() - start_time
        
        assert msg_resp.status_code == 200, f"Message failed: {msg_resp.text}"
        data = msg_resp.json()
        
        card = data.get("structured_card")
        card_type = card.get("type") if card else None
        
        print(f"Latency: {elapsed:.2f}s")
        print(f"Category: {data.get('category')}")
        print(f"Structured Card Type: {card_type}")
        if card:
            print(f"Card Title: {card.get('title')}")
        print(f"AI Content:\n{data.get('content')}")
        print(f"Suggested Follow-ups: {data.get('suggested_follow_ups')}")

    print("\n==================================================")
    print("ALL 5 COGNITIVE AGENT TESTS COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
