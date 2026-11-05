"""
Unit test suite verifying multi-turn conversation context, anaphora resolution,
topic transitions, cancellation, and truthful status tracking in VIGBOT.
"""

import pytest
from app.database import DatabaseSession
from app.agent.nlu_engine import NLUEngine
from app.agent.universal_nlu import UniversalNLU, CommunicationIntent


@pytest.fixture
def test_session():
    return DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")


def test_multiturn_anaphora_open_it(test_session):
    # Turn 1: User asks where to report lost belongings
    history = [
        {"role": "user", "content": "Where can I report a lost calculator?"},
        {
            "role": "assistant",
            "content": "You can report or browse lost belongings in the Lost & Found section.",
            "redirect_path": "lost-and-found"
        }
    ]

    # Turn 2: User says "open it"
    resolved_cap = UniversalNLU.resolve_contextual_capability("open it", history)
    assert resolved_cap is not None
    assert resolved_cap["feature_id"] == "lost-and-found"

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="open it",
        conversation_history=history,
        context_data={},
        language="en"
    )
    assert res.get("redirect_path") == "lost-and-found"
    assert res.get("action") is not None
    assert res["action"].get("target") == "lost-and-found"


def test_multiturn_anaphora_take_me_there(test_session):
    history = [
        {"role": "user", "content": "How do I check my timetable for today?"},
        {
            "role": "assistant",
            "content": "You can view your daily class routine in the Timetable section.",
            "redirect_path": "timetable"
        }
    ]

    resolved_cap = UniversalNLU.resolve_contextual_capability("take me there", history)
    assert resolved_cap is not None
    assert resolved_cap["feature_id"] == "timetable"

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="take me there",
        conversation_history=history,
        context_data={},
        language="en"
    )
    assert res.get("redirect_path") == "timetable"


def test_multiturn_hinglish_kholo(test_session):
    history = [
        {"role": "user", "content": "Where can I check my marks?"},
        {
            "role": "assistant",
            "content": "You can check your CIE marks and CGPA in Marks & CGPA.",
            "redirect_path": "marks"
        }
    ]

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="kholo isko",
        conversation_history=history,
        context_data={},
        language="hi"
    )
    assert res.get("redirect_path") == "marks"


def test_multiturn_cancellation(test_session):
    history = [
        {"role": "user", "content": "I want to apply for a bonafide certificate"},
        {"role": "assistant", "content": "Please provide the purpose for your certificate."}
    ]

    intent = UniversalNLU.parse_communication_intent("actually cancel that, don't submit", history)
    assert intent == CommunicationIntent.CANCEL_REQUEST

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="actually cancel that, don't submit",
        conversation_history=history,
        context_data={},
        language="en"
    )
    content = res.get("content", "")
    assert "cancel" in content.lower() or "aborted" in content.lower()
    assert "SR-2026-" not in content


def test_multiturn_topic_switch_to_academic_tutoring(test_session):
    history = [
        {"role": "user", "content": "What is my attendance in DBMS?"},
        {"role": "assistant", "content": "Your attendance in Database Management Systems is 84.6%."}
    ]

    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="Explain B+ Tree indexing with a simple diagram",
        conversation_history=history,
        context_data={"active_subject": "Database Management Systems"},
        language="en"
    )
    # Must seamlessly route to academic tutoring without crashing or assuming attendance context
    assert res.get("category") == "ACADEMIC_TUTORING"
    assert len(res.get("content", "")) > 50


def test_status_lookup_without_hallucinating(test_session):
    # Non-existent ticket query should indicate no record found or direct to services desk,
    # NEVER fabricate a fake status confirmation
    res = NLUEngine.classify_and_reason(
        session=test_session,
        query="Track my ticket SR-9999-9999",
        conversation_history=[],
        context_data={},
        language="en"
    )
    content = res.get("content", "")
    assert "No active request found matching ticket 'SR-9999-9999'" in content or res.get("redirect_path") == "services"

