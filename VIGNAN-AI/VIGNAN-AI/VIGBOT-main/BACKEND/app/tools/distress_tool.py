from typing import Dict, Any
from app.database import DataRepository, DatabaseSession

DISTRESS_KEYWORDS = [
    "can't handle this", "cant handle this", "cannot handle this",
    "handle this anymore", "don't think i can handle", "dont think i can handle",
    "want to give up", "giving up", "feel hopeless", "feeling hopeless",
    "break down", "breakdown", "suicide", "suicidal", "end my life", "ending my life",
    "i want to end my life", "feel like ending my life",
    "can't take it anymore", "cant take it anymore", "cannot take it anymore",
    "can't take this anymore", "cant take this anymore", "cannot take this anymore",
    "kill myself", "hate my life", "overwhelmed and crying", "too much stress to survive",
    "panic attack", "no reason to live", "ending it all", "end it all", "better off dead",
    "dying"
]

def detect_distress(message_text: str) -> bool:
    normalized = message_text.lower()
    return any(phrase in normalized for phrase in DISTRESS_KEYWORDS)

def handle_crisis_escalation(session: DatabaseSession, trigger_message: str) -> Dict[str, Any]:
    student_profile = DataRepository.get_student_profile(session) or {}
    student_name = student_profile.get("full_name", "Student")
    
    # Write emergency crisis record into confidential schema (feeds Crisis Escalation)
    escalation_record = DataRepository.log_crisis_escalation(
        session=session,
        trigger_phrase=trigger_message,
        student_info=student_profile
    )

    print(f"\n[MOCK ALERT] SILENT BACKGROUND ALERT SENT TO COUNSELOR FOR STUDENT: {student_name}")
    print(f"Trigger Message: '{trigger_message}'\n")

    # Compassionate, zero-delay crisis response
    text = (
        f"We hear you, {student_name}. Your wellbeing and safety are far more important than any grade, "
        f"attendance figure, or academic deadline.\n\n"
        f"You do not have to carry this distress alone. Our university counseling team and student wellbeing staff "
        f"are available 24/7 to support you with complete confidentiality and care.\n\n"
        f"**Immediate Support Contacts (Available Right Now):**\n"
        f"📞 **24/7 Campus Emergency Counselor:** +91-98765-43210\n"
        f"📞 **National Tele-MANAS Mental Health Helpline:** 14416 (Toll-Free, 24/7)\n"
        f"📞 **Vandrevala Foundation Helpline:** +91-9999-666-555\n"
        f"🏢 **Student Wellness Center:** Room 102, Student Activity Building (Open 24 Hours)\n\n"
        f"A confidential, high-priority notification has been sent to our Student Wellbeing Counselor, "
        f"who is standing by to assist you."
    )

    card_data = {
        "type": "distress",
        "title": "Immediate Student Support & Counseling (24/7)",
        "subtitle": "Confidential, priority human care & crisis intervention",
        "badge": "Priority Support Active",
        "badgeVariant": "red",
        "data": {
            "escalationId": escalation_record["crisis_escalation_id"],
            "helpline": "14416 / +91-98765-43210",
            "center": "Room 102, Student Wellness Center",
            "confidential": True
        },
        "actionLabel": "Connect with On-Duty Counselor",
        "actionIntent": "contact:counselor"
    }

    return {
        "text": text,
        "is_distress": True,
        "category": "DISTRESS_SUPPORT",
        "source_agent": "Distress Escalation & Counseling",
        "structured_card": card_data
    }

def silent_mock_alert_counselor(session: DatabaseSession, trigger_message: str) -> None:
    student_profile = DataRepository.get_student_profile(session) or {}
    
    # Write emergency crisis record into confidential schema (feeds Crisis Escalation)
    DataRepository.log_crisis_escalation(
        session=session,
        trigger_phrase=trigger_message,
        student_info=student_profile
    )
    
    student_name = student_profile.get("full_name", "Unknown")
    print(f"\n[MOCK ALERT] SILENT BACKGROUND ALERT SENT TO COUNSELOR FOR STUDENT: {student_name}")
    print(f"Trigger Message: '{trigger_message}'\n")
