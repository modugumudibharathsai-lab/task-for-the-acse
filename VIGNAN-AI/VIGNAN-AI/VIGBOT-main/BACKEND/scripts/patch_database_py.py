import re

db_path = r'BACKEND\app\database.py'
with open(db_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace TIMETABLE_DB initial definition
old_timetable_block = '''TIMETABLE_DB = [
    {
        "student_id": "cccccccc-0000-0000-0000-000000000001",
        "day_of_week": "Friday",
        "time_slot": "09:00 AM - 10:00 AM",
        "course_code": "CS301",
        "course_title": "Data Structures",
        "room_no": "Room 301, Academic Block B",
        "faculty_name": "Dr. Meera Iyer"
    },
    {
        "student_id": "cccccccc-0000-0000-0000-000000000001",
        "day_of_week": "Friday",
        "time_slot": "10:15 AM - 11:15 AM",
        "course_code": "CS302",
        "course_title": "Digital Electronics",
        "room_no": "Lab 204, Hardware Wing",
        "faculty_name": "Prof. K. Raman"
    },
    {
        "student_id": "cccccccc-0000-0000-0000-000000000001",
        "day_of_week": "Friday",
        "time_slot": "02:00 PM - 04:00 PM",
        "course_code": "CS302",
        "course_title": "Digital Electronics Lab",
        "room_no": "DE Lab, Room 108",
        "faculty_name": "Prof. K. Raman"
    }
]'''

new_timetable_block = '''TIMETABLE_DB = [
    # Section-7 (N-312) Official Academic Routine
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Monday", "time_slot": "09:05 AM - 10:45 AM", "course_code": "OOPS-25CS204", "course_title": "Object Oriented Programming Through Java [P]", "room_no": "N-312 / Java Lab", "faculty_name": "Mr. T. Latesh Babu, Manikanta Reddy, Vamsi Krishna, Shaik Shamsheer Bhash"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Monday", "time_slot": "12:30 PM - 01:20 PM", "course_code": "DLD-25CS205", "course_title": "Digital Logic design [L]", "room_no": "N-312", "faculty_name": "Mrs Archana (8985716984)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Monday", "time_slot": "01:20 PM - 02:10 PM", "course_code": "COUN", "course_title": "Counseling / Mentorship", "room_no": "N-312", "faculty_name": "Mr. T. Latesh Babu (Class Teacher)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Monday", "time_slot": "02:20 PM - 03:10 PM", "course_code": "DS-25CS201", "course_title": "Data Structures [L]", "room_no": "N-312", "faculty_name": "Dr. R. Prathap Kumar (7569888963)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Monday", "time_slot": "03:10 PM - 04:00 PM", "course_code": "DBMS-25CS203", "course_title": "Database Management System [L]", "room_no": "N-312", "faculty_name": "Ms. Y. Sai Eswari (8074131669)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Friday", "time_slot": "09:05 AM - 10:45 AM", "course_code": "DS-25CS201", "course_title": "Data Structures [P]", "room_no": "N-312 / DS Lab", "faculty_name": "Dr. R. Prathap Kumar (7569888963)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Friday", "time_slot": "12:30 PM - 01:20 PM", "course_code": "DMS-25MT202", "course_title": "Discrete Mathematical Structures [L]", "room_no": "N-312", "faculty_name": "DR. N. SANTHOSHO"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Friday", "time_slot": "01:20 PM - 02:10 PM", "course_code": "AI-24CS302", "course_title": "Artificial Intelligence [L]", "room_no": "N-312", "faculty_name": "Dr. M. Sunil Babu (8333001991)"},
    {"student_id": "cccccccc-0000-0000-0000-000000000001", "day_of_week": "Friday", "time_slot": "02:20 PM - 03:10 PM", "course_code": "DBMS-25CS203", "course_title": "Database Management System [T]", "room_no": "N-312", "faculty_name": "Nemalikanti Deena, Mathangi Haveela, Kommuri Ramya"}
]'''

if old_timetable_block in code:
    code = code.replace(old_timetable_block, new_timetable_block)
    print("Replaced initial TIMETABLE_DB block.")

# Replace Section 7 Timetable mapping inside _load_from_sqlite()
old_mapping = '''        # Section 7 Timetable mapping
        for sid in list(STUDENTS_DB.keys()):
            TIMETABLE_DB.extend([
                {"student_id": sid, "day_of_week": "Monday", "time_slot": "08:30 AM - 09:20 AM", "course_code": "CS201", "course_title": "Data Structures", "room_no": "N-301", "faculty_name": "Dr. Meera Iyer"},
                {"student_id": sid, "day_of_week": "Monday", "time_slot": "09:20 AM - 10:10 AM", "course_code": "CS202", "course_title": "DBMS & IS", "room_no": "N-301", "faculty_name": "Dr. K. V. Krishna Kishore"},
                {"student_id": sid, "day_of_week": "Monday", "time_slot": "10:30 AM - 12:10 PM", "course_code": "CS203L", "course_title": "OOP Java Lab", "room_no": "Software Lab 4", "faculty_name": "Prof. P. Subbarao"},
                {"student_id": sid, "day_of_week": "Tuesday", "time_slot": "08:30 AM - 09:20 AM", "course_code": "CS203", "course_title": "OOP Through Java", "room_no": "N-301", "faculty_name": "Prof. P. Subbarao"},
                {"student_id": sid, "day_of_week": "Tuesday", "time_slot": "09:20 AM - 10:10 AM", "course_code": "EC204", "course_title": "Digital Logic & Embedded Systems", "room_no": "N-301", "faculty_name": "Dr. T. Pitchaiah"},
                {"student_id": sid, "day_of_week": "Wednesday", "time_slot": "08:30 AM - 09:20 AM", "course_code": "AI205", "course_title": "Artificial Intelligence", "room_no": "N-301", "faculty_name": "Dr. S. Venkateswarlu"},
                {"student_id": sid, "day_of_week": "Wednesday", "time_slot": "09:20 AM - 10:10 AM", "course_code": "MA206", "course_title": "Discrete Mathematical Structures", "room_no": "N-301", "faculty_name": "Dr. P. L. N. Varma"},
                {"student_id": sid, "day_of_week": "Wednesday", "time_slot": "10:30 AM - 12:10 PM", "course_code": "CS201L", "course_title": "Data Structures Lab", "room_no": "Computing Lab 2", "faculty_name": "Dr. Meera Iyer"},
                {"student_id": sid, "day_of_week": "Thursday", "time_slot": "08:30 AM - 09:20 AM", "course_code": "CS208", "course_title": "Data Wrangling & Visualization", "room_no": "N-301", "faculty_name": "Dr. N. Veeranjaneyulu"},
                {"student_id": sid, "day_of_week": "Friday", "time_slot": "08:30 AM - 10:10 AM", "course_code": "CS202L", "course_title": "DBMS Lab", "room_no": "Database Lab 1", "faculty_name": "Dr. K. V. Krishna Kishore"}
            ])'''

new_mapping = '''        # Section 7 Timetable mapping (From SQLite timetable table)
        cur.execute("SELECT day_of_week, time_slot, course_code, course_title, room_no, faculty_name, slot_type FROM timetable")
        tt_rows = cur.fetchall()
        for sid in list(STUDENTS_DB.keys()):
            for tr in tt_rows:
                t_day, t_slot, t_code, t_title, t_room, t_fac, t_type = tr
                TIMETABLE_DB.append({
                    "student_id": sid,
                    "day_of_week": t_day,
                    "time_slot": t_slot,
                    "course_code": t_code,
                    "course_title": t_title,
                    "room_no": t_room,
                    "faculty_name": t_fac,
                    "slot_type": t_type
                })

        # Section 7 Exam Schedule
        sec7_exams = [
            {"exam_type": "End Semester Examination", "course_code": "DLD-25CS205", "course_title": "Digital Logic design", "exam_date": "2026-09-18", "time": "10:00 AM - 01:00 PM", "venue": "Examination Hall A2", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "DS-25CS201", "course_title": "Data Structures", "exam_date": "2026-09-22", "time": "02:00 PM - 05:00 PM", "venue": "Examination Hall B1", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "DMS-25MT202", "course_title": "Discrete Mathematical Structures", "exam_date": "2026-09-24", "time": "10:00 AM - 01:00 PM", "venue": "Examination Hall A2", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "OOPS-25CS204", "course_title": "Object Oriented Programming Through Java", "exam_date": "2026-09-25", "time": "10:00 AM - 01:00 PM", "venue": "Examination Hall A1", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "DBMS-25CS203", "course_title": "Database Management System", "exam_date": "2026-09-28", "time": "02:00 PM - 05:00 PM", "venue": "Examination Hall B3", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "AI-24CS302", "course_title": "Artificial Intelligence", "exam_date": "2026-09-30", "time": "10:00 AM - 01:00 PM", "venue": "Examination Hall A1", "hall_ticket_status": "APPROVED"},
            {"exam_type": "End Semester Examination", "course_code": "DW-25CS202", "course_title": "Data Wrangling and Visualization", "exam_date": "2026-10-03", "time": "02:00 PM - 04:00 PM", "venue": "Computing Lab N-314A", "hall_ticket_status": "APPROVED"}
        ]
        for sid in list(STUDENTS_DB.keys()):
            for ex in sec7_exams:
                EXAMS_DB.append({
                    "student_id": sid,
                    **ex
                })'''

if old_mapping in code:
    code = code.replace(old_mapping, new_mapping)
    print("Replaced _load_from_sqlite timetable mapping.")
else:
    print("WARNING: old_mapping not found in code.")

with open(db_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app/database.py successfully!")
