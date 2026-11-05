import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import DataRepository

client = TestClient(app)

def test_community_neon_cross_student_visibility():
    # 1. Student A reports a lost item
    student_a_roll = "251FA04E13"
    student_b_roll = "24CSE001"
    
    report_payload = {
        "student_id": student_a_roll,
        "type": "lost",
        "title": "Titan Black Watch",
        "description": "Lost near Pharmacy block cafeteria",
        "tags": "watch, accessories",
        "contact_info": "9876543210"
    }
    res = client.post("/api/v1/community/lost-and-found", json=report_payload)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data.get("success") is True
    item_id = res_data.get("id")
    assert item_id is not None

    try:
        # 2. Student B queries lost-and-found items
        # Community items must be visible to ANY student regardless of registration number
        fetch_res = client.get("/api/v1/community/lost-and-found")
        assert fetch_res.status_code == 200
        items = fetch_res.json().get("items", [])
        
        # Verify Student B can see Student A's reported item
        matched = next((item for item in items if item["id"] == item_id), None)
        assert matched is not None
        assert matched["title"] == "Titan Black Watch"
        assert matched["student_id"] == student_a_roll
        assert matched["status"] == "open"

        # 3. Student B creates a marketplace listing
        market_payload = {
            "student_id": student_b_roll,
            "title": "Engineering Chemistry 2nd Edition",
            "category": "Books",
            "price": 300.0
        }
        res_market = client.post("/api/v1/community/marketplace", json=market_payload)
        assert res_market.status_code == 200
        market_data = res_market.json()
        assert market_data.get("success") is True
        market_id = market_data.get("id")

        # 4. Student A queries marketplace and sees Student B's listing
        fetch_market = client.get("/api/v1/community/marketplace")
        assert fetch_market.status_code == 200
        listings = fetch_market.json().get("data", [])
        matched_market = next((l for l in listings if l["id"] == market_id), None)
        assert matched_market is not None
        assert matched_market["title"] == "Engineering Chemistry 2nd Edition"
        assert matched_market["student_id"] == student_b_roll

        # 5. Clean up marketplace test item
        DataRepository._execute_insert("DELETE FROM marketplace_listings WHERE id = ?", (market_id,))

    finally:
        # Clean up lost and found test item
        DataRepository._execute_insert("DELETE FROM lost_and_found WHERE id = ?", (item_id,))

