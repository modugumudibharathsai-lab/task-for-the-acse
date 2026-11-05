"""
Unit test suite verifying the strict distinction between asking and doing across all VIGBOT capabilities.
Guarantees:
1. Strictly 0 false writes on informational queries.
2. Strictly 0 fabricated tracking numbers or success confirmations on informational queries.
3. Proper procedural guidance and frontend navigation actions for informational requests.
4. Correct execution/modal-guidance for explicit action requests.
"""

import pytest
from app.database import DatabaseSession, DataRepository
from app.agent.nlu_engine import NLUEngine
from app.agent.universal_nlu import UniversalNLU, CommunicationIntent


@pytest.fixture
def test_session():
    return DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")


def test_lost_and_found_asking_never_creates_service_ticket(test_session):
    queries = [
        "Where can I report something if I found?",
        "How do I report a lost calculator on campus?",
        "Where do I go if I lost my ID card?",
        "What is the procedure for claiming a found item?",
        "Can you tell me where found items are deposited?"
    ]
    for q in queries:
        res = NLUEngine.classify_and_reason(
            session=test_session,
            query=q,
            conversation_history=[],
            context_data={},
            language="en"
        )
        content = res.get("content", "")
        # MUST NOT create service request
        assert "SR-2026-" not in content, f"Fabricated ticket in response to: {q}"
        assert "Service Request Created Successfully" not in content, f"False action for query: {q}"
        assert res.get("redirect_path") == "lost-and-found", f"Expected redirect_path='lost-and-found', got {res.get('redirect_path')}"
        assert res.get("action") is not None
        assert res["action"].get("target") == "lost-and-found"


def test_services_bonafide_asking_vs_doing(test_session):
    # Asking where/how should provide guidance and navigation, NOT create ticket
    info_query = "Where do I go to get a bonafide certificate?"
    res_info = NLUEngine.classify_and_reason(
        session=test_session,
        query=info_query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    content_info = res_info.get("content", "")
    assert "SR-2026-" not in content_info, "False write occurred for asking where to get bonafide"
    assert "Service Request Created Successfully" not in content_info
    assert res_info.get("redirect_path") == "services"
    assert res_info.get("action") is not None

    # Doing: explicit application should create verified ticket
    action_query = "Apply for bonafide certificate for passport verification"
    res_action = NLUEngine.classify_and_reason(
        session=test_session,
        query=action_query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    content_action = res_action.get("content", "")
    assert "SR-2026-" in content_action or res_action.get("category") == "SERVICE_REQUEST"
    assert res_action.get("structured_card") is not None


def test_facility_booking_asking_never_reserves(test_session):
    queries = [
        "Where can I book the seminar hall?",
        "How do I reserve the cricket ground for Saturday?",
        "What is the process to book the auditorium?"
    ]
    for q in queries:
        res = NLUEngine.classify_and_reason(
            session=test_session,
            query=q,
            conversation_history=[],
            context_data={},
            language="en"
        )
        content = res.get("content", "")
        assert "Booking Confirmed" not in content
        assert "SR-2026-" not in content
        assert res.get("redirect_path") == "bookings"


def test_grievance_asking_vs_filing(test_session):
    # Asking for procedure
    info_query = "Where do I lodge a grievance regarding faculty evaluation?"
    res_info = NLUEngine.classify_and_reason(
        session=test_session,
        query=info_query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    content_info = res_info.get("content", "")
    assert "SR-2026-" not in content_info
    assert res_info.get("redirect_path") == "services"

    # Anti-ragging emergency notice
    ragging_query = "Where can I report ragging on campus?"
    res_ragging = NLUEngine.classify_and_reason(
        session=test_session,
        query=ragging_query,
        conversation_history=[],
        context_data={},
        language="en"
    )
    assert "1800-180-5522" in res_ragging.get("content", "")
    assert res_ragging.get("redirect_path") == "services"


def test_negative_intent_preventing_unwanted_writes(test_session):
    queries = [
        "Don't submit anything, just tell me where I can get an ID card replacement",
        "Do not create a ticket, just explain how bus pass is renewed",
        "Don't book anything, tell me how seminar hall reservations work"
    ]
    for q in queries:
        intent = UniversalNLU.parse_communication_intent(q)
        assert intent == CommunicationIntent.INFORMATION_REQUEST, f"Failed negative intent parse for: {q}"
        res = NLUEngine.classify_and_reason(
            session=test_session,
            query=q,
            conversation_history=[],
            context_data={},
            language="en"
        )
        content = res.get("content", "")
        assert "SR-2026-" not in content, f"False action on negative query: {q}"
        assert "Created Successfully" not in content

