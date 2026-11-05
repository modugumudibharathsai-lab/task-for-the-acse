import math
from typing import Dict, Any, Optional
from app.database import DataRepository, DatabaseSession

def calculate_consecutive_needed(attended: int, held: int, target_pct: float = 75.0) -> int:
    """
    Calculates the exact number of future consecutive classes a student must attend
    without any absences to raise their attendance to the target percentage.
    Formula: (attended + x) / (held + x) >= target / 100
             x * (1 - target/100) >= (target/100) * held - attended
             x >= (0.75 * held - attended) / 0.25
    """
    target_ratio = target_pct / 100.0
    current_ratio = attended / held if held > 0 else 1.0
    if current_ratio >= target_ratio:
        return 0
    needed = (target_ratio * held - attended) / (1.0 - target_ratio)
    return max(0, math.ceil(needed))

def get_attendance_summary(session: DatabaseSession, subject_query: Optional[str] = None) -> Dict[str, Any]:
    records = DataRepository.get_attendance(session, subject_query)
    if not records:
        # If filtered by specific subject and none found
        all_records = DataRepository.get_attendance(session)
        if not all_records:
            return {
                "text": "No attendance records found for your student profile in the current term.",
                "has_records": False
            }
        records = all_records

    # Select the subject of interest (or the most critical one if multiple)
    critical_record = min(records, key=lambda r: r["current_pct"])
    
    # Calculate recovery for the critical subject
    classes_needed = calculate_consecutive_needed(
        critical_record["classes_attended"],
        critical_record["classes_held"],
        critical_record["required_pct"]
    )
    
    is_at_risk = critical_record["current_pct"] < critical_record["required_pct"]
    
    text = (
        f"Your attendance in **{critical_record['course_title']} ({critical_record['course_code']})** is "
        f"**{critical_record['current_pct']:.1f}%** ({critical_record['classes_attended']} out of {critical_record['classes_held']} classes attended).\n\n"
    )
    
    if is_at_risk:
        text += (
            f"⚠️ **Status: Below Mandatory 75% Threshold**\n"
            f"• Classes needed: You must attend the **next {classes_needed} consecutive classes** without absence to reach 75%.\n"
            f"• Deadline: Condonation cut-off date is **{critical_record['deadline']}**.\n"
            f"• Feasibility: Recovery is mathematically feasible before term instruction ends.\n"
            f"• Action: Ensure regular attendance and contact faculty mentor {critical_record['faculty_name']} if you have approved medical leave."
        )
    else:
        text += (
            f"✅ **Status: In Good Standing**\n"
            f"You are comfortably above the 75% requirement. Maintain your current attendance rate through the remainder of the semester."
        )

    card_data = {
        "type": "attendance",
        "title": f"{critical_record['course_title']} ({critical_record['course_code']})",
        "subtitle": f"Faculty: {critical_record['faculty_name']}",
        "badge": f"{critical_record['current_pct']:.1f}% Attendance",
        "badgeVariant": "amber" if is_at_risk else "green",
        "data": {
            "courseCode": critical_record["course_code"],
            "courseTitle": critical_record["course_title"],
            "currentPct": critical_record["current_pct"],
            "classesHeld": critical_record["classes_held"],
            "classesAttended": critical_record["classes_attended"],
            "classesNeeded": classes_needed,
            "deadline": critical_record["deadline"],
            "isAtRisk": is_at_risk
        },
        "actionLabel": "Apply for Medical Condonation" if is_at_risk else "View Full Attendance Record",
        "actionIntent": "service:condonation" if is_at_risk else "view:attendance"
    }

    return {
        "text": text,
        "critical_record": critical_record,
        "all_records": records,
        "structured_card": card_data,
        "context_subject": critical_record["course_title"]
    }
