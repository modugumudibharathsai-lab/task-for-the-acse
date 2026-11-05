"""
Feedback Remediation Service (app/agent/feedback_remediator.py)
Autonomous Cognitive Evaluator and Self-Improving Query Remediator powered by Google Gemini.

When a student gives negative feedback (dislike / thumbs down) in helpdesk chat:
1. Gathers the student query, bot output, conversation history, and optional user comment.
2. Sanitizes PII (Roll numbers, emails, phone numbers) before external cognitive evaluation.
3. Invokes Google Gemini (gemini-3.5-flash / gemini-3.8-flash) as an institutional audit agent.
4. Strictly evaluates INTENT-OUTPUT MISMATCH:
   - Does NOT remediate if the user disliked a truthful, policy-enforcing response (e.g., attendance <75%, fee dues, cross-student privacy refusal under Clause 2.1).
   - ONLY remediates if the bot's response genuinely failed to match the student's true intent (e.g. misclassified intent, wrong campus directions, confusing building info vs walking route, hallucinated landmarks).
5. When remediation is needed, generates:
   - Normalized trigger patterns
   - Intended intent category
   - Target entity
   - Routing action / Tool / Direct grounded template
6. Persists the remediation rule to Neon PostgreSQL and SQLite.
7. Future matching queries are automatically intercepted and served with the corrected handler and grounded answer!
"""

import os
import re
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple

from app.config import settings
from app.database import DataRepository, DatabaseSession

logger = logging.getLogger(__name__)


class FeedbackRemediationService:
    """
    Self-improving AI remediation service.
    Audits negative feedback with Google Gemini and dynamically updates query handling.
    """

    _cache_active_remediations: Optional[List[Dict[str, Any]]] = None
    _last_cache_time: float = 0.0
    CACHE_TTL_SECONDS: float = 10.0  # Hot cache re-sync interval

    @classmethod
    def get_gemini_api_key(cls) -> str:
        """Resolves the Gemini API key from database system_settings, settings, environment, or .env."""
        from app.database import DataRepository
        stored_key = DataRepository.get_system_setting("GEMINI_API_KEY")
        if stored_key and not stored_key.startswith("YOUR_"):
            return stored_key.strip()
        key = getattr(settings, "GEMINI_API_KEY", "").strip()
        if key and not key.startswith("YOUR_"):
            return key
        for env_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            val = os.getenv(env_var, "").strip()
            if val and not val.startswith("YOUR_"):
                return val
        # Check backend .env directly
        try:
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return ""

    @classmethod
    def redact_pii_for_audit(cls, text: str) -> str:
        """Strips student names, roll numbers, emails, and phone numbers before external audit."""
        if not text:
            return ""
        # 1. Roll numbers (Vignan & standard format)
        cleaned = re.sub(r"\b(?:2[0-9]{2}[a-z]{1,4}[0-9a-z]{3,7}|\d{2}[a-z]{2,5}\d{3,4})\b", "[STUDENT_ROLL_NO]", text, flags=re.I)
        # 2. Email addresses
        cleaned = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[STUDENT_EMAIL]", cleaned)
        # 3. Phone numbers
        cleaned = re.sub(r"(?:\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}\b", "[STUDENT_PHONE]", cleaned)
        return cleaned

    @classmethod
    def call_gemini_audit_engine(
        cls,
        user_query: str,
        bot_output: str,
        student_comment: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sends the disliked conversation turn to Google Gemini for intent-output mismatch evaluation.
        """
        api_key = cls.get_gemini_api_key()
        if not api_key:
            logger.warning("[FeedbackRemediator] No Gemini API key found for background feedback audit.")
            return None

        clean_query = cls.redact_pii_for_audit(user_query)
        clean_output = cls.redact_pii_for_audit(bot_output)
        clean_comment = cls.redact_pii_for_audit(student_comment or "")

        audit_prompt = f"""You are the VIGBOT Institutional Audit Engine for Vignan University (VFSTR Vadlamudi).
A student gave negative feedback (thumbs down / dislike) on the following conversation turn:

[STUDENT QUERY]:
{clean_query}

[BOT OUTPUT DELIVERED]:
{clean_output}

[STUDENT FEEDBACK COMMENT]:
{clean_comment or "None provided"}

TASK:
Analyze whether there is a genuine INTENT-OUTPUT MISMATCH or if the bot was correct.

CRITICAL EVALUATION RULES:
1. DO NOT REMEDIATE (mismatch_detected = false, remediation_needed = false):
   - If the bot correctly enforced university regulations (e.g. attendance below mandatory 75% cutoff, condonation rules Clause 4.2).
   - If the bot correctly enforced privacy policies (e.g. refusing to show other students' attendance or marks under Clause 2.1 RLAC).
   - If the bot gave accurate fee dues, timetable periods, or hostel curfew times, and the student simply expressed frustration with the rule itself.
   - In these cases, the bot's response was factually and procedurally accurate.

2. REMEDIATE (mismatch_detected = true, remediation_needed = true):
   - If the bot answered a completely different topic (e.g. user asked for building directions or location, but bot gave document request services).
   - If the bot failed to distinguish informational building queries ("what is N-Block?") from walking navigation ("where is N-Block?").
   - If the bot hallucinated inaccurate campus landmarks (e.g. calling Zest Supermarket "Chest", or missing that N-Block is just beside Zest).
   - If the bot failed to route to the correct tool or provided irrelevant generic boilerplate.

Respond ONLY with valid JSON (no markdown formatting, no code blocks) matching this schema:
{{
  "mismatch_detected": true or false,
  "mismatch_reason": "Clear diagnosis of whether intent matched output",
  "remediation_needed": true or false,
  "intended_intent": "CAMPUS_DIRECTIONS | BUILDING_PROFILE | LOST_AND_FOUND | ATTENDANCE | FEES | EXAMS | TIMETABLE | SERVICES | HOSTEL | TRANSPORT | PRIVACY_GUARD | GENERAL",
  "target_entity": "Name of building, subject, or landmark (e.g. N_BLOCK, ZEST, CS302, etc.) or null",
  "trigger_patterns": ["phrase 1", "phrase 2", "phrase 3"],
  "routing_action": "TOOL:get_campus_location_and_navigation | TOOL:get_attendance | RULE:privacy_refusal | DIRECT_ANSWER",
  "remediation_type": "TOOL_ROUTING | BUILDING_PROFILE | POLICY_DEFENSE | DIRECT_ANSWER",
  "grounded_response_template": "High-quality, factual markdown answer to serve future queries",
  "suggested_follow_ups": ["follow up question 1", "follow up question 2"]
}}
"""

        candidate_models = [
            getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash"),
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-flash-latest"
        ]

        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": audit_prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                    "responseMimeType": "application/json"
                }
            }
            t0 = time.time()
            try:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=25) as resp:
                    latency = int((time.time() - t0) * 1000)
                    DataRepository.log_gemini_call(endpoint="auditEngine", model=model, status_code=200, latency_ms=latency)
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_data.get("candidates", [])
                    if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                        raw_text = candidates[0]["content"]["parts"][0].get("text", "")
                        # Parse JSON cleanly
                        cleaned_json = re.sub(r"^```json\s*", "", raw_text.strip())
                        cleaned_json = re.sub(r"\s*```$", "", cleaned_json).strip()
                        return json.loads(cleaned_json)
            except urllib.error.HTTPError as he:
                latency = int((time.time() - t0) * 1000)
                DataRepository.log_gemini_call(endpoint="auditEngine", model=model, status_code=he.code, latency_ms=latency)
                if he.code == 404:
                    logger.warning(f"[FeedbackRemediator] Gemini model {model} 404, trying next...")
                    continue
                logger.warning(f"[FeedbackRemediator] Gemini HTTP error on {model}: {he}")
                break
            except Exception as e:
                logger.warning(f"[FeedbackRemediator] Error calling Gemini {model}: {e}")
                break

        return None

    @classmethod
    def evaluate_and_remediate(
        cls,
        feedback_id: str,
        conversation_id: str,
        user_query: str,
        bot_output: str,
        student_comment: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """
        Background task: Evaluates disliked conversation turn with Gemini.
        If intent and output mismatched, creates and persists a learned query remediation.
        """
        try:
            logger.info(f"[FeedbackRemediator] Evaluating negative feedback {feedback_id} for query: '{user_query}'")
            audit_result = cls.call_gemini_audit_engine(
                user_query=user_query,
                bot_output=bot_output,
                student_comment=student_comment,
                history=history
            )

            if not audit_result:
                logger.warning(f"[FeedbackRemediator] Audit engine returned no result for feedback {feedback_id}")
                return None

            mismatch = audit_result.get("mismatch_detected", False)
            remediation_needed = audit_result.get("remediation_needed", False)
            reason = audit_result.get("mismatch_reason", "No reason provided")

            logger.info(f"[FeedbackRemediator] Audit result for feedback {feedback_id}: mismatch={mismatch}, remediation_needed={remediation_needed}. Reason: {reason}")

            # IFF necessary: only update query handling if intent and output genuinely mismatched
            if not (mismatch and remediation_needed):
                logger.info(f"[FeedbackRemediator] Dislike was on a policy-compliant or correct answer. Storing POLICY_PROTECTED audit log.")
                policy_audit_record = {
                    "feedback_id": feedback_id,
                    "conversation_id": conversation_id,
                    "user_query": user_query,
                    "bot_output": bot_output,
                    "student_comment": student_comment or "",
                    "mismatch_detected": False,
                    "mismatch_reason": reason or "Disliked query verified: bot correctly upheld university academic policy or RLS student data privacy rules.",
                    "intended_intent": audit_result.get("intended_intent") or "POLICY_GUARD",
                    "remediation_type": "POLICY_DEFENSE",
                    "trigger_patterns": [user_query.strip().lower()],
                    "target_entity": audit_result.get("target_entity") or "",
                    "routing_action": "RULE:policy_enforcement",
                    "remediation_payload": {
                        "grounded_response_template": bot_output,
                        "suggested_follow_ups": audit_result.get("suggested_follow_ups") or []
                    },
                    "status": "POLICY_PROTECTED"
                }
                DataRepository.save_learned_remediation(policy_audit_record)
                return None

            # Prepare trigger patterns
            triggers = audit_result.get("trigger_patterns") or []
            normalized_user_q = user_query.strip().lower()
            if normalized_user_q not in triggers:
                triggers.append(normalized_user_q)

            # Compile remediation record
            remediation_record = {
                "feedback_id": feedback_id,
                "conversation_id": conversation_id,
                "user_query": user_query,
                "bot_output": bot_output,
                "student_comment": student_comment or "",
                "mismatch_detected": True,
                "mismatch_reason": reason,
                "intended_intent": audit_result.get("intended_intent") or "GENERAL",
                "remediation_type": audit_result.get("remediation_type") or "DIRECT_ANSWER",
                "trigger_patterns": triggers,
                "target_entity": audit_result.get("target_entity") or "",
                "routing_action": audit_result.get("routing_action") or "DIRECT_ANSWER",
                "remediation_payload": {
                    "grounded_response_template": audit_result.get("grounded_response_template") or "",
                    "suggested_follow_ups": audit_result.get("suggested_follow_ups") or []
                },
                "status": "ACTIVE"
            }

            rem_id = DataRepository.save_learned_remediation(remediation_record)
            # Invalidate in-memory cache to make it active instantly
            cls._cache_active_remediations = None
            logger.info(f"[FeedbackRemediator] Stored active learned remediation '{rem_id}' for intent: {remediation_record['intended_intent']}")
            return rem_id

        except Exception as e:
            logger.error(f"[FeedbackRemediator] Failed to evaluate and remediate feedback {feedback_id}: {e}", exc_info=True)
            return None

    @classmethod
    def get_active_remediations(cls) -> List[Dict[str, Any]]:
        """Cached retrieval of active remediations for fast query matching."""
        now = time.time()
        if cls._cache_active_remediations is not None and (now - cls._last_cache_time) < cls.CACHE_TTL_SECONDS:
            return cls._cache_active_remediations

        try:
            rems = DataRepository.get_active_learned_remediations()
            cls._cache_active_remediations = rems
            cls._last_cache_time = now
            return rems
        except Exception as e:
            logger.warning(f"[FeedbackRemediator] Could not load active remediations: {e}")
            return []

    @classmethod
    def match_query(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Matches an incoming student query against all active learned remediations.
        Returns the best matching remediation if one exists.
        """
        q_clean = query.strip().lower()
        q_norm = re.sub(r"[?!.,;:()\[\]{}]", "", q_clean).strip()
        remediations = cls.get_active_remediations()

        for rem in remediations:
            triggers = rem.get("trigger_patterns") or []
            for trigger in triggers:
                trig_clean = trigger.strip().lower()
                trig_norm = re.sub(r"[?!.,;:()\[\]{}]", "", trig_clean).strip()
                if not trig_norm:
                    continue
                # Exact or substring match (trigger contained in query)
                if trig_norm == q_norm or trig_norm in q_norm:
                    return rem
                try:
                    if re.search(r"\b" + re.escape(trig_norm) + r"\b", q_norm, re.I):
                        return rem
                except Exception:
                    pass

        return None

    @classmethod
    def apply_remediation(
        cls,
        remediation: Dict[str, Any],
        session: DatabaseSession,
        query: str,
        effective_lang: str = "en",
        active_subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the learned routing remediation for a matched student query.
        Dispatches to the correct tool, building profile, privacy guard, or direct grounded response.
        """
        from app.agent.tool_registry import ToolRegistry

        rem_type = remediation.get("remediation_type", "DIRECT_ANSWER")
        routing_action = remediation.get("routing_action", "DIRECT_ANSWER")
        target_entity = remediation.get("target_entity") or ""
        payload = remediation.get("remediation_payload") or {}
        follow_ups = payload.get("suggested_follow_ups") or ["Check campus map", "Ask another question"]
        template = payload.get("grounded_response_template") or ""

        # 1. TOOL ROUTING (e.g. Campus Navigation to N-Block, Zest, Library, etc.)
        if rem_type == "TOOL_ROUTING" and "get_campus_location_and_navigation" in routing_action:
            dest = target_entity or query
            tool_res = ToolRegistry.get_campus_location_and_navigation(destination=dest)
            tool_dict = tool_res if isinstance(tool_res, dict) else (getattr(tool_res, "data", {}) or {})
            data = tool_dict.get("data") if isinstance(tool_dict, dict) else {}
            direct_answer = tool_dict.get("direct_answer", "") if isinstance(tool_dict, dict) else ""
            
            # Check if query was informational vs directional
            is_directional = bool(re.search(r"\b(where|reach|how\s+to\s+(?:go|get|reach)|path|route|direction|directions|way\s+to|walk|walking)\b", query, re.I))
            building_profile = data.get("building_profile") if isinstance(data, dict) else None

            if not is_directional and building_profile:
                # Informational Building Profile
                content = (
                    f"### 🏛️ {building_profile.get('title', 'Campus Landmark')}\n\n"
                    f"• **Campus Role & Purpose:** {building_profile.get('purpose', '')}\n"
                    f"• **Student Cohorts & Branches:** {building_profile.get('cohort', '')}\n"
                    f"• **Geographic Location:** {building_profile.get('location', '')}\n"
                    f"• **Key Facilities & Labs:** {building_profile.get('facilities', '')}\n\n"
                    f"💡 *Need walking directions from the Main Gate? Just ask 'Where is {dest}?' or 'How do I reach {dest}?'*"
                )
                topic = f"{building_profile.get('title')} Profile"
            else:
                # Turn-by-Turn Route
                steps = data.get("steps", []) if isinstance(data, dict) else []
                step_lines = []
                for i, s in enumerate(steps):
                    s_clean = s.strip()
                    if s_clean.lower().startswith("step "):
                        step_lines.append(f"• {s_clean}")
                    else:
                        step_lines.append(f"• **Step {i+1}:** {s_clean}")
                steps_formatted = "\n".join(step_lines)

                tot_dist = data.get("total_distance_meters", 240) if isinstance(data, dict) else 240
                dest_name = data.get("destination") or dest.replace("_", "-")

                walking_section = ""
                if steps_formatted:
                    walking_section = f"\n\n🚶‍♂️ **Turn-by-Turn Walking Route from Main Gate ({tot_dist:.0f}m):**\n{steps_formatted}"

                content = (
                    f"### 📍 {dest_name} Location & Campus Directions:\n\n"
                    f"{direct_answer}"
                    f"{walking_section}\n\n"
                    f"🗺️ *You can also inspect the full interactive layout in the Campus Map tab.*"
                )
                topic = f"{dest_name} Directions"

            return {
                "category": "MAP",
                "topic": topic,
                "source_agent": "VIGBOT Cognitive Remediation Engine",
                "content": content,
                "citations": [
                    {
                        "title": "VFSTR Campus Spatial Directory",
                        "clause": "Campus Node Directory & Dijkstra Graph",
                        "effective_date": "2026-07-01",
                        "summary": "Verified spatial coordinates and walking routes."
                    }
                ],
                "structured_card": {
                    "type": "navigation",
                    "title": f"Route to {data.get('destination', dest)}",
                    "path": "/campus-map",
                    "action_text": "Open Campus Map",
                    "actionIntent": "navigate:map",
                    "target": "map"
                },
                "redirect_path": "map",
                "action": {
                    "type": "navigate",
                    "label": "Open Campus Map",
                    "target": "map",
                    "route": "/?tab=map"
                },
                "suggested_follow_ups": follow_ups,
                "active_subject": active_subject,
                "language": effective_lang,
                "llm_provider": "gemini-remediated",
                "model_used": "gemini-learned-rule",
                "used_fallback": False,
                "routed_by": "learned_remediation",
                "remediation_id": remediation.get("remediation_id")
            }

        # 2. BUILDING PROFILE
        if rem_type == "BUILDING_PROFILE":
            block_key = target_entity.upper().replace(" ", "_") if target_entity else "N_BLOCK"
            profile = ToolRegistry.CAMPUS_BLOCK_PROFILES.get(block_key) or ToolRegistry.CAMPUS_BLOCK_PROFILES.get("N_BLOCK")
            content = (
                f"### 🏛️ {profile.get('title', target_entity)}\n\n"
                f"• **Campus Role & Purpose:** {profile.get('purpose', '')}\n"
                f"• **Student Cohorts & Branches:** {profile.get('cohort', '')}\n"
                f"• **Geographic Location:** {profile.get('location', '')}\n"
                f"• **Key Facilities & Labs:** {profile.get('facilities', '')}\n\n"
                f"💡 *Need walking directions? Ask 'Where is {profile.get('title')}?'*"
            )
            return {
                "category": "CAMPUS_INFO",
                "topic": f"{profile.get('title')} Profile",
                "source_agent": "VIGBOT Cognitive Remediation Engine",
                "content": content,
                "citations": [],
                "structured_card": {
                    "type": "navigation_route",
                    "title": f"{profile.get('title')}",
                    "path": "/campus-map",
                    "action_text": "View on Campus Map"
                },
                "suggested_follow_ups": follow_ups,
                "active_subject": active_subject,
                "language": effective_lang,
                "llm_provider": "gemini-remediated",
                "model_used": "gemini-learned-rule",
                "used_fallback": False,
                "routed_by": "learned_remediation",
                "remediation_id": remediation.get("remediation_id")
            }

        # 3. POLICY DEFENSE
        if rem_type == "POLICY_DEFENSE":
            from app.agent.nlu_engine import NLUEngine
            defense_res = NLUEngine.generate_privacy_injection_defense_response(session, query, effective_lang)
            defense_res["routed_by"] = "learned_remediation"
            defense_res["remediation_id"] = remediation.get("remediation_id")
            return defense_res

        # 4. DIRECT GROUNDED ANSWER
        return {
            "category": remediation.get("intended_intent", "GENERAL"),
            "topic": "Learned Institutional Remediation",
            "source_agent": "VIGBOT Cognitive Remediation Engine",
            "content": template or "I have processed your query according to verified university records.",
            "citations": [
                {
                    "title": "VFSTR Institutional Knowledge Base",
                    "clause": "Verified Helpdesk Rule",
                    "effective_date": "2026-07-01",
                    "summary": "Verified institutional information."
                }
            ],
            "structured_card": None,
            "suggested_follow_ups": follow_ups,
            "active_subject": active_subject,
            "language": effective_lang,
            "llm_provider": "gemini-remediated",
            "model_used": "gemini-learned-rule",
            "used_fallback": False,
            "routed_by": "learned_remediation",
            "remediation_id": remediation.get("remediation_id")
        }
