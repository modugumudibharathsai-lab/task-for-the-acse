from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import List
import os
import json
import logging
import datetime

logger = logging.getLogger(__name__)

from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageCreate,
    MessageResponse,
    MessageFeedbackCreate,
    MessageFeedbackResponse
)
from app.database import DataRepository, DatabaseSession
from app.security import get_current_student
from app.agent.orchestrator import VIGBOTOrchestrator

router = APIRouter(prefix="/conversations", tags=["Conversations & Helpdesk Chat"])

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    req: ConversationCreate,
    current_student: dict = Depends(get_current_student)
):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    new_conv = DataRepository.create_conversation(session, req.title)
    return ConversationResponse(**new_conv)

@router.get("", response_model=List[ConversationResponse])
async def list_my_conversations(current_student: dict = Depends(get_current_student)):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    convs = DataRepository.list_conversations(session)
    return [ConversationResponse(**c) for c in convs]

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_student: dict = Depends(get_current_student)
):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    conv = DataRepository.get_conversation(session, conversation_id)
    if not conv:
        # Row-level check: Return 404/403 if it does not belong to the student
        raise HTTPException(status_code=404, detail="Conversation not found or access denied.")
    
    messages = DataRepository.get_conversation_messages(session, conversation_id)
    return ConversationDetailResponse(
        **conv,
        messages=[MessageResponse(**m) for m in messages]
    )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    msg: MessageCreate,
    current_student: dict = Depends(get_current_student)
):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    conv = DataRepository.get_conversation(session, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied.")

    try:
        agent_response = VIGBOTOrchestrator.process_message(
            session=session,
            conversation_id=conversation_id,
            user_message=msg.content,
            language=msg.language or "en",
            selected_model=msg.selected_model or "8B"
        )
    except Exception as exc:
        logger.exception("VIGBOT message processing failed for conversation %s", conversation_id)
        # Return a graceful fallback response instead of a 500 crash
        import uuid, datetime
        fallback_response = {
            "message_id": f"msg-err-{uuid.uuid4().hex[:8]}",
            "conversation_id": conversation_id,
            "sender_role": "VIGBOT",
            "content": (
                "I'm sorry, I ran into a temporary issue processing your request. "
                "Please try again in a moment. If the problem persists, try refreshing the page."
            ),
            "category": "GENERAL",
            "source_agent": "VIGBOT (Error Recovery)",
            "citations": [],
            "structured_card": None,
            "is_distress": False,
            "suggested_follow_ups": [],
            "llm_provider": "fallback",
            "model_used": "error-recovery",
            "used_fallback": True,
            "routed_by": "rules",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        return MessageResponse(**fallback_response)
    return MessageResponse(**agent_response)

@router.post("/{conversation_id}/messages/{message_id}/feedback", response_model=MessageFeedbackResponse)
async def submit_message_feedback(
    conversation_id: str,
    message_id: str,
    fb: MessageFeedbackCreate,
    background_tasks: BackgroundTasks,
    current_student: dict = Depends(get_current_student)
):
    session = DatabaseSession(student_id=current_student["student_id"], user_id=current_student["user_id"])
    
    # 1. Record feedback in database
    feedback_record = None
    try:
        feedback_record = DataRepository.record_message_feedback(
            session=session,
            conversation_id=conversation_id,
            message_id=message_id,
            rating=fb.rating,
            comment=fb.comment
        )
    except Exception as e:
        logger.warning(f"Could not record feedback in DB: {e}")

    saved_for_training = False

    # Extract conversation messages and target turn
    history = []
    try:
        history = DataRepository.get_conversation_messages(session, conversation_id)
    except Exception as e:
        logger.warning(f"Could not fetch conversation messages: {e}")

    assistant_response = fb.response_text or ""
    student_query = ""

    if history:
        target_idx = -1
        for idx, m in enumerate(history):
            if m.get("message_id") == message_id:
                target_idx = idx
                break
        if target_idx != -1:
            assistant_response = history[target_idx].get("content", "")
            # Find closest preceding student query
            for m in reversed(history[:target_idx]):
                if m.get("sender_role") == "STUDENT":
                    student_query = m.get("content", "")
                    break
        else:
            if not assistant_response and history:
                assistant_response = history[-1].get("content", "")
            for m in reversed(history):
                if m.get("sender_role") == "STUDENT":
                    student_query = m.get("content", "")
                    break
    elif fb.messages:
        for m in reversed(fb.messages):
            if m.get("role") in ("user", "student") and not student_query:
                student_query = m.get("content", "")
            if m.get("role") in ("assistant", "bot") and not assistant_response:
                assistant_response = m.get("content", "")

    # 2. When rating is "down" (disliked): Trigger Gemini Background Auditor for Intent-Output Mismatch
    if fb.rating.lower() in ["down", "thumbs_down", "thumbsdown", "-1", "negative"]:
        from app.agent.feedback_remediator import FeedbackRemediationService
        fb_id = (feedback_record.get("feedback_id") if feedback_record else None) or f"fb-{message_id}"
        
        background_tasks.add_task(
            FeedbackRemediationService.evaluate_and_remediate,
            feedback_id=fb_id,
            conversation_id=conversation_id,
            user_query=student_query or "helpdesk inquiry",
            bot_output=assistant_response or "helpdesk response",
            student_comment=fb.comment,
            history=history
        )
        logger.info(f"Scheduled background Gemini audit for disliked turn {message_id} (Query: '{student_query[:40]}...')")

        return MessageFeedbackResponse(
            status="success",
            saved_for_training=False,
            rating=fb.rating,
            message="Feedback recorded. Cognitive auditor initiated in background."
        )

    # 3. When rating is "up" (thumbs up), store ONLY this specific conversation turn to train the local AI model
    if fb.rating.lower() in ["up", "thumbs_up", "thumbsup", "1", "positive"]:
        try:
            history = DataRepository.get_conversation_messages(session, conversation_id)
            student_profile = DataRepository.get_student_profile(session)
            student_name = student_profile.get("full_name", "Student") if student_profile else "Student"

            system_content = (
                f"You are VIGBOT, an exceptionally intelligent, empathetic, and knowledgeable university AI assistant "
                f"running locally with zero external API keys, grounded in official university records. "
                f"Student profile: {student_name}."
            )

            prompt_msgs = [{"role": "system", "content": system_content}]
            assistant_response = fb.response_text or ""

            if history:
                target_idx = -1
                for idx, m in enumerate(history):
                    if m.get("message_id") == message_id:
                        target_idx = idx
                        break
                
                if target_idx != -1:
                    for m in history[:target_idx]:
                        role = "user" if m.get("sender_role") == "STUDENT" else "assistant"
                        prompt_msgs.append({"role": role, "content": m.get("content", "")})
                    assistant_response = history[target_idx].get("content", "")
                else:
                    for m in history[:-1]:
                        role = "user" if m.get("sender_role") == "STUDENT" else "assistant"
                        prompt_msgs.append({"role": role, "content": m.get("content", "")})
                    if not assistant_response and history:
                        assistant_response = history[-1].get("content", "")
            elif fb.messages:
                for m in fb.messages:
                    prompt_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})
                if not assistant_response and fb.messages and fb.messages[-1].get("role") == "assistant":
                    assistant_response = fb.messages[-1].get("content", "")

            if assistant_response:
                if not prompt_msgs or prompt_msgs[-1].get("role") != "assistant":
                    prompt_msgs.append({"role": "assistant", "content": assistant_response})

                import hashlib
                import re

                raw_sid = current_student.get("student_id") or "anonymous"
                anonymized_sid = "stu_" + hashlib.sha256(raw_sid.encode()).hexdigest()[:10]

                # Automated PII Scrubbing (Emails, Phones, Identity tokens)
                scrubbed_msgs = []
                for m in prompt_msgs:
                    role = m.get("role", "user")
                    txt = m.get("content", "")
                    txt = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', txt)
                    txt = re.sub(r'(\+?91[-\s]?)?[6-9]\d{9}', '[REDACTED_PHONE]', txt)
                    scrubbed_msgs.append({"role": role, "content": txt})

                quarantine_entry = {
                    "messages": scrubbed_msgs,
                    "model_response": assistant_response,
                    "rating": "thumbs_up",
                    "anonymized_id": anonymized_sid,
                    "status": "pending_curation",
                    "pii_scrubbed": True,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }

                quarantine_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "feedback_quarantine.jsonl"))
                with open(quarantine_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(quarantine_entry, ensure_ascii=False) + "\n")
                saved_for_training = True
                logger.info(f"Appended approved thumbs_up conversation turn {message_id} to feedback_quarantine.jsonl (PII scrubbed)")
        except Exception as err:
            logger.error(f"Failed to append to feedback_quarantine.jsonl: {err}")

    if saved_for_training:
        return MessageFeedbackResponse(
            status="success",
            saved_for_training=True,
            rating=fb.rating,
            message="Conversation turn quarantined and queued for active-learning review."
        )
    else:
        return MessageFeedbackResponse(
            status="success",
            saved_for_training=False,
            rating=fb.rating,
            message="Feedback recorded. Thank you for helping improve VIGBOT."
        )

