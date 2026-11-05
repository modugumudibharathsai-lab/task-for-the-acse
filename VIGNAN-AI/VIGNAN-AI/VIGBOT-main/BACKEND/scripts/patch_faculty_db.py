"""
Patch script to ensure faculty table and student advisor columns exist and are populated
in database/vigbot.db
"""

import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))

FACULTY_RECORDS = [
    (
        "fac-latesh",
        "EMP1001",
        "Mr. T. Latesh Babu",
        "Assistant Professor & Class Teacher",
        "CSE",
        "latesh.babu@vignan.ac.in",
        "+91 94901 23456",
        "N-312 Faculty Staff Room / CSE Department",
        "CLASS_TEACHER,MENTOR,COURSE_FACULTY",
        "10:00 AM - 12:00 PM (Mon-Fri)"
    ),
    (
        "fac-radhika",
        "EMP1002",
        "Dr. Radhika Sharma",
        "Associate Professor & Section 7 Counsellor",
        "CSE",
        "radhika.sharma@vignan.ac.in",
        "+91 98480 12345",
        "C-402, Student Wellness Center & Counseling Cell",
        "COUNSELLOR",
        "02:00 PM - 04:30 PM (Mon-Fri)"
    ),
    (
        "fac-prathap",
        "EMP1003",
        "Dr. R. Prathap Kumar",
        "Associate Professor",
        "CSE",
        "prathap.kumar@vignan.ac.in",
        "+91 75698 88963",
        "N-312 / Room 204, Academic Block",
        "COURSE_FACULTY",
        "03:00 PM - 05:00 PM (Tue, Thu)"
    ),
    (
        "fac-santhosh",
        "EMP1004",
        "Dr. N. Santhosh",
        "Associate Professor",
        "Mathematics / S&H",
        "santhosh.n@vignan.ac.in",
        "+91 94402 33456",
        "N-314 / Room 102, S&H Block",
        "COURSE_FACULTY",
        "11:00 AM - 01:00 PM (Wed, Fri)"
    ),
    (
        "fac-saieswari",
        "EMP1005",
        "Ms. Y. Sai Eswari",
        "Assistant Professor",
        "CSE",
        "sai.eswari@vignan.ac.in",
        "+91 80741 31669",
        "N-312 / DBMS Faculty Wing",
        "COURSE_FACULTY",
        "02:00 PM - 04:00 PM (Mon, Wed)"
    ),
    (
        "fac-archana",
        "EMP1006",
        "Mrs. Archana",
        "Assistant Professor",
        "ECE / CSE",
        "archana@vignan.ac.in",
        "+91 89857 16984",
        "N-312 / Hardware Lab 2",
        "COURSE_FACULTY",
        "10:00 AM - 12:00 PM (Tue, Fri)"
    ),
    (
        "fac-sunil",
        "EMP1007",
        "Dr. M. Sunil Babu",
        "Associate Professor",
        "CSE",
        "sunil.babu@vignan.ac.in",
        "+91 83330 01991",
        "N-312 / AI Research Lab",
        "COURSE_FACULTY",
        "01:00 PM - 03:00 PM (Wed, Sat)"
    ),
    (
        "fac-rajarao",
        "EMP1008",
        "Dr. M. Raja Rao",
        "Associate Professor",
        "CSE",
        "raja.rao@vignan.ac.in",
        "+91 89798 03148",
        "N-314A / Computing Lab Wing",
        "COURSE_FACULTY",
        "09:00 AM - 11:00 AM (Tue, Sat)"
    ),
    (
        "fac-meera",
        "EMP1009",
        "Dr. Meera Iyer",
        "Associate Professor",
        "CSE",
        "meera@vignan.ac.in",
        "+91 94400 11223",
        "Academic Block B, Room 301",
        "MENTOR,CLASS_TEACHER,COURSE_FACULTY",
        "02:00 PM - 04:00 PM (Mon-Thu)"
    ),
    (
        "fac-phanikumar",
        "EMP1000",
        "Dr. S. V. Phani Kumar",
        "Professor & Head of Department",
        "CSE",
        "hod_cse@vignan.ac.in",
        "+91 94401 55678",
        "HOD Cabin, CSE Department, Academic Block 1",
        "HOD",
        "10:00 AM - 01:00 PM (Mon-Sat)"
    )
]

def patch_database():
    print(f"Opening database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Create faculty table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        faculty_id TEXT PRIMARY KEY,
        employee_no TEXT UNIQUE,
        name TEXT NOT NULL,
        designation TEXT NOT NULL,
        department TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        cabin TEXT NOT NULL,
        role TEXT NOT NULL,
        office_hours TEXT
    )
    """)

    # Populate faculty table
    cur.execute("DELETE FROM faculty")
    cur.executemany("""
    INSERT INTO faculty (faculty_id, employee_no, name, designation, department, email, phone, cabin, role, office_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, FACULTY_RECORDS)
    print(f"Populated faculty table with {len(FACULTY_RECORDS)} faculty records.")

    # 2. Check and add advisor columns in students table
    existing_cols = [c["name"] for c in cur.execute("PRAGMA table_info(students)").fetchall()]
    print(f"Existing columns in students table: {len(existing_cols)}")

    advisor_columns = [
        ("class_teacher_name", "TEXT"),
        ("class_teacher_phone", "TEXT"),
        ("class_teacher_email", "TEXT"),
        ("class_teacher_cabin", "TEXT"),
        ("counsellor_name", "TEXT"),
        ("counsellor_phone", "TEXT"),
        ("counsellor_email", "TEXT"),
        ("counsellor_cabin", "TEXT"),
        ("mentor_phone", "TEXT"),
        ("mentor_email", "TEXT"),
        ("mentor_cabin", "TEXT"),
        ("hod_name", "TEXT"),
        ("hod_phone", "TEXT"),
        ("hod_email", "TEXT")
    ]

    for col_name, col_type in advisor_columns:
        if col_name not in existing_cols:
            print(f"Adding column '{col_name}' ({col_type}) to students table...")
            cur.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")

    # 3. Populate advisor columns for all students
    cur.execute("""
    UPDATE students
    SET class_teacher_name = 'Mr. T. Latesh Babu',
        class_teacher_phone = '+91 94901 23456',
        class_teacher_email = 'latesh.babu@vignan.ac.in',
        class_teacher_cabin = 'N-312 Faculty Staff Room / CSE Department',
        counsellor_name = 'Dr. Radhika Sharma',
        counsellor_phone = '+91 98480 12345',
        counsellor_email = 'radhika.sharma@vignan.ac.in',
        counsellor_cabin = 'C-402, Student Wellness Center & Counseling Cell',
        mentor_name = 'Mr. T. Latesh Babu',
        mentor_phone = '+91 94901 23456',
        mentor_email = 'latesh.babu@vignan.ac.in',
        mentor_cabin = 'N-312 Faculty Staff Room / CSE Department',
        hod_name = 'Dr. S. V. Phani Kumar',
        hod_phone = '+91 94401 55678',
        hod_email = 'hod_cse@vignan.ac.in'
    WHERE roll_no LIKE '251FA%'
    """)

    # Asha and Rahul (24CSE001, 24CSE002):
    cur.execute("""
    UPDATE students
    SET class_teacher_name = 'Dr. Meera Iyer',
        class_teacher_phone = '+91 94400 11223',
        class_teacher_email = 'meera@vignan.ac.in',
        class_teacher_cabin = 'Academic Block B, Room 301',
        counsellor_name = 'Dr. Radhika Sharma',
        counsellor_phone = '+91 98480 12345',
        counsellor_email = 'radhika.sharma@vignan.ac.in',
        counsellor_cabin = 'C-402, Student Wellness Center & Counseling Cell',
        mentor_name = 'Dr. Meera Iyer',
        mentor_phone = '+91 94400 11223',
        mentor_email = 'meera@vignan.ac.in',
        mentor_cabin = 'Academic Block B, Room 301',
        hod_name = 'Dr. S. V. Phani Kumar',
        hod_phone = '+91 94401 55678',
        hod_email = 'hod_cse@vignan.ac.in'
    WHERE roll_no LIKE '24CSE%'
    """)

    # Any other students fallback:
    cur.execute("""
    UPDATE students
    SET class_teacher_name = 'Mr. T. Latesh Babu',
        class_teacher_phone = '+91 94901 23456',
        class_teacher_email = 'latesh.babu@vignan.ac.in',
        class_teacher_cabin = 'N-312 Faculty Staff Room / CSE Department',
        counsellor_name = 'Dr. Radhika Sharma',
        counsellor_phone = '+91 98480 12345',
        counsellor_email = 'radhika.sharma@vignan.ac.in',
        counsellor_cabin = 'C-402, Student Wellness Center & Counseling Cell',
        mentor_name = COALESCE(mentor_name, 'Mr. T. Latesh Babu'),
        mentor_phone = '+91 94901 23456',
        mentor_email = 'latesh.babu@vignan.ac.in',
        mentor_cabin = 'N-312 Faculty Staff Room / CSE Department',
        hod_name = 'Dr. S. V. Phani Kumar',
        hod_phone = '+91 94401 55678',
        hod_email = 'hod_cse@vignan.ac.in'
    WHERE class_teacher_name IS NULL OR class_teacher_name = ''
    """)

    conn.commit()

    # 4. Verify
    print("\n--- VERIFICATION OF STUDENTS TABLE ADVISOR DATA ---")
    rows = cur.execute("SELECT roll_no, full_name, class_teacher_name, class_teacher_phone, counsellor_name, counsellor_phone, mentor_name, mentor_phone FROM students LIMIT 5").fetchall()
    for r in rows:
        print(f"Roll: {r['roll_no']} | Student: {r['full_name']}")
        print(f"   Class Teacher: {r['class_teacher_name']} (Phone: {r['class_teacher_phone']})")
        print(f"   Counsellor:    {r['counsellor_name']} (Phone: {r['counsellor_phone']})")
        print(f"   Mentor:        {r['mentor_name']} (Phone: {r['mentor_phone']})")

    cnt = cur.execute("SELECT COUNT(*) FROM students WHERE class_teacher_phone IS NOT NULL AND counsellor_phone IS NOT NULL").fetchone()[0]
    total = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    print(f"\nStudents with complete advisor & phone data: {cnt} / {total}")

    conn.close()
    print("Database patch completed successfully!")

if __name__ == "__main__":
    patch_database()
