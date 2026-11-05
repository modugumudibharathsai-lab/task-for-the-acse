from typing import Dict, Any
from app.database import DataRepository, DatabaseSession

def get_curriculum_summary(session: DatabaseSession) -> Dict[str, Any]:
    curr = DataRepository.get_curriculum(session)
    if not curr:
        return {
            "text": "Curriculum details could not be retrieved for your registered degree programme.",
            "structured_card": None
        }

    text = (
        f"Here is your Degree Audit and Curriculum status under **{curr['regulation']}**:\n\n"
        f"• **Programme:** {curr['programme']}\n"
        f"• **Credits Earned:** **{curr['credits_earned']}** / {curr['total_credits_required']} credits\n"
        f"• **Credits Needed to Graduate:** **{curr['credits_remaining']} credits**\n"
        f"• **Current Semester Registered Load:** {curr['current_semester_credits']} credits\n"
        f"• **Status:** {curr['graduation_eligibility']}\n\n"
        f"📚 **Upcoming Semester Course Plan:**\n"
    )
    for c in curr["next_semester_courses"]:
        text += f"  - {c['code']}: {c['title']} ({c['credits']} credits, {c['type']})\n"

    card_data = {
        "type": "curriculum",
        "title": "Graduation Degree Audit",
        "subtitle": curr["regulation"],
        "badge": f"{curr['credits_remaining']} Credits Left",
        "badgeVariant": "blue",
        "data": curr,
        "actionLabel": "Download Full Regulation Syllabi",
        "actionIntent": "view:curriculum"
    }

    return {
        "text": text,
        "structured_card": card_data
    }
