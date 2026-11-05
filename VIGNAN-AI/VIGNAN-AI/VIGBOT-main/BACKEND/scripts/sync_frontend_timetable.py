import sqlite3
import os
import json

db_path = os.path.abspath(r'database\vigbot.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('''
    SELECT day_of_week, time_slot, course_code, course_title, room_no, faculty_name, slot_type
    FROM timetable
    WHERE student_id = 'stu-251fa04e03'
''')
rows = [dict(r) for r in cur.fetchall()]

by_day = {}
for r in rows:
    d = r['day_of_week']
    by_day.setdefault(d, []).append(r)

out = '''export interface TimetableSlot {
  id: string;
  time: string;
  startTime: string;
  endTime: string;
  subject: string;
  code: string;
  room: string;
  faculty: string;
  type: "Lecture" | "Lab" | "Break" | "Tutorial" | "Self Learning" | "Counseling";
  status: "Completed" | "Current" | "Next" | "Upcoming";
}

export interface SectionDetails {
  section: string;
  room: string;
  classTeacher: string;
  timetableCoordinator: string;
  coordinatorPhone: string;
  hodCse: string;
}

export const SECTION_METADATA: SectionDetails = {
  section: "Section-7",
  room: "N-312",
  classTeacher: "Mr. T. Latesh Babu",
  timetableCoordinator: "Mr. Uttej Kumar Nannapaneni",
  coordinatorPhone: "+91 95737 93802",
  hodCse: "Dr. S V Phani Kumar",
};

export const WEEKLY_TIMETABLE: Record<string, TimetableSlot[]> = {
'''

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
for day in day_order:
    slots = by_day.get(day, [])
    out += f'  "{day}": [\n'
    for idx, s in enumerate(slots, 1):
        time_parts = [p.strip() for p in s['time_slot'].split('-')]
        start_t = time_parts[0] if len(time_parts) > 0 else ''
        end_t = time_parts[1] if len(time_parts) > 1 else ''
        slot_obj = {
            'id': f'{day[:3].upper()}-{idx}',
            'time': f'{start_t} – {end_t}',
            'startTime': start_t,
            'endTime': end_t,
            'subject': s['course_title'],
            'code': s['course_code'],
            'room': s['room_no'],
            'faculty': s['faculty_name'],
            'type': s['slot_type'] or 'Lecture',
            'status': 'Upcoming'
        }
        out += '    ' + json.dumps(slot_obj) + ',\n'
    out += '  ],\n'

out += '''};

export const TODAY_TIMETABLE = {
  day: "Saturday",
  date: "13 September 2026",
  sourceAgent: "Timetable Engine",
  slots: WEEKLY_TIMETABLE["Saturday"] || [],
};
'''

target_file = r'FRONTEND\src\data\timetable.ts'
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(out)
print(f'Successfully updated {target_file} from database.')
