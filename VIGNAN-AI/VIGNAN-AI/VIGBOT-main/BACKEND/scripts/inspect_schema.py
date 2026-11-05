import os
import sqlite3
import json

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("=== TABLES IN DATABASE ===")
for t in tables:
    tname = t[0]
    cols = cur.execute(f"PRAGMA table_info({tname})").fetchall()
    cnt = cur.execute(f"SELECT count(*) FROM {tname}").fetchone()[0]
    print(f"\nTable: {tname} (count: {cnt})")
    for c in cols:
        print(f"  - {c['name']} ({c['type']})")

print("\n=== SAMPLE STUDENT RECORD (251FA04E03) ===")
student = cur.execute("SELECT * FROM students WHERE roll_no = '251FA04E03'").fetchone()
if student:
    print(json.dumps(dict(student), indent=2, default=str))
else:
    first_s = cur.execute("SELECT * FROM students LIMIT 1").fetchone()
    print(json.dumps(dict(first_s), indent=2, default=str) if first_s else "No students found")

print("\n=== DISTINCT MENTOR / COUNSELLOR / FACULTY IN STUDENTS TABLE ===")
cols_in_students = [c['name'] for c in cur.execute("PRAGMA table_info(students)").fetchall()]
for col in cols_in_students:
    if any(k in col.lower() for k in ['mentor', 'counsel', 'teacher', 'faculty', 'advisor', 'phone', 'mobile', 'cabin']):
        print(f"Column found in students: {col}")
        vals = cur.execute(f"SELECT DISTINCT {col} FROM students LIMIT 5").fetchall()
        print(f"  Values: {[v[0] for v in vals]}")

conn.close()
