from typing import Dict, Any, List, Optional
from app.database import DataRepository, DatabaseSession
from app.tools.distress_tool import detect_distress, silent_mock_alert_counselor
from app.agent.nlu_engine import NLUEngine
from app.agent.llm_client import LLMClient

class VIGBOTOrchestrator:
    """
    VIGBOT Orchestrator.
    Fulfills all 10 workflow steps and non-negotiable security guardrails:
    1. Authenticated student identity boundary (Session-bound RLS).
    2. Real-time cognitive Intent Classification & Entity Extraction.
    3. Row-level security at data layer.
    4. Actionable answers with recovery math, formulas, and deadlines.
    5. Multi-turn context preservation.
    6. Multilingual support.
    7. Service request actions.
    8. Human administrative escalations (Step 8).
    9. Mandatory distress detection & crisis routing.
    10. Privacy-safe aggregated query pattern analytics.
    """

    @classmethod
    def process_message(
        cls,
        session: DatabaseSession,
        conversation_id: str,
        user_message: str,
        language: str = "en",
        selected_model: str = "8B"
    ) -> Dict[str, Any]:
        query = user_message.strip()

        is_distress_detected = False
        # ---------------- 1. MANDATORY SAFETY GUARDRAIL (Workflow Step 9) ----------------
        if detect_distress(query):
            is_distress_detected = True
            
            # Remove silent_mock_alert_counselor and use handle_crisis_escalation instead
            from app.tools.distress_tool import handle_crisis_escalation
            crisis_response = handle_crisis_escalation(session, query)

            # ---------------- 3. RECORD STUDENT MESSAGE ----------------
            DataRepository.add_message(session, conversation_id, {
                "sender_role": "STUDENT",
                "content": query,
                "category": "DISTRESS_SUPPORT",
                "is_distress": True
            })

            # Log anonymous metric (Step 10)
            DataRepository.record_query_metric(
                intent_category="DISTRESS_SUPPORT",
                topic="Mental Health Crisis Intervention",
                language=language,
                is_distress=True
            )

            # ---------------- 6. PERSIST AGENT RESPONSE IN DB ----------------
            agent_msg = DataRepository.add_message(session, conversation_id, {
                "sender_role": "VIGBOT",
                "content": crisis_response["text"],
                "category": crisis_response["category"],
                "source_agent": crisis_response["source_agent"],
                "citations": [],
                "structured_card": crisis_response.get("structured_card"),
                "is_distress": True
            })

            return {
                "message_id": agent_msg["message_id"],
                "conversation_id": conversation_id,
                "sender_role": "VIGBOT",
                "content": crisis_response["text"],
                "category": crisis_response["category"],
                "source_agent": crisis_response["source_agent"],
                "citations": [],
                "structured_card": crisis_response.get("structured_card"),
                "is_distress": True,
                "suggested_follow_ups": [],
                "llm_provider": "system",
                "model_used": "rules",
                "used_fallback": False,
                "routed_by": "rules",
                "redirect_path": None,
                "action": None,
                "created_at": agent_msg["created_at"]
            }

        # ---------------- 2. MULTI-TURN CONTEXT RESOLUTION (Workflow Step 5) ----------------
        history = DataRepository.get_conversation_messages(session, conversation_id)
        conv = DataRepository.get_conversation(session, conversation_id)
        context_data = conv.get("context_data", {}) if conv else {}

        # ---------------- 3. RECORD STUDENT MESSAGE ----------------
        DataRepository.add_message(session, conversation_id, {
            "sender_role": "STUDENT",
            "content": query,
            "category": "GENERAL" if not is_distress_detected else "DISTRESS_SUPPORT",
            "is_distress": is_distress_detected
        })

        # ---------------- 4. LOCAL NLU REASONING & TOOL DISPATCH ----------------
        nlu_result = NLUEngine.classify_and_reason(
            session=session,
            query=query,
            conversation_history=history,
            context_data=context_data,
            language=language,
            selected_model=selected_model
        )

        # Update conversational memory context
        if conv and nlu_result.get("active_subject"):
            conv.setdefault("context_data", {})["active_subject"] = nlu_result["active_subject"]
            DataRepository.update_conversation_context(session, conversation_id, conv["context_data"])

        # ---------------- 5. RECORD PRIVACY-SAFE ANALYTICS (Workflow Step 10) ----------------
        DataRepository.record_query_metric(
            intent_category=nlu_result.get("category", "GENERAL"),
            topic=nlu_result.get("topic", "General Inquiry"),
            language=language,
            is_distress=False
        )

        # ---------------- 6. PERSIST AGENT RESPONSE IN DB ----------------
        clean_content = LLMClient.clean_latex_formatting(nlu_result.get("content", ""))
        agent_msg = DataRepository.add_message(session, conversation_id, {
            "sender_role": "VIGBOT",
            "content": clean_content,
            "category": nlu_result.get("category", "GENERAL"),
            "source_agent": nlu_result.get("source_agent", "VIGBOT"),
            "citations": nlu_result.get("citations", []),
            "structured_card": nlu_result.get("structured_card"),
            "is_distress": False
        })

        return {
            "message_id": agent_msg["message_id"],
            "conversation_id": conversation_id,
            "sender_role": "VIGBOT",
            "content": clean_content,
            "category": nlu_result.get("category", "GENERAL"),
            "source_agent": nlu_result.get("source_agent", "VIGBOT"),
            "citations": nlu_result.get("citations", []),
            "structured_card": nlu_result.get("structured_card"),
            "is_distress": False,
            "suggested_follow_ups": nlu_result.get("suggested_follow_ups", []),
            "llm_provider": nlu_result.get("llm_provider", "local"),
            "model_used": nlu_result.get("model_used", "unknown"),
            "used_fallback": nlu_result.get("used_fallback", False),
            "routed_by": nlu_result.get("routed_by", "rules"),
            "redirect_path": nlu_result.get("redirect_path"),
            "action": nlu_result.get("action"),
            "created_at": agent_msg["created_at"]
        }


VigbotOrchestrator = VIGBOTOrchestrator
Agent65Orchestrator = VIGBOTOrchestrator
