import os
import sys
import math
import sqlite3
import psycopg
from app.config import settings

STUDENTS_DATA = [
    # SL, Regd No, Name, DS, DBMSIS, OOPTJ, DLDES, AI, DMS-MTA, DS-L, DBMSIS-L, OOPTJ-L, DWAV, Total
    (1, "251FA04131", "SAHIL SHARAD", 80.36, 81.82, 69.77, 81.97, 80.0, 82.35, 80.0, 80.56, 75.0, 70.83, 79.0),
    (2, "251FA04D46", "VENNAPUSA SAI NIYONTHI", 94.64, 90.91, 86.05, 91.8, 92.73, 88.24, 87.5, 91.67, 90.62, 87.5, 91.0),
    (3, "251FA04D56", "VUKOTI KARTHIK", 91.07, 87.27, 76.74, 81.97, 96.36, 94.12, 92.5, 91.67, 87.5, 89.58, 89.0),
    (4, "251FA04D69", "YALAM AMRUTHA VARSHINI", 91.07, 87.27, 95.35, 91.8, 90.91, 88.24, 92.5, 91.67, 100.0, 91.67, 92.0),
    (5, "251FA04D73", "YALAVARTHI NEHA SRI", 92.86, 87.27, 90.7, 93.44, 89.09, 92.16, 90.0, 91.67, 100.0, 87.5, 92.0),
    (6, "251FA04D76", "YANDAPALLI VAMSI NAGA SANTHOSH", 78.57, 74.55, 81.4, 81.97, 74.55, 80.39, 75.0, 88.89, 100.0, 79.17, 81.0),
    (7, "251FA04D80", "YARAMATI ANIRUDH", 89.29, 89.09, 90.7, 91.8, 90.91, 92.16, 92.5, 91.67, 96.88, 91.67, 92.0),
    (8, "251FA04D81", "YARAMATI MANISHANKAR CHOWDARY", 82.14, 83.64, 83.72, 85.25, 85.45, 86.27, 90.0, 83.33, 100.0, 81.25, 86.0),
    (9, "251FA04D83", "YARRAPATHRUNI VENKATA GANGADHAR", 87.5, 94.55, 90.7, 88.52, 92.73, 90.2, 92.5, 91.67, 100.0, 89.58, 92.0),
    (10, "251FA04D86", "YASASWINI SURYADEVARA", 92.86, 98.18, 88.37, 93.44, 92.73, 98.04, 92.5, 83.33, 91.67, 91.67, 94.0),
    (11, "251FA04D87", "YELCHURI VENKATA KARTHIKEYA KUMAR", 78.57, 76.36, 81.4, 90.16, 80.0, 80.39, 85.0, 75.0, 90.62, 77.08, 82.0),
    (12, "251FA04D93", "YERRAMSETTI AKHILA", 91.07, 87.27, 74.42, 85.25, 87.27, 90.2, 85.0, 83.33, 84.38, 81.25, 86.0),
    (13, "251FA04D94", "YERUVA HARINI", 66.07, 60.0, 60.47, 75.41, 70.91, 76.47, 72.5, 91.67, 90.62, 85.42, 74.0),
    (14, "251FA04D95", "ABHISHEK KUMAR THAKUR", 89.29, 78.18, 86.05, 93.44, 87.27, 92.16, 87.5, 100.0, 100.0, 91.67, 90.0),
    (15, "251FA04D97", "ADAPA ABHISEK", 87.5, 81.82, 74.42, 90.16, 80.0, 82.35, 72.5, 86.11, 81.25, 72.92, 82.0),
    (16, "251FA04E03", "AKSHAT RAJ", 85.71, 83.64, 79.07, 86.89, 90.91, 94.12, 85.0, 94.44, 87.5, 89.58, 88.0),
    (17, "251FA04E05", "ALA SRIDHAR", 83.93, 74.55, 81.4, 83.61, 85.45, 80.39, 85.0, 91.67, 100.0, 89.58, 85.0),
    (18, "251FA04E07", "ALAPATI BHARGHAV CHAITANYA NAIDU", 83.93, 72.73, 83.72, 86.89, 89.09, 86.27, 85.0, 86.11, 100.0, 93.75, 87.0),
    (19, "251FA04E08", "ALASYAM SIRISHA", 89.29, 85.45, 79.07, 95.08, 81.82, 90.2, 70.0, 91.67, 100.0, 95.83, 88.0),
    (20, "251FA04E10", "ALLADA VEERA SAI SANTOSH", 83.93, 70.91, 69.77, 85.25, 80.0, 84.31, 60.0, 69.44, 81.25, 68.75, 77.0),
    (21, "251FA04E12", "ALLURI VISHNUVARDHAN", 89.29, 83.64, 86.05, 90.16, 85.45, 84.31, 70.0, 83.33, 90.62, 79.17, 85.0),
    (22, "251FA04E13", "AMAN KUMAR", 85.71, 81.82, 74.42, 83.61, 90.91, 90.2, 77.5, 88.89, 100.0, 77.08, 85.0),
    (23, "251FA04E14", "AMARANENI HARISH", 89.29, 89.09, 79.07, 86.89, 92.73, 90.2, 85.0, 86.11, 100.0, 79.17, 88.0),
    (24, "251FA04E19", "ANDRAJU MONIKA", 87.5, 78.18, 79.07, 85.25, 87.27, 82.35, 92.5, 88.89, 87.5, 87.5, 86.0),
    (25, "251FA04E21", "ANKIT RAJ", 96.43, 87.27, 93.02, 93.44, 90.91, 92.16, 92.5, 94.44, 96.88, 87.5, 93.0),
    (26, "251FA04E22", "ANNA NAGA VENKATA PRAGNA", 92.86, 85.45, 88.37, 91.8, 81.82, 92.16, 85.0, 91.67, 100.0, 87.5, 90.0),
    (27, "251FA04E24", "ARIKATLA MANI CHAND", 87.5, 90.91, 81.4, 85.25, 89.09, 88.24, 85.0, 80.56, 93.75, 91.67, 88.0),
    (28, "251FA04E26", "ARUN SHARMA", 89.29, 85.45, 76.74, 86.89, 94.55, 98.04, 85.0, 91.67, 100.0, 83.33, 89.0),
    (29, "251FA04E27", "ATTI ADITHYA KUMAR", 76.79, 67.27, 76.74, 80.33, 85.45, 82.35, 80.0, 83.33, 90.62, 66.67, 79.0),
    (30, "251FA04E28", "AYUSH KUMAR", 89.29, 83.64, 81.4, 86.89, 85.45, 94.12, 77.5, 83.33, 96.88, 89.58, 87.0),
    (31, "251FA04E32", "BALE SIRISHA", 85.71, 74.55, 79.07, 95.08, 89.09, 90.2, 92.5, 91.67, 100.0, 91.67, 89.0),
    (32, "251FA04E37", "BATHULA ROHITH", 82.14, 90.91, 74.42, 86.89, 87.27, 86.27, 77.5, 75.0, 90.62, 83.33, 85.0),
    (33, "251FA04E41", "BEVARA PRASANNA", 87.5, 83.64, 88.37, 88.52, 83.64, 90.2, 77.5, 91.67, 96.88, 87.5, 88.0),
    (34, "251FA04E47", "BITU KUMAR", 89.29, 87.27, 76.74, 86.89, 92.73, 94.12, 92.5, 97.22, 100.0, 85.42, 90.0),
    (35, "251FA04E50", "BODDU VENKATA SIREESH CHAND", 96.43, 92.73, 88.37, 93.44, 85.45, 94.12, 90.0, 77.78, 96.88, 91.67, 92.0),
    (36, "251FA04E51", "BODE VEDESH JEEVAN", 89.29, 83.64, 86.05, 85.25, 81.82, 84.31, 75.0, 75.0, 75.0, 77.08, 83.0),
    (37, "251FA04E52", "BOGALA AMULYA", 85.71, 87.27, 79.07, 91.8, 90.91, 94.12, 95.0, 83.33, 87.5, 87.5, 89.0),
    (38, "251FA04E53", "BOJJA LAKSHMI", 89.29, 87.27, 88.37, 85.25, 83.64, 86.27, 85.0, 80.56, 93.75, 81.25, 87.0),
    (39, "251FA04E57", "BOPPANA PRADEESH", 82.14, 80.0, 81.4, 81.97, 85.45, 84.31, 72.5, 86.11, 81.25, 79.17, 82.0),
    (40, "251FA04E64", "CHALLA DEEKSHITHA", 96.43, 96.36, 97.67, 98.36, 94.55, 94.12, 95.0, 91.67, 100.0, 100.0, 97.0),
    (41, "251FA04E65", "CHALLAGALLA DEEPTHI", 91.07, 81.82, 90.7, 93.44, 89.09, 92.16, 92.5, 80.56, 96.88, 95.83, 91.0),
    (42, "251FA04E68", "CHAPPIDI CHANDRA SEKHAR", 62.5, 54.55, 60.47, 67.21, 74.55, 82.35, 85.0, 83.33, 71.88, 72.92, 71.0),
    (43, "251FA04E69", "CHARUGUNDLA AJAY KUMAR", 91.07, 96.36, 90.7, 90.16, 92.73, 98.04, 100.0, 97.22, 90.62, 83.33, 93.0),
    (44, "251FA04E72", "CHEGONDI NAGA DURGA SATHVIKA", 73.21, 74.55, 65.12, 78.69, 81.82, 82.35, 75.0, 69.44, 78.12, 79.17, 77.0),
    (45, "251FA04E74", "CHENNAREDDY LAVANYA", 91.07, 90.91, 83.72, 86.89, 92.73, 88.24, 85.0, 86.11, 93.75, 87.5, 89.0),
    (46, "251FA04E75", "CHEPALA MADHU SANJAY KRISHNA", 67.86, 78.18, 81.4, 83.61, 87.27, 80.39, 87.5, 75.0, 62.5, 77.08, 79.0),
    (47, "251FA04E79", "CHITYALA VENKATA PRATAP REDDY", 75.0, 80.0, 83.72, 90.16, 85.45, 92.16, 85.0, 91.67, 90.62, 87.5, 86.0),
    (48, "251FA04E80", "CHODA NEHAMRUTHA", 96.43, 92.73, 90.7, 93.44, 96.36, 96.08, 92.5, 91.67, 100.0, 91.67, 95.0),
    (49, "251FA04E85", "DARAM ABHINAI SAI REDDY", 73.21, 78.18, 60.47, 68.85, 72.73, 80.39, 70.0, 75.0, 100.0, 79.17, 75.0),
    (50, "251FA04E86", "DARAM RUPA SRINIDHI", 91.07, 89.09, 88.37, 91.8, 94.55, 92.16, 85.0, 83.33, 90.62, 87.5, 90.0),
    (51, "251FA04E89", "DESAVATH VENKATESWARA NAIK", 87.5, 85.45, 76.74, 85.25, 89.09, 92.16, 85.0, 75.0, 100.0, 85.42, 86.0),
    (52, "251FA04E92", "DHULIPALLA SIREESHA", 82.14, 70.91, 76.74, 77.05, 80.0, 92.16, 82.5, 83.33, 100.0, 77.08, 81.0),
    (53, "251FA04E94", "EDIGA VIJAY CHANDRA", 75.0, 78.18, 67.44, 77.05, 81.82, 86.27, 85.0, 75.0, 81.25, 81.25, 79.0),
    (54, "251FA04E96", "ESHANA RAI", 85.71, 80.0, 69.77, 85.25, 78.18, 90.2, 77.5, 72.22, 100.0, 89.58, 83.0),
    (55, "251FA04F05", "GANGAVARAM CHIRUDEEP", 83.93, 85.45, 72.09, 77.05, 92.73, 96.08, 85.0, 100.0, 100.0, 85.42, 87.0),
    (56, "251FA04F06", "GANGIREDDY MANUSREE", 96.43, 92.73, 86.05, 93.44, 92.73, 98.04, 92.5, 94.44, 96.88, 95.83, 94.0),
    (57, "251FA04F08", "GANITHI SREE YAMINI", 89.29, 87.27, 88.37, 86.89, 89.09, 94.12, 92.5, 91.67, 90.62, 91.67, 91.0),
    (58, "251FA04F15", "GODA POOJITH", 83.93, 83.64, 93.02, 93.44, 92.73, 94.12, 85.0, 83.33, 90.62, 91.67, 90.0),
    (59, "251FA04F20", "GOLLA YOGANANDU", 78.57, 74.55, 69.77, 78.69, 80.0, 90.2, 70.0, 75.0, 90.62, 79.17, 79.0),
    (60, "251FA04F21", "GONE HARISHA", 96.43, 89.09, 93.02, 95.08, 89.09, 94.12, 92.5, 91.67, 90.62, 91.67, 93.0),
    (61, "251FA04F25", "GOSU NAGAKOWSHIK", 87.5, 83.64, 72.09, 83.61, 90.91, 92.16, 85.0, 83.33, 90.62, 81.25, 85.0),
    (62, "251FA04F26", "GOTTAM VARSHITHA", 91.07, 89.09, 86.05, 91.8, 92.73, 90.2, 85.0, 83.33, 90.62, 87.5, 89.0),
    (63, "251FA04F34", "GUNJA CHANDU", 96.43, 89.09, 86.05, 91.8, 90.91, 96.08, 92.5, 97.22, 90.62, 91.67, 93.0),
    (64, "251FA04F38", "GUDIPATI MANASA", 96.43, 94.55, 83.72, 93.44, 85.45, 92.16, 85.0, 77.78, 100.0, 89.58, 91.0),
    (65, "251FA04F40", "HEMASRI ANNAPAREDDY", 92.86, 85.45, 88.37, 85.25, 90.91, 94.12, 77.5, 100.0, 96.88, 91.67, 90.0),
    (66, "251FA04F43", "IRUVURI GOKUL MANIDEEP", 82.14, 76.36, 69.77, 78.69, 83.64, 90.2, 72.5, 83.33, 90.62, 77.08, 81.0),
    (67, "251FA04F45", "JAMPANI VENKATA LOKESH REDDY", 78.57, 87.27, 79.07, 91.8, 87.27, 86.27, 75.0, 72.22, 90.62, 83.33, 84.0),
    (68, "251FA04F90", "KISHAN KUMAR", 89.29, 85.45, 81.4, 91.8, 89.09, 90.2, 92.5, 100.0, 100.0, 87.5, 90.0),
    (69, "251FA04G37", "MANUKONDA CHARISHMA SIVANI", 83.93, 90.91, 83.72, 91.8, 89.09, 82.35, 100.0, 100.0, 100.0, 91.67, 91.0),
    (70, "251FA04G38", "MANVI MANOGNA", 91.07, 87.27, 93.02, 90.16, 80.0, 96.08, 77.5, 91.67, 100.0, 87.5, 90.0)
]

SUBJECT_METADATA = [
    ("DS", "DS-25CS201", "Data Structures", "Dr. K. Srinivasa Rao", 56),
    ("DBMSIS", "DBMS-25CS203", "Database Management Systems & Information Systems", "Dr. M. Radhika", 55),
    ("OOPTJ", "OOPS-25CS204", "Object Oriented Programming through Java", "Prof. T. Venkateswarlu", 43),
    ("DLDES", "DLD-25CS205", "Digital Logic Design & Embedded Systems", "Dr. G. Ramu", 61),
    ("AI", "AI-24CS302", "Artificial Intelligence", "Dr. S. Balamurugan", 55),
    ("DMS-MTA", "DMS-25MT202", "Discrete Mathematical Structures - MTA", "Dr. P. V. S. Anand", 51),
    ("DS-L", "DS-25CS201L", "Data Structures Laboratory", "Dr. K. Srinivasa Rao", 40),
    ("DBMSIS-L", "DBMS-25CS203L", "DBMS Laboratory", "Dr. M. Radhika", 36),
    ("OOPTJ-L", "OOPS-25CS204L", "Java Programming Laboratory", "Prof. T. Venkateswarlu", 32),
    ("DWAV", "DW-25CS202", "Data Wrangling, Analytics and Visualization", "Dr. N. Veeranjaneyulu", 48),
]

def migrate():
    db_url = settings.DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
    print("Connecting to Neon PostgreSQL...", flush=True)
    conn = psycopg.connect(db_url)
    
    with conn.cursor() as cur:
        # Collect existing student IDs for these roll numbers
        roll_list = [s[1] for s in STUDENTS_DATA]
        cur.execute("SELECT roll_no, student_id FROM students WHERE roll_no = ANY(%s);", (roll_list,))
        existing_map = dict(cur.fetchall())
        
        all_attendance_rows = []
        student_ids_to_clean = []
        
        for student in STUDENTS_DATA:
            sl, roll_no, name, ds, dbmsis, ooptj, dldes, ai, dms_mta, ds_l, dbmsis_l, ooptj_l, dwav, total_pct = student
            sid = existing_map.get(roll_no, f"stu-{roll_no.lower()}")
            
            # Upsert into students by roll_no
            cur.execute("""
                INSERT INTO students (
                    student_id, user_id, roll_no, username, password_hash, full_name, 
                    programme_code, programme_name, department_code, batch_label, section_code, 
                    current_year_of_study, overall_attendance_pct, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 
                    'BTECH-CSE', 'B.Tech Computer Science and Engineering', 'CSE', '2025-2029', 'SEC-A',
                    2, %s, 'ACTIVE'
                )
                ON CONFLICT (roll_no) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    overall_attendance_pct = EXCLUDED.overall_attendance_pct
                RETURNING student_id;
            """, (
                sid, sid, roll_no, roll_no.lower(),
                "pbkdf2_sha256$29000$mock$hashedpassword", name, total_pct
            ))
            actual_sid = cur.fetchone()[0]
            student_ids_to_clean.append(actual_sid)
            student_ids_to_clean.append(roll_no)
            
            # Attendance rows
            scores = [ds, dbmsis, ooptj, dldes, ai, dms_mta, ds_l, dbmsis_l, ooptj_l, dwav]
            for (sub_key, course_code, course_title, faculty, held), current_pct in zip(SUBJECT_METADATA, scores):
                attended = round((held * current_pct) / 100.0)
                risk_level = "HIGH" if current_pct < 75.0 else ("MEDIUM" if current_pct < 80.0 else "LOW")
                needed = max(0, math.ceil((0.75 * held - attended) / (1 - 0.75))) if current_pct < 75.0 else 0
                all_attendance_rows.append((
                    actual_sid, course_code, course_title, faculty,
                    held, attended, current_pct, 75.0,
                    needed, risk_level, '2026-11-20', 1
                ))
                
        # Clean previous attendance records for these students in one operation
        cur.execute("DELETE FROM attendance WHERE student_id = ANY(%s);", (student_ids_to_clean,))
        
        # Insert all 700 attendance rows in batch
        cur.executemany("""
            INSERT INTO attendance (
                student_id, course_code, course_title, faculty_name,
                classes_held, classes_attended, current_pct, required_pct,
                classes_needed, risk_level, deadline, recovery_possible
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            );
        """, all_attendance_rows)
        
        # Circular update
        cur.execute("""
            INSERT INTO circulars (
                circular_no, title, issued_date, effective_date, summary, issued_by
            ) VALUES (
                'VSH/TRANSPORT/2026/09/01',
                'Hostel Residents Bus Transport Timetable (KM Hostel, Villas SP Residency, AP/AR/AA/AO)',
                '2026-10-01',
                '2026-10-01',
                'Official bus schedule for boys hostel residents w.e.f 01.10.2026. Covers morning shifts (7:45 AM - 11:35 AM) and evening shifts (1:45 PM - 9:00 PM) for KM Hostel, Villas SP Residency, and AP/AR/AA/AO Hostels.',
                'Dr. Y. Vara Prasad, Chief Warden'
            )
            ON CONFLICT (circular_no) DO UPDATE SET
                title = EXCLUDED.title,
                summary = EXCLUDED.summary,
                issued_by = EXCLUDED.issued_by;
        """)
        
        conn.commit()
        print(f"Neon migration finished successfully! Processed {len(STUDENTS_DATA)} students and {len(all_attendance_rows)} attendance records.", flush=True)

if __name__ == "__main__":
    migrate()
