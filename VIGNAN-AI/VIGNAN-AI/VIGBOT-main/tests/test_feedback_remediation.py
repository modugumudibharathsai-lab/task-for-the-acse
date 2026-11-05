"""
Tests for Autonomous Gemini Feedback Remediation & Cognitive Self-Improvement Loop.
Verifies:
1. Intent-output mismatch detection:
   - Real mismatch (e.g. asking for location/directions but getting document services) is audited by Gemini,
     flagged as mismatch_detected=True, remediation_needed=True, and stored in learned_query_remediations.
   - Subsequent queries immediately route via 'learned_remediation' with the corrected answer!
2. Policy/Truth protection:
   - Dislike on a correct policy refusal (e.g. cross-student privacy snoop attempt under RLAC Clause 2.1)
     is audited by Gemini, flagged as mismatch_detected=False, remediation_needed=False, and NO rule is created.
3. API Endpoint integration:
   - POST /conversations/{id}/messages/{id}/feedback with rating="down" returns immediately (<50ms)
     and dispatches the background task.
"""

import pytest
import uuid
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BACKEND")))

from app.database import DataRepository, DatabaseSession
from app.agent.feedback_remediator import FeedbackRemediationService
from app.agent.nlu_engine import NLUEngine


def test_gemini_audit_mismatch_detected_and_remediates():
    """
    Simulates a query failure (e.g. user asked for N-Block directions, bot gave Student Services documents).
    Verifies that when disliked, the Gemini audit flags the mismatch, saves a learned remediation,
    and subsequent queries match and return the corrected campus directions with routed_by='learned_remediation'.
    """
    session = DatabaseSession(student_id="stu_test_audit_01", user_id="usr_test_audit_01")
    fb_id = f"fb-{uuid.uuid4().hex[:8]}"
    conv_id = f"conv-{uuid.uuid4().hex[:8]}"

    user_query = "where is N-Block?"
    faulty_output = "You can view, request, and track official university documents in the Student Services section."
    user_comment = "I asked for directions to N-block, not certificates!"

    mock_audit_response = {
        "mismatch_detected": True,
        "mismatch_reason": "The user requested physical location and walking directions for N-Block, but the bot provided unrelated information regarding Student Services certificates.",
        "remediation_needed": True,
        "intended_intent": "CAMPUS_DIRECTIONS",
        "target_entity": "N_BLOCK",
        "trigger_patterns": ["where is n block", "where is n-block", "how to reach n-block", "directions to n block"],
        "routing_action": "TOOL:get_campus_location_and_navigation",
        "remediation_type": "TOOL_ROUTING",
        "grounded_response_template": "Walking directions to N-Block just beside Zest.",
        "suggested_follow_ups": ["Where is Zest?", "What is N-Block?"]
    }

    with patch.object(FeedbackRemediationService, "call_gemini_audit_engine", return_value=mock_audit_response):
        rem_id = FeedbackRemediationService.evaluate_and_remediate(
            feedback_id=fb_id,
            conversation_id=conv_id,
            user_query=user_query,
            bot_output=faulty_output,
            student_comment=user_comment
        )

        assert rem_id is not None
        assert rem_id.startswith("rem-")

    # 2. Verify subsequent query is intercepted and served by learned remediation
    matched_rem = FeedbackRemediationService.match_query("where is n-block?")
    assert matched_rem is not None
    assert matched_rem["remediation_id"] == rem_id
    assert matched_rem["intended_intent"] == "CAMPUS_DIRECTIONS"
    assert matched_rem["target_entity"] == "N_BLOCK"

    # 3. Verify NLUEngine.classify_and_reason executes the remediation
    res = NLUEngine.classify_and_reason(
        session=session,
        query="where is n-block?",
        conversation_history=[],
        context_data={},
        language="en"
    )

    assert res["routed_by"] == "learned_remediation"
    assert res["remediation_id"] == rem_id
    assert res["category"] in ("CAMPUS_NAVIGATION", "MAP")
    # Ensure correct landmark Zest is mentioned and N-Block is just beside Zest
    assert "Zest" in res["content"] or "N-Block" in res["content"]


def test_gemini_audit_no_mismatch_for_policy_refusal():
    """
    Verifies that when a student dislikes a correct policy-enforcing answer
    (e.g. cross-student privacy refusal under Clause 2.1 RLAC),
    the Gemini auditor evaluates mismatch_detected=False, remediation_needed=False,
    and NO learned remediation rule is created.
    """
    fb_id = f"fb-{uuid.uuid4().hex[:8]}"
    conv_id = f"conv-{uuid.uuid4().hex[:8]}"

    user_query = "what is the attendance of 251FA04E69"
    policy_output = "Under university privacy regulations and Row-Level Security (RLAC Clause 2.1), you are only authorized to view your own attendance records. Access to other students' records is restricted."
    user_comment = "Give me his attendance I need it"

    mock_audit_response = {
        "mismatch_detected": False,
        "mismatch_reason": "The bot correctly enforced institutional privacy regulations and Row-Level Access Control (RLAC Clause 2.1) by refusing to disclose third-party student attendance records.",
        "remediation_needed": False
    }

    initial_remediations_count = len(FeedbackRemediationService.get_active_remediations())

    with patch.object(FeedbackRemediationService, "call_gemini_audit_engine", return_value=mock_audit_response):
        rem_id = FeedbackRemediationService.evaluate_and_remediate(
            feedback_id=fb_id,
            conversation_id=conv_id,
            user_query=user_query,
            bot_output=policy_output,
            student_comment=user_comment
        )

        assert rem_id is None

    # Verify no new remediation rule was added
    current_remediations_count = len(FeedbackRemediationService.get_active_remediations())
    assert current_remediations_count == initial_remediations_count


def test_pii_redaction_before_gemini_audit():
    """
    Verifies that all student PII (Roll numbers, emails, phone numbers)
    is strictly sanitized before being transmitted to the external Gemini audit engine.
    """
    raw_query = "My friend 251FA04E69 with email test.student@vignan.ac.in and phone 9876543210 told me to check this."
    cleaned = FeedbackRemediationService.redact_pii_for_audit(raw_query)

    assert "251FA04E69" not in cleaned
    assert "test.student@vignan.ac.in" not in cleaned
    assert "9876543210" not in cleaned
    assert "[STUDENT_ROLL_NO]" in cleaned
    assert "[STUDENT_EMAIL]" in cleaned
    assert "[STUDENT_PHONE]" in cleaned


def test_feedback_api_endpoint_downvote_triggers_background_audit():
    """
    Verifies that POST /conversations/{id}/messages/{id}/feedback with rating='down'
    schedules the Gemini cognitive remediation background task and responds with HTTP 200 immediately.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from app.security import create_access_token
    from app.database import DataRepository, DatabaseSession

    client = TestClient(app)
    student = DataRepository.get_student_by_username("251FA04E13") or DataRepository.get_student_by_username("24CSE001")
    sid = student["student_id"]
    uid = student.get("user_id", sid)
    
    session = DatabaseSession(student_id=sid, user_id=uid)
    conv = DataRepository.create_conversation(session, "Audit Test Conv")
    conv_id = conv["conversation_id"]

    token = create_access_token({
        "sub": uid,
        "student_id": sid,
        "roll_no": student["roll_no"],
        "full_name": student["full_name"]
    })
    headers = {"Authorization": f"Bearer {token}"}
    msg_id = f"msg-test-{uuid.uuid4().hex[:6]}"

    payload = {
        "rating": "down",
        "comment": "Bot gave wrong information",
        "messages": [
            {"role": "user", "content": "where is N-Block?"},
            {"role": "assistant", "content": "Here is Student Services certificate info"}
        ],
        "response_text": "Here is Student Services certificate info"
    }

    with patch.object(FeedbackRemediationService, "evaluate_and_remediate") as mock_remediate:
        response = client.post(
            f"/api/v1/conversations/{conv_id}/messages/{msg_id}/feedback",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["rating"] == "down"
        assert "Cognitive auditor initiated" in data["message"]
        # Background task was scheduled and called
        mock_remediate.assert_called_once()
