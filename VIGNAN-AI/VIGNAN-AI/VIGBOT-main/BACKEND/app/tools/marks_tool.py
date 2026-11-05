from typing import Dict, Any, Optional
from app.database import DataRepository, DatabaseSession

def get_marks_summary(session: DatabaseSession, subject_query: Optional[str] = None) -> Dict[str, Any]:
    marks = DataRepository.get_marks(session, subject_query)
    profile = DataRepository.get_student_profile(session)
    
    if not marks:
        return {
            "text": "No continuous assessment marks found for your profile in this term.",
            "structured_card": None
        }

    # Format text response
    text_lines = ["Here are your continuous internal evaluation (CIE) records:\n"]
    for m in marks:
        if m["obtained_marks"] is not None:
            text_lines.append(
                f"• **{m['course_title']} ({m['course_code']})** - {m['assessment_name']}: "
                f"**{m['obtained_marks']}/{m['max_marks']} marks** ({m['percentage']}%) - Status: {m['status']}"
            )
        else:
            text_lines.append(
                f"• **{m['course_title']} ({m['course_code']})** - {m['assessment_name']}: "
                f"**Scheduled** - Max Marks: {m['max_marks']} ({m['status']})"
            )

    if profile and profile.get("cgpa"):
        text_lines.append(f"\n📊 **Cumulative GPA:** {profile['cgpa']:.2f} | **Active Backlogs:** {profile['backlog_count']}")

    card_data = {
        "type": "marks",
        "title": "Continuous Assessment & CIE Marks",
        "subtitle": f"Cumulative GPA: {profile.get('cgpa', 'N/A') if profile else 'N/A'}",
        "badge": f"{profile.get('backlog_count', 0) if profile else 0} Backlogs",
        "badgeVariant": "green" if profile and profile.get("backlog_count") == 0 else "amber",
        "data": {
            "marksList": marks,
            "cgpa": profile.get("cgpa") if profile else None,
            "backlogs": profile.get("backlog_count", 0) if profile else 0
        },
        "actionLabel": "Apply for Revaluation / Grade Card",
        "actionIntent": "service:grade_card"
    }

    return {
        "text": "\n".join(text_lines),
        "structured_card": card_data
    }
