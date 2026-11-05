import sqlite3
import json

db_path = r"database\vigbot.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check HOD knowledge procedures
cursor.execute("SELECT procedure_id, title FROM knowledge_procedure WHERE title LIKE '%HOD%' OR title LIKE '%Head%'")
procedures = [dict(row) for row in cursor.fetchall()]

# Check attendance updates
cursor.execute("SELECT overall_attendance_pct FROM students LIMIT 10")
attendance_samples = [dict(row) for row in cursor.fetchall()]

cursor.execute("SELECT COUNT(*) as count FROM students WHERE overall_attendance_pct != 0")
attendance_count = dict(cursor.fetchone())

# Check how many total students
cursor.execute("SELECT COUNT(*) as count FROM students")
total_students = dict(cursor.fetchone())

print(json.dumps({
    "procedures": procedures,
    "attendance_samples": attendance_samples,
    "attendance_updated_count": attendance_count['count'],
    "total_students": total_students['count']
}, indent=2))

conn.close()
