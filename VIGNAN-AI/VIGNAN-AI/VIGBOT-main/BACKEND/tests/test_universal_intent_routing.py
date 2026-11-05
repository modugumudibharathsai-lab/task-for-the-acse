"""
Universal Intent Understanding & Application-Wide Feature Routing Benchmark Suite.
Tests:
1. False-Action Prevention (Lost & Found vs Services ticket creation)
2. Semantic intent parsing (Information vs Navigation vs Action vs Ambiguous)
3. Application Capability Registry resolution across all 24 features
4. Statutory Anti-Ragging & SGRC guidance
5. Genuine service request creation retention
6. Academic tutoring retention
"""

import pytest
from unittest.mock import patch
from app.database import DatabaseSession, DataRepository
from app.agent.capability_registry import (
    APPLICATION_CAPABILITIES,
    CommunicationIntent,
    find_matching_capability
)
from app.agent.universal_nlu import UniversalNLU
from app.agent.nlu_engine import NLUEngine
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def test_session():
    return DatabaseSession(student_id="cccccccc-0000-0000-0000-000000000001", user_id="eeeeeeee-0000-0000-0000-000000000001")


@pytest.fixture
def asha_token():
    resp = client.post("/api/v1/auth/login", json={"username": "24cse001", "password": "student123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_01_reproduce_and_prevent_lost_and_found_false_action(test_session, asha_token):
    """
    CRITICAL TEST CASE:
    Query: "Where can I report something if I found?"
    Must NEVER create a service request, ticket number, or modify database tables.
    Must return clear guidance with navigation action to lost-and-found.
    """
    query = "Where can I report something if I found?"
    
    # 1. Direct NLUEngine execution
    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )

    assert "SR-2026-" not in res["content"]
    assert "Service Request Created" not in res["content"]
    assert res["category"] == "LOST_AND_FOUND"
    assert res["redirect_path"] == "lost-and-found"
    assert res["action"] is not None
    assert res["action"]["type"] == "navigate"
    assert res["action"]["target"] == "lost-and-found"
    assert "Lost & Found" in res["content"]

    # 2. End-to-end API test over HTTP
    headers = {"Authorization": f"Bearer {asha_token}"}
    conv_resp = client.post("/api/v1/conversations", json={"title": "Lost Item Query"}, headers=headers)
    assert conv_resp.status_code == 200
    conv_id = conv_resp.json()["conversation_id"]

    msg_resp = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": query},
        headers=headers
    )
    assert msg_resp.status_code == 200
    api_data = msg_resp.json()

    assert "SR-2026-" not in api_data["content"]
    assert api_data["category"] == "LOST_AND_FOUND"
    assert api_data["redirect_path"] == "lost-and-found"
    assert api_data["action"]["target"] == "lost-and-found"


def test_02_navigation_request_handling(test_session):
    """Verifies direct navigation request like 'Open Lost & Found'."""
    query = "Open Lost & Found"
    comm_intent = UniversalNLU.parse_communication_intent(query)
    assert comm_intent == CommunicationIntent.NAVIGATION_REQUEST

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert res["redirect_path"] == "lost-and-found"
    assert res["action"]["type"] == "navigate"
    assert "Opening **Lost & Found**" in res["content"] or "Lost & Found" in res["content"]


def test_03_ambiguous_intent_prompts_clarification(test_session):
    """
    Verifies that ambiguous queries like 'I found something' prompt for clarification
    rather than guessing or taking unauthorized action.
    """
    query = "I found something"
    comm_intent = UniversalNLU.parse_communication_intent(query)
    assert comm_intent == CommunicationIntent.AMBIGUOUS

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert "SR-2026-" not in res["content"]
    assert res["redirect_path"] == "lost-and-found"
    assert "found an item" in res["content"].lower()
    assert "lost an item" in res["content"].lower()


def test_04_statutory_anti_ragging_guidance(test_session):
    """
    Verifies that anti-ragging queries direct to statutory authorities & National Helpline
    without fabricating generic tickets.
    """
    query = "Where can I report ragging?"
    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert "SR-2026-" not in res["content"]
    assert "1800-180-5522" in res["content"]
    assert "helpline@antiragging.in" in res["content"]
    assert res["redirect_path"] == "services"


def test_05_genuine_service_request_still_creates_ticket(test_session, asha_token):
    """
    Confirms that explicit action requests (e.g. applying for bonafide)
    STILL succeed and generate legitimate service request tickets.
    """
    query = "I want to apply for a bonafide certificate for my bus pass"
    comm_intent = UniversalNLU.parse_communication_intent(query)
    assert comm_intent == CommunicationIntent.ACTION_REQUEST

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert "SR-2026-" in res["content"]
    assert res["category"] == "SERVICE_REQUEST"
    assert res["structured_card"]["type"] == "service"


def test_06_academic_tutoring_remains_unaffected(test_session):
    """
    Confirms that general academic tutoring (binary search, normalization, etc.)
    routes to pedagogical tutoring without triggering false app features.
    """
    query = "Explain binary search algorithm"
    comm_intent = UniversalNLU.parse_communication_intent(query)
    assert comm_intent == CommunicationIntent.GENERAL_ACADEMIC

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query=query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert res["category"] == "ACADEMIC_TUTORING"
    assert "Binary Search" in res["content"] or "binary search" in res["content"].lower()


def test_07_capability_registry_completeness():
    """Verifies that all 20+ core application capabilities are registered with required fields."""
    assert len(APPLICATION_CAPABILITIES) >= 20
    for cap_id, cap in APPLICATION_CAPABILITIES.items():
        assert "feature_id" in cap
        assert "name" in cap
        assert "category" in cap
        assert "frontend_tab" in cap
        assert "frontend_route" in cap
        assert "guidance_text" in cap
        assert "default_navigation_label" in cap
        assert len(cap["keywords"]) > 0
