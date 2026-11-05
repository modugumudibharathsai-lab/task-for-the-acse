"""
Tests for Distress vs Crisis Handling (Requirement 5)
Verifies:
1. Keyword crisis check runs first and untouched. Emergency crisis keywords trigger
   the crisis overlay (is_distress=True, routed_by='rules').
2. An intent classifier prediction of 'distress_support' alone provides a supportive
   counseling reply WITHOUT triggering the crisis overlay (is_distress=False).
3. Neither path makes calls to external LLMs (Gemini is mocked).
"""

import pytest
from unittest.mock import patch, MagicMock
from app.database import DatabaseSession, DataRepository
from app.config import settings
from app.agent.orchestrator import VIGBOTOrchestrator
from app.agent.intent_classifier import IntentClassifierService
from app.agent.nlu_engine import NLUEngine


@pytest.fixture
def db_session():
    return DatabaseSession(
        student_id="eeeeeeee-0000-0000-0000-000000000001",
        user_id="11111111-0000-0000-0000-000000000001"
    )


def test_crisis_keyword_triggers_crisis_overlay(db_session):
    """
    Emergency crisis keyword phrase triggers crisis overlay (is_distress=True)
    at Step 1 before NLU dispatch, routing as 'rules'.
    """
    crisis_query = "I feel like ending my life"

    # Create authorized conversation for the session
    conv = DataRepository.create_conversation(db_session, title="Crisis Test")
    conv_id = conv["conversation_id"]

    with patch("app.agent.llm_client.LLMClient._send_gemini_chat") as mock_gemini, \
         patch("app.agent.llm_client.LLMClient._send_chat_with_provider") as mock_provider, \
         patch("app.agent.llm_client.LLMClient.classify_intent") as mock_gemini_intent, \
         patch("app.agent.llm_client.LLMClient.chat_with_history") as mock_gemini_chat:

        response = VIGBOTOrchestrator.process_message(
            session=db_session,
            conversation_id=conv_id,
            user_message=crisis_query,
            language="en"
        )

        # 1. Crisis overlay must be triggered
        assert response["is_distress"] is True
        assert response["routed_by"] == "rules"
        assert response["category"] in ("DISTRESS_SUPPORT", "CRISIS_INTERVENTION")
        assert "Tele-MANAS" in response["content"]
        assert "+91-98765-43210" in response["content"]

        # 2. Gemini must NEVER be called
        mock_gemini.assert_not_called()
        mock_provider.assert_not_called()
        mock_gemini_intent.assert_not_called()
        mock_gemini_chat.assert_not_called()


def test_classifier_distress_support_does_not_trigger_crisis_overlay(db_session):
    """
    A query without crisis keywords classified as 'distress_support' returns
    supportive counseling info with is_distress=False (NO crisis overlay).
    """
    non_crisis_distress_query = "I am feeling severely burned out and exhausted with the heavy academic workload"

    # Create authorized conversation for the session
    conv = DataRepository.create_conversation(db_session, title="Distress Support Test")
    conv_id = conv["conversation_id"]

    mock_clf_result = {
        "intent": "distress_support",
        "confidence": 0.88,
        "is_confident": True,
        "threshold": 0.40,
        "routed_by": "classifier"
    }

    with patch("app.agent.llm_client.LLMClient._send_gemini_chat") as mock_gemini, \
         patch("app.agent.llm_client.LLMClient._send_chat_with_provider") as mock_provider, \
         patch("app.agent.llm_client.LLMClient.classify_intent") as mock_gemini_intent, \
         patch("app.agent.llm_client.LLMClient.chat_with_history") as mock_gemini_chat, \
         patch.object(settings, "USE_INTENT_CLASSIFIER", True), \
         patch.object(IntentClassifierService, "get_instance") as mock_service_inst:

        mock_inst = MagicMock()
        mock_inst.classify.return_value = mock_clf_result
        mock_service_inst.return_value = mock_inst

        response = VIGBOTOrchestrator.process_message(
            session=db_session,
            conversation_id=conv_id,
            user_message=non_crisis_distress_query,
            language="en"
        )

        # 1. Must NOT trigger crisis overlay
        assert response["is_distress"] is False
        assert response["routed_by"] == "classifier"
        assert response["category"] == "DISTRESS_SUPPORT"

        # 2. Must provide supportive counseling information
        assert "counseling" in response["content"].lower() or "wellness" in response["content"].lower()

        # 3. Gemini must NEVER be called
        mock_gemini.assert_not_called()
        mock_provider.assert_not_called()
        mock_gemini_intent.assert_not_called()
        mock_gemini_chat.assert_not_called()


def test_nlu_direct_distress_support_flag(db_session):
    """
    Direct test on NLUEngine route_classified_intent for distress_support.
    Verifies is_distress is explicitly False in the structured payload.
    """
    mock_clf_result = {
        "intent": "distress_support",
        "confidence": 0.85,
        "is_confident": True,
        "threshold": 0.40,
        "routed_by": "classifier"
    }

    with patch("app.agent.llm_client.LLMClient._send_gemini_chat") as mock_gemini, \
         patch.object(settings, "USE_INTENT_CLASSIFIER", True), \
         patch.object(IntentClassifierService, "get_instance") as mock_service_inst:

        mock_inst = MagicMock()
        mock_inst.classify.return_value = mock_clf_result
        mock_service_inst.return_value = mock_inst

        response = NLUEngine.classify_and_reason(
            session=db_session,
            query="Can someone help me cope with severe exam stress and fatigue?",
            conversation_history=[],
            context_data={},
            language="en"
        )

        assert response["is_distress"] is False
        assert response["category"] == "DISTRESS_SUPPORT"
        assert response["routed_by"] == "classifier"
        assert "counselor" in response["content"].lower()
        mock_gemini.assert_not_called()
