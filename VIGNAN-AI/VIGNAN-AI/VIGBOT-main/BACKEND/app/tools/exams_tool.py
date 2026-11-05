from typing import Dict, Any
from app.database import DataRepository, DatabaseSession

def get_exams_summary(session: DatabaseSession) -> Dict[str, Any]:
    exams = DataRepository.get_exams(session)
    if not exams:
        return {
            "text": "No upcoming examination events or published schedules found for your enrolled courses.",
            "structured_card": None
        }

    text_lines = ["Here is your official examination schedule:\n"]
    for e in exams:
        text_lines.append(
            f"• **{e['exam_type']}**: **{e['course_title']} ({e['course_code']})**\n"
            f"  Date: **{e['exam_date']}** | Time: {e['time']}\n"
            f"  Venue: {e['venue']} | Hall Ticket: {e['hall_ticket_status']}"
        )

    nearest = exams[0] if exams else {}
    card_data = {
        "type": "exam",
        "title": "Upcoming Examination Schedule",
        "subtitle": "Controller of Examinations",
        "badge": f"{len(exams)} Events",
        "badgeVariant": "purple",
        "data": {
            "subject": nearest.get("course_title", "Continuous Internal Evaluation"),
            "date": nearest.get("exam_date", "18 Sep 2026"),
            "time": nearest.get("time", "10:00 AM"),
            "venue": nearest.get("venue", "Examination Hall (N-Block)"),
            "seating": nearest.get("hall_ticket_status", "Hall Ticket Allocated"),
            "exams": exams
        },
        "actionLabel": "Download Hall Ticket Verification",
        "actionIntent": "service:hall_ticket"
    }

    return {
        "text": "\n".join(text_lines),
        "structured_card": card_data
    }
