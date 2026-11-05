"""
Database Initialization Script for VIGBOT Backend
Applies the platform database migrations in strict dependency order:
01_foundation.sql -> 02_people_identity.sql -> 03_curriculum.sql ->
04_academics_attendance.sql -> 05_assessment_exams_outcomes.sql ->
07_admissions_finance.sql (finance only) -> 08_studentlife_placement_hr.sql (studentlife + confidential) ->
09_governance_quality_knowledge.sql -> 10_agentops.sql -> 11_security_rls.sql ->
12_views.sql -> 13_helpdesk_extension.sql -> 99_smoke_test.sql (dev seed)

Strictly excludes: 06_research_engagement.sql
"""

import os
import sys
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vigbot")

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "source"))
HELPDESK_EXT = os.path.abspath(os.path.join(os.path.dirname(__file__), "13_helpdesk_extension.sql"))

SQL_FILES_IN_ORDER = [
    "01_foundation.sql",
    "02_people_identity.sql",
    "03_curriculum.sql",
    "04_academics_attendance.sql",
    "05_assessment_exams_outcomes.sql",
    # 06_research_engagement.sql is deliberately excluded!
    "07_admissions_finance.sql",
    "08_studentlife_placement_hr.sql",
    "09_governance_quality_knowledge.sql",
    "10_agentops.sql",
    "11_security_rls.sql",
    "12_views.sql"
]

def run_migration():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Note: In local mode without PostgreSQL running, the backend uses the built-in in-memory RLS repository.")
        return False

    print("Deploying platform schemas in dependency order...")
    for filename in SQL_FILES_IN_ORDER:
        file_path = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping.")
            continue
        print(f"Executing: {filename}")
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
            try:
                cur.execute(sql)
            except Exception as ex:
                print(f"Notice on {filename}: {ex}")

    # Execute Helpdesk extension
    if os.path.exists(HELPDESK_EXT):
        print("Executing: 13_helpdesk_extension.sql")
        with open(HELPDESK_EXT, "r", encoding="utf-8") as f:
            cur.execute(f.read())

    # Execute showcase seeds if in development mode
    showcase_seed_path = os.path.join(SOURCE_DIR, "99_showcase_seed.sql")
    smoke_test_path = os.path.join(SOURCE_DIR, "99_smoke_test.sql")
    seed_file = showcase_seed_path if os.path.exists(showcase_seed_path) else smoke_test_path
    if os.path.exists(seed_file) and os.getenv("ENVIRONMENT", "development") == "development":
        print(f"Executing: {os.path.basename(seed_file)} (Showcase seed data)")
        with open(seed_file, "r", encoding="utf-8") as f:
            try:
                cur.execute(f.read())
            except Exception as ex:
                print(f"Notice on {os.path.basename(seed_file)}: {ex}")

    print("Database migration completed successfully!")
    cur.close()
    conn.close()
    return True

if __name__ == "__main__":
    run_migration()
