import sqlite3
import os
import json
import random
import uuid

db_path = os.path.abspath(r'database\vigbot.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('Updating SQLite database at:', db_path)

# 1. Update Courses Table
cur.execute('DELETE FROM course')

courses = [
    ('course-ds201', 'DS-25CS201', 'Data Structures', 'PCC', 4.0, 'THEORY_CUM_PRACTICAL', 'Dr. R. Prathap Kumar (7569888963)', 'prathap.kumar@vignan.ac.in'),
    ('course-dms202', 'DMS-25MT202', 'Discrete Mathematical Structures', 'BSC', 3.0, 'THEORY', 'DR. N. SANTHOSHO', 'santhosho@vignan.ac.in'),
    ('course-dbms203', 'DBMS-25CS203', 'Database Management System', 'PCC', 4.0, 'THEORY_CUM_PRACTICAL', 'Ms. Y. Sai Eswari (8074131669)', 'sai.eswari@vignan.ac.in'),
    ('course-oops204', 'OOPS-25CS204', 'Object Oriented Programming Through Java', 'PCC', 4.0, 'THEORY_CUM_PRACTICAL', 'Mr. T. Latesh Babu (Class Teacher)', 'latesh.babu@vignan.ac.in'),
    ('course-dld205', 'DLD-25CS205', 'Digital Logic design', 'ESC', 3.0, 'THEORY', 'Mrs Archana (8985716984)', 'archana@vignan.ac.in'),
    ('course-ai302', 'AI-24CS302', 'Artificial Intelligence', 'PCC', 3.0, 'THEORY', 'Dr. M. Sunil Babu (8333001991)', 'sunil.babu@vignan.ac.in'),
    ('course-dw202', 'DW-25CS202', 'Data Wrangling and Visualization', 'PCC', 2.0, 'PRACTICAL', 'Dr. M. Raja Rao (8979803148)', 'raja.rao@vignan.ac.in')
]

cur.executemany('''
    INSERT INTO course (course_id, course_code, title, course_category, credits, course_type, faculty_name, faculty_email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', courses)

# 2. Update Student Table Mentor and Section
cur.execute('''
    UPDATE student 
    SET mentor_name = 'Mr. T. Latesh Babu (Class Teacher, Section 7, N-312)',
        section_code = '7'
''')

# 3. Create and Populate Timetable Table
cur.execute('''
CREATE TABLE IF NOT EXISTS timetable (
    slot_id TEXT PRIMARY KEY,
    day_of_week TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    course_code TEXT NOT NULL,
    course_title TEXT NOT NULL,
    slot_type TEXT NOT NULL,
    room_no TEXT NOT NULL,
    faculty_name TEXT NOT NULL,
    faculty_contact TEXT
)
''')
cur.execute('DELETE FROM timetable')

timetable_data = [
    # MONDAY
    ('mon-1', 'Monday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'OOPS-25CS204', 'Object Oriented Programming Through Java [P]', 'Lab', 'N-312 / Java Lab', 'Mr. T. Latesh Babu, Manikanta Reddy, Vamsi Krishna, Shaik Shamsheer Bhash', ''),
    ('mon-2', 'Monday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('mon-3', 'Monday', '12:30 PM - 01:20 PM', '12:30', '13:20', 'DLD-25CS205', 'Digital Logic design [L]', 'Lecture', 'N-312', 'Mrs Archana', '8985716984'),
    ('mon-4', 'Monday', '01:20 PM - 02:10 PM', '13:20', '14:10', 'COUN', 'Counseling / Mentorship', 'Counseling', 'N-312', 'Mr. T. Latesh Babu (Class Teacher)', ''),
    ('mon-5', 'Monday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DS-25CS201', 'Data Structures [L]', 'Lecture', 'N-312', 'Dr. R. Prathap Kumar', '7569888963'),
    ('mon-6', 'Monday', '03:10 PM - 04:00 PM', '15:10', '16:00', 'DBMS-25CS203', 'Database Management System [L]', 'Lecture', 'N-312', 'Ms. Y. Sai Eswari', '8074131669'),

    # TUESDAY
    ('tue-1', 'Tuesday', '08:15 AM - 09:05 AM', '08:15', '09:05', 'DMS-25MT202', 'Discrete Mathematical Structures [L]', 'Lecture', 'N-314', 'DR. N. SANTHOSHO', ''),
    ('tue-2', 'Tuesday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'DW-25CS202', 'Data Wrangling and Visualization [T]', 'Tutorial', 'N-314', 'Dr. M. Raja Rao, Bhavvanjali, Pallaprolu Kavya Sri', '8979803148 / 7989443565'),
    ('tue-3', 'Tuesday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('tue-4', 'Tuesday', '12:30 PM - 01:20 PM', '12:30', '13:20', 'DS-25CS201', 'Data Structures [L]', 'Lecture', 'N-312', 'Dr. R. Prathap Kumar', '7569888963'),
    ('tue-5', 'Tuesday', '01:20 PM - 02:10 PM', '13:20', '14:10', 'DBMS-25CS203', 'Database Management System [L]', 'Lecture', 'N-312', 'Ms. Y. Sai Eswari', '8074131669'),
    ('tue-6', 'Tuesday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DLD-25CS205', 'Digital Logic design [L]', 'Lecture', 'N-312', 'Mrs Archana', '8985716984'),
    ('tue-7', 'Tuesday', '03:10 PM - 04:00 PM', '15:10', '16:00', 'OOPS-25CS204', 'Object Oriented Programming Through Java [L]', 'Lecture', 'N-312', 'Mr. T. Latesh Babu', ''),

    # WEDNESDAY
    ('wed-1', 'Wednesday', '08:15 AM - 09:05 AM', '08:15', '09:05', 'DLD-25CS205', 'Digital Logic design [L]', 'Lecture', 'N-312', 'Mrs Archana', '8985716984'),
    ('wed-2', 'Wednesday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'DMS-25MT202', 'Discrete Mathematical Structures [T]', 'Tutorial', 'N-312', 'DR. N. SANTHOSHO', ''),
    ('wed-3', 'Wednesday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('wed-4', 'Wednesday', '12:30 PM - 01:20 PM', '12:30', '13:20', 'AI-24CS302', 'Artificial Intelligence [L]', 'Lecture', 'N-312', 'Dr. M. Sunil Babu', '8333001991'),
    ('wed-5', 'Wednesday', '01:20 PM - 02:10 PM', '13:20', '14:10', 'DBMS-25CS203', 'Database Management System [L]', 'Lecture', 'N-312', 'Ms. Y. Sai Eswari', '8074131669'),
    ('wed-6', 'Wednesday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DS-25CS201', 'Data Structures [T]', 'Tutorial', 'N-312', 'Naga Lakshmi, Shaik Thayab', '9908378028'),

    # THURSDAY
    ('thu-1', 'Thursday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'DBMS-25CS203', 'Database Management System [P]', 'Lab', 'N-312 / DBMS Lab', 'Ms. Y. Sai Eswari, Nemalikanti Deena, Mathangi Haveela, Kommuri Ramya', '8074131669'),
    ('thu-2', 'Thursday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('thu-3', 'Thursday', '12:30 PM - 02:10 PM', '12:30', '14:10', 'AI-24CS302', 'Artificial Intelligence [T]', 'Tutorial', 'N-312', 'Dr. M. Sunil Babu, Palagani Pavani, Mulpuri Koti surya sama prabh', '8333001991'),
    ('thu-4', 'Thursday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DMS-25MT202', 'Discrete Mathematical Structures [L]', 'Lecture', 'N-312', 'DR. N. SANTHOSHO', ''),
    ('thu-5', 'Thursday', '03:10 PM - 04:00 PM', '15:10', '16:00', 'OOPS-25CS204', 'Object Oriented Programming Through Java [L]', 'Lecture', 'N-312', 'Mr. T. Latesh Babu', ''),

    # FRIDAY
    ('fri-1', 'Friday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'DS-25CS201', 'Data Structures [P]', 'Lab', 'N-312 / DS Lab', 'Dr. R. Prathap Kumar, Naga Lakshmi, Shaik Thayab, Adil Shai', '7569888963 / 9908378028'),
    ('fri-2', 'Friday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('fri-3', 'Friday', '12:30 PM - 01:20 PM', '12:30', '13:20', 'DMS-25MT202', 'Discrete Mathematical Structures [L]', 'Lecture', 'N-312', 'DR. N. SANTHOSHO', ''),
    ('fri-4', 'Friday', '01:20 PM - 02:10 PM', '13:20', '14:10', 'AI-24CS302', 'Artificial Intelligence [L]', 'Lecture', 'N-312', 'Dr. M. Sunil Babu', '8333001991'),
    ('fri-5', 'Friday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DBMS-25CS203', 'Database Management System [T]', 'Tutorial', 'N-312', 'Nemalikanti Deena, Mathangi Haveela, Kommuri Ramya', ''),

    # SATURDAY
    ('sat-1', 'Saturday', '08:15 AM - 09:05 AM', '08:15', '09:05', 'AI-24CS302', 'Artificial Intelligence [L]', 'Lecture', 'N-314A', 'Dr. M. Sunil Babu', '8333001991'),
    ('sat-2', 'Saturday', '09:05 AM - 10:45 AM', '09:05', '10:45', 'DW-25CS202', 'Data Wrangling and Visualization [P]', 'Lab', 'N-314A', 'Dr. M. Raja Rao, Bhavvanjali, Pallaprolu Kavya Sri', '8979803148 / 7989443565'),
    ('sat-3', 'Saturday', '11:00 AM - 11:50 AM', '11:00', '11:50', 'SELF-LEARN', 'Self Learning / Advanced Learning', 'Self Learning', 'N-312', 'Faculty Mentors', ''),
    ('sat-4', 'Saturday', '12:30 PM - 01:20 PM', '12:30', '13:20', 'OOPS-25CS204', 'Object Oriented Programming Through Java [L]', 'Lecture', 'N-312', 'Mr. T. Latesh Babu', ''),
    ('sat-5', 'Saturday', '01:20 PM - 02:10 PM', '13:20', '14:10', 'DS-25CS201', 'Data Structures [L]', 'Lecture', 'N-312', 'Dr. R. Prathap Kumar', '7569888963'),
    ('sat-6', 'Saturday', '02:20 PM - 03:10 PM', '14:20', '15:10', 'DLD-25CS205', 'Digital Logic design [T]', 'Tutorial', 'N-312', 'Mrs Archana, Mr K. Raj Kiran', '8985716984')
]

cur.executemany('''
    INSERT INTO timetable (slot_id, day_of_week, time_slot, start_time, end_time, course_code, course_title, slot_type, room_no, faculty_name, faculty_contact)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', timetable_data)

# 4. Update Attendance Summary for all students
cur.execute('DELETE FROM attendance_summary')
cur.execute('SELECT student_id, total_attendance_pct FROM student')
students = cur.fetchall()

random.seed(42)
att_summaries = []
for sid, overall in students:
    for c in courses:
        cid, code, title, cat, cred, ctype, fac, femail = c
        delta = random.uniform(-6.0, 6.0)
        pct = max(45.0, min(96.0, round(overall + delta, 1)))
        held = 40 if 'PRACTICAL' not in ctype else 30
        attended = int(round((pct / 100.0) * held))
        pct = round((attended / held) * 100.0, 1)
        needed = 0
        if pct < 75.0:
            needed = max(0, 3 * held - 4 * attended)
        risk = 'SAFE' if pct >= 75.0 else ('AT_RISK' if pct >= 65.0 else 'CRITICAL')
        att_summaries.append((
            str(uuid.uuid4()),
            sid, code, title, fac, pct, held, attended, risk, needed
        ))

cur.executemany('''
    INSERT INTO attendance_summary (summary_id, student_id, course_code, course_title, faculty_name, attendance_pct, classes_held, classes_attended, risk_level, classes_needed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', att_summaries)

# 5. Update Internal Marks Table
cur.execute('DELETE FROM internal_mark')
mark_types = [('Mid-1 (Descriptive)', 40), ('Online Quiz-1', 10), ('Lab Assignment', 20)]
mark_rows = []
for sid, _ in students:
    for c in courses:
        cid, code, title, cat, cred, ctype, fac, femail = c
        for mname, mmax in mark_types:
            obt = int(round(random.uniform(0.55, 0.95) * mmax))
            mid = str(uuid.uuid4())
            mark_rows.append((mid, sid, code, mname, mmax, obt, 'EVALUATED'))

cur.executemany('''
    INSERT INTO internal_mark (mark_id, student_id, course_code, assessment_name, max_marks, marks_obtained, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', mark_rows)

conn.commit()
print('Database commit finished!')
print(f'Courses: {len(courses)}')
print(f'Timetable slots: {len(timetable_data)}')
print(f'Attendance summaries: {len(att_summaries)}')
print(f'Internal marks: {len(mark_rows)}')
conn.close()
