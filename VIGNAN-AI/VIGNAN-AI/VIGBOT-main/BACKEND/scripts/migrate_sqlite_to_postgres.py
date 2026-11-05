"""
Migration Script: SQLite (database/vigbot.db) -> Neon PostgreSQL
Migrates all 141 students, Section 8 records, timetable slots, attendance,
marks, fees, exams, and faculty directly into Neon PostgreSQL.
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import sqlite3

def get_pg_connection(pg_url: str):
    try:
        import psycopg
        from psycopg.rows import dict_row
        return psycopg.connect(pg_url, row_factory=dict_row)
    except ImportError:
        try:
            import psycopg2
            import psycopg2.extras
            return psycopg2.connect(pg_url, cursor_factory=psycopg2.extras.RealDictCursor)
        except ImportError:
            print("ERROR: Neither 'psycopg' nor 'psycopg2' is installed.")
            print("Please run: pip install \"psycopg[binary]\"")
            sys.exit(1)

# PostgreSQL DDL Schemas matching the SQLite schema exactly
PG_SCHEMAS = [
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        user_id TEXT,
        roll_no TEXT UNIQUE,
        username TEXT,
        password_hash TEXT,
        full_name TEXT NOT NULL,
        gender TEXT,
        email TEXT,
        programme_code TEXT,
        programme_name TEXT,
        department_code TEXT,
        batch_label TEXT,
        section_code TEXT,
        current_year_of_study INTEGER,
        cgpa REAL,
        backlog_count INTEGER,
        overall_attendance_pct REAL,
        fee_outstanding REAL,
        mentor_name TEXT,
        status TEXT,
        semester INTEGER,
        class_teacher_name TEXT,
        class_teacher_phone TEXT,
        class_teacher_email TEXT,
        class_teacher_cabin TEXT,
        counsellor_name TEXT,
        counsellor_phone TEXT,
        counsellor_email TEXT,
        counsellor_cabin TEXT,
        mentor_phone TEXT,
        mentor_email TEXT,
        mentor_cabin TEXT,
        hod_name TEXT,
        hod_phone TEXT,
        hod_email TEXT
    );
    """,
    """
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
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        course_code TEXT NOT NULL,
        course_title TEXT NOT NULL,
        faculty_name TEXT NOT NULL,
        classes_held INTEGER NOT NULL,
        classes_attended INTEGER NOT NULL,
        current_pct REAL NOT NULL,
        required_pct REAL DEFAULT 75.0,
        classes_needed INTEGER DEFAULT 0,
        risk_level TEXT NOT NULL,
        deadline TEXT,
        recovery_possible INTEGER DEFAULT 1
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS marks (
        id SERIAL PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        course_code TEXT NOT NULL,
        course_title TEXT NOT NULL,
        assessment_name TEXT NOT NULL,
        max_marks INTEGER,
        obtained_marks INTEGER,
        percentage REAL,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS timetable (
        id SERIAL PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        day_of_week TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        course_code TEXT NOT NULL,
        course_title TEXT NOT NULL,
        room_no TEXT,
        faculty_name TEXT,
        slot_type TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS fees (
        id SERIAL PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        academic_year TEXT NOT NULL,
        total_demand REAL NOT NULL,
        paid_amount REAL NOT NULL,
        outstanding_balance REAL NOT NULL,
        due_date TEXT,
        status TEXT,
        next_installment_amount REAL,
        next_installment_date TEXT,
        penalty_warning TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exams (
        id SERIAL PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        exam_type TEXT NOT NULL,
        course_code TEXT NOT NULL,
        course_title TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        time TEXT,
        venue TEXT,
        hall_ticket_status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS policies (
        policy_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        clause_no TEXT,
        effective_date TEXT,
        summary TEXT,
        authority TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS circulars (
        circular_no TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        issued_date TEXT,
        effective_date TEXT,
        summary TEXT,
        issued_by TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        context_data TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        sender_role TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        source_agent TEXT,
        citations TEXT,
        structured_card TEXT,
        is_distress INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS service_requests (
        service_request_id TEXT PRIMARY KEY,
        request_no TEXT UNIQUE,
        student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_office TEXT NOT NULL,
        sla_due_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS crisis_escalations (
        crisis_escalation_id TEXT PRIMARY KEY,
        student_id TEXT,
        student_name TEXT,
        roll_no TEXT,
        detected_at TEXT,
        detected_by TEXT,
        trigger_snippet TEXT,
        escalated_to TEXT,
        channel_used TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS analytics_daily (
        id SERIAL PRIMARY KEY,
        stat_date TEXT,
        intent_category TEXT,
        topic TEXT,
        language_code TEXT DEFAULT 'en',
        query_count INTEGER DEFAULT 1,
        successful_answers INTEGER DEFAULT 1,
        escalated_count INTEGER DEFAULT 0,
        distress_count INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS message_feedback (
        feedback_id TEXT PRIMARY KEY,
        message_id TEXT,
        conversation_id TEXT,
        student_id TEXT,
        rating TEXT,
        comment TEXT,
        created_at TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS curriculum (
        regulation TEXT PRIMARY KEY,
        programme TEXT,
        total_credits_required INTEGER,
        credits_earned INTEGER,
        credits_remaining INTEGER,
        current_semester_credits INTEGER,
        graduation_eligibility TEXT,
        next_semester_courses TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS library_operating_hours (
        id SERIAL PRIMARY KEY,
        day_of_week TEXT NOT NULL,
        status TEXT NOT NULL,
        open_time TEXT,
        close_time TEXT,
        reading_room_hours TEXT,
        circulation_counter_hours TEXT,
        notes TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hostels (
        hostel_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        gender_type TEXT,
        resident_category TEXT,
        mess_type TEXT,
        mess_location TEXT,
        breakfast_hours TEXT,
        lunch_hours TEXT,
        tea_snacks_hours TEXT,
        dinner_hours TEXT,
        ac_status TEXT,
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hostel_bus_schedules (
        id SERIAL PRIMARY KEY,
        hostel_route TEXT NOT NULL,
        shift TEXT NOT NULL,
        direction TEXT,
        departure_times_json TEXT,
        time_range TEXT,
        stoppages TEXT,
        effective_date TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS campus_locations (
        location_id TEXT PRIMARY KEY,
        room_number TEXT,
        block TEXT,
        floor TEXT,
        description TEXT,
        latitude REAL,
        longitude REAL,
        features TEXT,
        type TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS campus_navigation_edges (
        edge_id TEXT PRIMARY KEY,
        source_node TEXT NOT NULL,
        target_node TEXT NOT NULL,
        path_name TEXT,
        direction_instruction TEXT,
        distance_meters REAL NOT NULL,
        is_bidirectional INTEGER DEFAULT 1
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS administrative_procedures (
        procedure_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT,
        phase1_digital_instructions TEXT,
        phase2_physical_location TEXT,
        phase2_steps_json TEXT,
        fee_amount REAL,
        office_location TEXT,
        sla_turnaround_days INTEGER
    );
    """
]

TABLES_TO_MIGRATE = [
    ("faculty", ["faculty_id", "employee_no", "name", "designation", "department", "email", "phone", "cabin", "role", "office_hours"]),
    ("students", [
        "student_id", "user_id", "roll_no", "username", "password_hash", "full_name", "gender", "email",
        "programme_code", "programme_name", "department_code", "batch_label", "section_code",
        "current_year_of_study", "cgpa", "backlog_count", "overall_attendance_pct", "fee_outstanding",
        "mentor_name", "status", "semester", "class_teacher_name", "class_teacher_phone", "class_teacher_email",
        "class_teacher_cabin", "counsellor_name", "counsellor_phone", "counsellor_email", "counsellor_cabin",
        "mentor_phone", "mentor_email", "mentor_cabin", "hod_name", "hod_phone", "hod_email"
    ]),
    ("attendance", ["student_id", "course_code", "course_title", "faculty_name", "classes_held", "classes_attended", "current_pct", "required_pct", "classes_needed", "risk_level", "deadline", "recovery_possible"]),
    ("marks", ["student_id", "course_code", "course_title", "assessment_name", "max_marks", "obtained_marks", "percentage", "status"]),
    ("timetable", ["student_id", "day_of_week", "time_slot", "course_code", "course_title", "room_no", "faculty_name", "slot_type"]),
    ("fees", ["student_id", "academic_year", "total_demand", "paid_amount", "outstanding_balance", "due_date", "status", "next_installment_amount", "next_installment_date", "penalty_warning"]),
    ("exams", ["student_id", "exam_type", "course_code", "course_title", "exam_date", "time", "venue", "hall_ticket_status"]),
    ("policies", ["policy_id", "title", "clause_no", "effective_date", "summary", "authority"]),
    ("circulars", ["circular_no", "title", "issued_date", "effective_date", "summary", "issued_by"]),
    ("curriculum", ["regulation", "programme", "total_credits_required", "credits_earned", "credits_remaining", "current_semester_credits", "graduation_eligibility", "next_semester_courses"]),
    ("library_operating_hours", ["day_of_week", "status", "open_time", "close_time", "reading_room_hours", "circulation_counter_hours", "notes"]),
    ("hostels", ["hostel_id", "name", "gender_type", "resident_category", "mess_type", "mess_location", "breakfast_hours", "lunch_hours", "tea_snacks_hours", "dinner_hours", "ac_status", "description"]),
    ("hostel_bus_schedules", ["hostel_route", "shift", "direction", "departure_times_json", "time_range", "stoppages", "effective_date"]),
    ("campus_locations", ["location_id", "room_number", "block", "floor", "description", "latitude", "longitude", "features", "type"]),
    ("campus_navigation_edges", ["edge_id", "source_node", "target_node", "path_name", "direction_instruction", "distance_meters", "is_bidirectional"]),
    ("administrative_procedures", ["procedure_id", "title", "category", "phase1_digital_instructions", "phase2_physical_location", "phase2_steps_json", "fee_amount", "office_location", "sla_turnaround_days"])
]

def migrate(sqlite_path: str, pg_url: str):
    print(f"Connecting to SQLite: {sqlite_path}")
    if not os.path.exists(sqlite_path):
        print(f"ERROR: SQLite database file not found at {sqlite_path}")
        sys.exit(1)

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    print(f"Connecting to PostgreSQL...")
    pg_conn = get_pg_connection(pg_url)
    pg_cur = pg_conn.cursor()

    print("\n1. Creating tables in PostgreSQL...")
    try:
        pg_cur.execute("DROP TABLE IF EXISTS policies, circulars, curriculum CASCADE;")
    except Exception:
        pass
    for ddl in PG_SCHEMAS:
        pg_cur.execute(ddl)
    try:
        pg_cur.execute("ALTER TABLE marks ALTER COLUMN obtained_marks DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE marks ALTER COLUMN percentage DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE marks ALTER COLUMN max_marks DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE marks ALTER COLUMN status DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE timetable ALTER COLUMN slot_type DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE timetable ALTER COLUMN room_no DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE timetable ALTER COLUMN faculty_name DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE fees ALTER COLUMN due_date DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE fees ALTER COLUMN status DROP NOT NULL;")
        pg_cur.execute("ALTER TABLE exams ALTER COLUMN hall_ticket_status DROP NOT NULL;")
    except Exception:
        pass
    pg_conn.commit()
    print("[OK] All PostgreSQL tables verified/created.")

    print("\n2. Migrating rows from SQLite...")
    for table_name, columns in TABLES_TO_MIGRATE:
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        sqlite_cur.execute(f"SELECT {cols_str} FROM {table_name}")
        rows = sqlite_cur.fetchall()
        print(f"  -> Migrating {table_name} ({len(rows)} records)...", end="", flush=True)

        if not rows:
            print(" (Skipped - empty)")
            continue

        # Truncate or clean target table for clean sync
        pg_cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")

        insert_sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
        all_values = [tuple(r[c] for c in columns) for r in rows]
        pg_cur.executemany(insert_sql, all_values)
        pg_conn.commit()
        print(f" [OK: {len(rows)} rows inserted]")

    sqlite_conn.close()
    pg_conn.close()
    print("\n==============================================")
    print(" [SUCCESS] All student data migrated to Neon! ")
    print("==============================================")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_sqlite_to_postgres.py <NEON_POSTGRES_URL>")
        print("Example:")
        print("python migrate_sqlite_to_postgres.py \"postgresql://neondb_owner:xyz@ep-cool-12345.us-east-2.aws.neon.tech/neondb?sslmode=require\"")
        sys.exit(1)

    neon_url = sys.argv[1].strip()
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))
    migrate(db_file, neon_url)
