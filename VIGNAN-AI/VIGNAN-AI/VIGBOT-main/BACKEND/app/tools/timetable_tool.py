import datetime
from typing import Dict, Any, Optional
from app.database import DataRepository, DatabaseSession

def get_timetable_summary(session: DatabaseSession, day: Optional[str] = None) -> Dict[str, Any]:
    target_day = day
    if not target_day:
        weekday_name = datetime.date.today().strftime('%A')
        today_slots = DataRepository.get_timetable(session, weekday_name)
        if today_slots:
            target_day = weekday_name
        else:
            target_day = 'Friday'

    slots = DataRepository.get_timetable(session, target_day)
    
    if not slots:
        slots = DataRepository.get_timetable(session)

    profile = DataRepository.get_student_profile(session) or {}
    section = profile.get("section") or profile.get("section_code") or "Not Assigned"
    room_no = profile.get("class_room") or "Room 301"
    
    advisors = DataRepository.get_student_advisors(session) or {}
    class_teacher = advisors.get("class_teacher", {}).get("name", "Not Assigned")
    coordinator = profile.get("coordinator_name", "Not Assigned")
    if coordinator == "Not Assigned" and "coordinator_phone" in profile:
        coordinator_phone = profile.get("coordinator_phone")
        if coordinator_phone:
            coordinator = f"{coordinator} ({coordinator_phone})"

    if not slots:
        return {
            'text': f'You have no scheduled lectures or laboratories on {target_day}.',
            'structured_card': None
        }

    text_lines = [
        f'Here is your official schedule for Section {section} ({room_no}) on **{target_day}**:\n',
        f'Class Teacher: **{class_teacher}** | Coordinator: **{coordinator}**\n'
    ]
    for s in slots:
        time_slot = s.get('time_slot', '')
        title = s.get('course_title', '')
        code = s.get('course_code', '')
        room = s.get('room_no', '')
        fac = s.get('faculty_name', '')
        text_lines.append(
            f'• **{time_slot}**: **{title} ({code})**\n'
            f'  Location: **{room}** | Faculty: {fac}'
        )

    card_data = {
        'type': 'timetable',
        'title': f'Academic Schedule ({target_day}) — Section {section} ({room_no})',
        'subtitle': f'{len(slots)} Sessions Scheduled',
        'badge': f'Section {section} Active',
        'badgeVariant': 'blue',
        'data': {
            'day': target_day,
            'room': room_no,
            'class_teacher': class_teacher,
            'coordinator': coordinator,
            'slots': slots
        },
        'actionLabel': 'View Full Weekly Routine',
        'actionIntent': 'view:timetable'
    }

    return {
        'text': '\n'.join(text_lines),
        'structured_card': card_data
    }
