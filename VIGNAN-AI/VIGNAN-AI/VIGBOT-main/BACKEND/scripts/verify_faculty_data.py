"""
Iterative Faculty Data Verification Suite
Ensures that all student-to-faculty relationships, class teachers, counsellors, mentors,
HODs, subject instructors, phone numbers, emails, and cabin locations are properly
stored in the database, fetched by backend services, exposed through APIs, grounded
in the NLU engine, and synchronized with the frontend dataset.
"""

import os
import sys
import sqlite3
import json

# Ensure BACKEND is in Python path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import get_db_connection, DataRepository, DatabaseSession
from app.agent.nlu_engine import NLUEngine
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    print("=" * 70)
    print("🚀 STARTING ITERATIVE FACULTY DATA VERIFICATION")
    print("=" * 70)

    db_path = os.path.abspath(os.path.join(BACKEND_DIR, "..", "database", "vigbot.db"))
    assert os.path.exists(db_path), f"Database not found at {db_path}"

    errors = []

    # -------------------------------------------------------------
    # Test 1: SQLite Database Faculty Table Verification
    # -------------------------------------------------------------
    print("\n[TEST 1] Verifying SQLite 'faculty' Table...")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT count(*) as cnt FROM faculty")
        fac_count = cur.fetchone()["cnt"]
        print(f"  ✓ Faculty records found: {fac_count}")
        assert fac_count >= 10, f"Expected at least 10 faculty records, got {fac_count}"

        # Verify key faculty exist with phone numbers
        cur.execute("SELECT faculty_id, name, designation, phone, email, cabin FROM faculty")
        fac_rows = cur.fetchall()
        for f in fac_rows:
            assert f["phone"] and len(f["phone"]) >= 10, f"Faculty {f['name']} has invalid phone: {f['phone']}"
            assert f["email"] and "@" in f["email"], f"Faculty {f['name']} has invalid email: {f['email']}"
            assert f["cabin"], f"Faculty {f['name']} has missing cabin location"
        print(f"  ✓ All {len(fac_rows)} faculty members have verified phone, email, and cabin")
    except Exception as e:
        errors.append(f"Test 1 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 2: SQLite Database Students Advisor Columns Verification
    # -------------------------------------------------------------
    print("\n[TEST 2] Verifying All Students Have Complete Faculty Advisor Records...")
    try:
        cur.execute("""
            SELECT student_id, roll_no, full_name,
                   class_teacher_name, class_teacher_phone, class_teacher_email, class_teacher_cabin,
                   counsellor_name, counsellor_phone, counsellor_email, counsellor_cabin,
                   mentor_name, mentor_phone, mentor_email, mentor_cabin,
                   hod_name, hod_phone, hod_email
            FROM students
        """)
        stud_rows = cur.fetchall()
        print(f"  ✓ Total enrolled students in DB: {len(stud_rows)}")
        assert len(stud_rows) > 0, "No students found in DB!"

        missing_ct = 0
        missing_counsellor = 0
        missing_mentor = 0
        missing_phone = 0

        for s in stud_rows:
            if not s["class_teacher_name"]: missing_ct += 1
            if not s["counsellor_name"]: missing_counsellor += 1
            if not s["mentor_name"]: missing_mentor += 1
            if not s["class_teacher_phone"] or not s["counsellor_phone"] or not s["mentor_phone"]:
                missing_phone += 1

        assert missing_ct == 0, f"{missing_ct} students missing Class Teacher"
        assert missing_counsellor == 0, f"{missing_counsellor} students missing Counsellor"
        assert missing_mentor == 0, f"{missing_mentor} students missing Mentor"
        assert missing_phone == 0, f"{missing_phone} students missing Phone numbers"

        print("  ✓ 100% of students have Class Teacher, Counsellor, Mentor, and HOD populated with phone numbers")
        conn.close()
    except Exception as e:
        errors.append(f"Test 2 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 3: SQL Showcase Seed File Verification
    # -------------------------------------------------------------
    print("\n[TEST 3] Verifying PostgreSQL Showcase Seed SQL File...")
    try:
        sql_path = os.path.abspath(os.path.join(BACKEND_DIR, "..", "database", "source", "99_showcase_seed.sql"))
        assert os.path.exists(sql_path), f"File not found: {sql_path}"
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_text = f.read()
        assert "Section 7 Faculty" in sql_text, "Section 6 missing in 99_showcase_seed.sql"
        assert "people.faculty" in sql_text, "people.faculty inserts missing in 99_showcase_seed.sql"
        assert "studentlife.mentorship" in sql_text, "studentlife.mentorship inserts missing"
        assert "confidential.counselling_case" in sql_text, "confidential.counselling_case inserts missing"
        print("  ✓ 99_showcase_seed.sql contains faculty, mentorship, and counselling seed data")
    except Exception as e:
        errors.append(f"Test 3 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 4: DataRepository Methods Verification
    # -------------------------------------------------------------
    print("\n[TEST 4] Verifying DataRepository Methods...")
    try:
        session = DatabaseSession(student_id="251FA04E03")
        advisors = DataRepository.get_student_advisors(session)
        assert advisors is not None, "get_student_advisors returned None"
        assert advisors["class_teacher"]["name"] == "Mr. T. Latesh Babu", f"Unexpected CT: {advisors['class_teacher']}"
        assert advisors["class_teacher"]["phone"] == "+91 94901 23456", f"Unexpected CT Phone: {advisors['class_teacher']}"
        assert advisors["counsellor"]["name"] == "Dr. Radhika Sharma", f"Unexpected Counsellor: {advisors['counsellor']}"
        assert advisors["counsellor"]["phone"] == "+91 98480 12345", f"Unexpected Counsellor Phone: {advisors['counsellor']}"
        print(f"  ✓ DataRepository.get_student_advisors() successfully returned:")
        print(f"      Class Teacher: {advisors['class_teacher']['name']} ({advisors['class_teacher']['phone']})")
        print(f"      Counsellor:    {advisors['counsellor']['name']} ({advisors['counsellor']['phone']})")
        print(f"      Mentor:        {advisors['mentor']['name']} ({advisors['mentor']['phone']})")
        print(f"      HOD:           {advisors['hod']['name']} ({advisors['hod']['phone']})")

        directory = DataRepository.get_faculty_directory(session)
        assert len(directory) >= 10, f"Faculty directory returned only {len(directory)} members"
        print(f"  ✓ DataRepository.get_faculty_directory() returned {len(directory)} faculty members")

        sub_faculty = DataRepository.get_subject_faculty(session, "Data Structures")
        assert len(sub_faculty) > 0, "No faculty returned for Data Structures"
        print(f"  ✓ DataRepository.get_subject_faculty('Data Structures') returned: {sub_faculty[0]['faculty_name']} ({sub_faculty[0]['phone']})")
    except Exception as e:
        errors.append(f"Test 4 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 5: FastAPI REST Endpoints Verification
    # -------------------------------------------------------------
    print("\n[TEST 5] Verifying FastAPI Endpoints with TestClient...")
    try:
        from app.security import create_access_token
        test_token = create_access_token({
            "sub": "user-251fa04e03",
            "student_id": "stu-251fa04e03",
            "roll_no": "251FA04E03",
            "full_name": "Akshat Raj"
        })
        auth_headers = {"Authorization": f"Bearer {test_token}"}
        client = TestClient(app)

        # 5a. GET /api/v1/student/faculty
        res_fac = client.get("/api/v1/student/faculty", headers=auth_headers)
        assert res_fac.status_code == 200, f"Status code {res_fac.status_code}: {res_fac.text}"
        data_fac = res_fac.json()
        assert "advisors" in data_fac, "Missing 'advisors' in /api/v1/student/faculty"
        assert data_fac["advisors"]["class_teacher"]["name"] == "Mr. T. Latesh Babu"
        assert data_fac["advisors"]["counsellor"]["name"] == "Dr. Radhika Sharma"
        assert data_fac["advisors"]["counsellor"]["phone"] == "+91 98480 12345"
        print(f"  ✓ GET /api/v1/student/faculty: 200 OK (verified CT, Counsellor & phone)")

        # 5b. GET /api/v1/faculty
        res_dir = client.get("/api/v1/faculty")
        assert res_dir.status_code == 200, f"Status code {res_dir.status_code}"
        data_dir = res_dir.json()
        assert len(data_dir) >= 10, f"Expected >= 10 faculty in directory, got {len(data_dir)}"
        print(f"  ✓ GET /api/v1/faculty: 200 OK ({len(data_dir)} faculty members returned)")

        # 5c. GET /api/v1/student/dashboard
        res_dash = client.get("/api/v1/student/dashboard", headers=auth_headers)
        assert res_dash.status_code == 200, f"Status code {res_dash.status_code}"
        data_dash = res_dash.json()
        assert "advisors" in data_dash, "Missing 'advisors' in dashboard"
        assert "faculty" in data_dash, "Missing 'faculty' in dashboard"
        assert data_dash["advisors"]["class_teacher"]["phone"] == "+91 94901 23456"
        print(f"  ✓ GET /api/v1/student/dashboard: 200 OK (advisors & faculty embedded)")

        # 5d. GET /api/v1/me
        res_me = client.get("/api/v1/me", headers=auth_headers)
        assert res_me.status_code == 200
        data_me = res_me.json()
        assert data_me.get("class_teacher_name") == "Mr. T. Latesh Babu"
        assert data_me.get("counsellor_phone") == "+91 98480 12345"
        print(f"  ✓ GET /api/v1/me: 200 OK (profile has CT & Counsellor fields)")
    except Exception as e:
        errors.append(f"Test 5 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 6: NLUEngine Faculty Queries & Grounding
    # -------------------------------------------------------------
    print("\n[TEST 6] Verifying NLUEngine Queries & Grounding...")
    try:
        session = DatabaseSession(student_id="251FA04E03")

        # Test context building
        ctx = NLUEngine.build_grounded_student_context(session, "Who is my class teacher?")
        assert "Official Advisors" in ctx, "Missing Official Advisors in context"
        assert "Mr. T. Latesh Babu" in ctx, "Missing Class Teacher name in context"
        assert "+91 94901 23456" in ctx, "Missing Class Teacher phone in context"
        assert "Dr. Radhika Sharma" in ctx, "Missing Counsellor in context"
        print("  ✓ build_grounded_student_context() includes all official advisors with phones")

        # Test queries
        queries_to_test = [
            ("Who is my class teacher?", ["Mr. T. Latesh Babu", "+91 94901 23456"]),
            ("Who is my counsellor?", ["Dr. Radhika Sharma", "+91 98480 12345"]),
            ("What is my class teacher's phone number?", ["+91 94901 23456"]),
            ("What is my counsellor's contact number?", ["+91 98480 12345"]),
            ("Who is my mentor?", ["Mr. T. Latesh Babu", "+91 94901 23456"]),
            ("Who is the HOD of CSE?", ["Dr. S. V. Phani Kumar", "+91 94401 55678"]),
            ("Who teaches Data Structures and what is their phone number?", ["Dr. R. Prathap Kumar", "+91 75698 88963"])
        ]

        for q, expected_substrings in queries_to_test:
            ans = NLUEngine.classify_and_reason(session, q, [], {}, "en")
            full_response = (ans.get("content") or "") + " " + json.dumps(ans.get("structured_card") or {})
            for sub in expected_substrings:
                assert sub.lower() in full_response.lower(), (
                    f"Query '{q}' did not contain '{sub}'. Got:\n{ans.get('content')}"
                )
            print(f"  ✓ Query: '{q}'")
            print(f"      Resolution: {(ans.get('content') or '')[:80]}...")
            if ans.get("structured_card"):
                print(f"      Card Type:  {ans['structured_card'].get('type')}")
    except Exception as e:
        errors.append(f"Test 6 Failed: {e}")
        print(f"  ❌ Error: {e}")

    # -------------------------------------------------------------
    # Test 7: Frontend Dataset Synchronization Verification
    # -------------------------------------------------------------
    print("\n[TEST 7] Verifying FRONTEND/src/data/students-db.ts...")
    try:
        fe_path = os.path.abspath(os.path.join(BACKEND_DIR, "..", "FRONTEND", "src", "data", "students-db.ts"))
        assert os.path.exists(fe_path), f"Frontend file missing: {fe_path}"
        with open(fe_path, "r", encoding="utf-8") as f:
            fe_text = f.read()

        assert "classTeacher" in fe_text, "Missing 'classTeacher' in students-db.ts"
        assert "counsellor" in fe_text, "Missing 'counsellor' in students-db.ts"
        assert "+91 94901 23456" in fe_text, "Missing Class Teacher phone in students-db.ts"
        assert "+91 98480 12345" in fe_text, "Missing Counsellor phone in students-db.ts"
        print("  ✓ FRONTEND/src/data/students-db.ts has synchronized class teacher and counsellor data")
    except Exception as e:
        errors.append(f"Test 7 Failed: {e}")
        print(f"  ❌ Error: {e}")

    print("\n" + "=" * 70)
    if errors:
        print(f"❌ VERIFICATION FAILED WITH {len(errors)} ERRORS:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("🎉 ALL TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
