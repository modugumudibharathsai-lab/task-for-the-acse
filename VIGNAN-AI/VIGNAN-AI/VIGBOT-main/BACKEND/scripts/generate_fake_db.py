"""
Generate Showcase Database for VIGBOT VIGBOT
University: Vignan Foundation for Science, Technology and Research (VFSTR)
Department: Computer Science & Engineering (CSE)
Batch: 2024-2028 (Second Year, Section 7)
"""

import os
import sqlite3
import uuid
import datetime
import json

# 70 Authenticated Students of VFSTR CSE Section 7
STUDENTS_DATA = [
    # (RegdNo, Name, SGPA_II, CGPA, Att_DS, Att_DBMSIS, Att_OOPTJ, Att_DLDES, Att_AI, Att_DMS, Att_DSL, Att_DBMSL, Att_OOPTJL, Att_DWAV, Att_Lib, Att_Coun, Total_Att)
    ("251FA04131", "SAHIL SHARAD", 0.0, 7.39, 53.57, 65.52, 33.33, 58.62, 57.14, 52.38, 66.67, 18.18, 60.00, 47.62, 25.0, 100.0, 54.0),
    ("251FA04D46", "VENNAPUSA SAI NIYONTHI", 8.16, 8.22, 92.86, 86.21, 80.95, 93.10, 95.24, 95.24, 83.33, 100.0, 80.00, 80.95, 75.0, 66.67, 89.0),
    ("251FA04D56", "VUKOTI KARTHIK", 7.58, 7.76, 89.29, 82.76, 57.14, 72.41, 95.24, 95.24, 83.33, 100.0, 80.00, 85.71, 25.0, 66.67, 82.0),
    ("251FA04D69", "YALAM AMRUTHA VARSHINI", 8.37, 8.59, 96.43, 89.66, 95.24, 93.10, 95.24, 95.24, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 94.0),
    ("251FA04D73", "YALAVARTHI NEHA SRI", 7.51, 7.46, 92.86, 86.21, 90.48, 93.10, 85.71, 95.24, 83.33, 100.0, 100.0, 80.95, 75.0, 100.0, 91.0),
    ("251FA04D76", "YANDAPALLI VAMSI NAGA SANTHOSH", 7.30, 7.18, 64.29, 58.62, 71.43, 75.86, 52.38, 66.67, 50.00, 63.64, 100.0, 80.95, 75.0, 66.67, 68.0),
    ("251FA04D80", "YARAMATI ANIRUDH", 6.71, 6.72, 89.29, 89.66, 90.48, 89.66, 80.95, 85.71, 83.33, 72.73, 100.0, 90.48, 75.0, 100.0, 88.0),
    ("251FA04D81", "YARAMATI MANISHANKAR CHOWDARY", 6.57, 6.29, 82.14, 89.66, 80.95, 86.21, 80.95, 90.48, 83.33, 63.64, 100.0, 76.19, 75.0, 100.0, 85.0),
    ("251FA04D83", "YARRAPATHRUNI VENKATA GANGADHAR", 8.53, 8.48, 92.86, 96.55, 100.0, 86.21, 100.0, 100.0, 100.0, 100.0, 100.0, 95.24, 100.0, 66.67, 96.0),
    ("251FA04D86", "YASASWINI SURYADEVARA", 8.69, 8.93, 96.43, 100.0, 95.24, 93.10, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 99.0),
    ("251FA04D87", "YELCHURI VENKATA KARTHIKEYA KUMAR", 6.66, 6.55, 71.43, 62.07, 76.19, 96.55, 80.95, 90.48, 83.33, 72.73, 100.0, 76.19, 100.0, 33.33, 81.0),
    ("251FA04D93", "YERRAMSETTI AKHILA", 7.82, 7.61, 75.00, 75.86, 52.38, 68.97, 85.71, 90.48, 83.33, 72.73, 80.00, 57.14, 25.0, 100.0, 74.0),
    ("251FA04D94", "YERUVA HARINI", 7.17, 7.31, 67.86, 58.62, 57.14, 75.86, 76.19, 80.95, 50.00, 100.0, 80.00, 76.19, 75.0, 33.33, 71.0),
    ("251FA04D95", "ABHISHEK KUMAR THAKUR", 7.47, 7.37, 89.29, 79.31, 85.71, 96.55, 80.95, 95.24, 77.78, 100.0, 100.0, 90.48, 50.0, 100.0, 89.0),
    ("251FA04D97", "ADAPA ABHISEK", 6.52, 6.42, 89.29, 82.76, 76.19, 93.10, 95.24, 95.24, 83.33, 100.0, 80.00, 71.43, 75.0, 100.0, 87.0),
    ("251FA04E03", "AKSHAT RAJ", 8.79, 8.79, 75.00, 79.31, 61.90, 79.31, 95.24, 100.0, 72.22, 100.0, 100.0, 85.71, 0.0, 100.0, 82.0),
    ("251FA04E05", "ALA SRIDHAR", 6.96, 6.87, 85.71, 68.97, 76.19, 86.21, 95.24, 85.71, 83.33, 100.0, 100.0, 90.48, 25.0, 66.67, 85.0),
    ("251FA04E07", "ALAPATI BHARGHAV CHAITANYA NAIDU", 7.18, 7.29, 82.14, 68.97, 76.19, 93.10, 95.24, 85.71, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 86.0),
    ("251FA04E08", "ALASYAM SIRISHA", 7.15, 7.25, 89.29, 82.76, 71.43, 89.66, 85.71, 95.24, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 88.0),
    ("251FA04E10", "ALLADA VEERA SAI SANTOSH", 6.76, 6.41, 85.71, 68.97, 61.90, 86.21, 76.19, 90.48, 61.11, 90.91, 100.0, 76.19, 50.0, 100.0, 79.0),
    ("251FA04E12", "ALLURI VISHNUVARDHAN", 6.89, 6.85, 89.29, 86.21, 80.95, 89.66, 95.24, 95.24, 83.33, 100.0, 100.0, 80.95, 75.0, 100.0, 90.0),
    ("251FA04E13", "AMAN KUMAR", 8.23, 8.09, 75.00, 75.86, 52.38, 75.86, 95.24, 95.24, 66.67, 63.64, 100.0, 66.67, 0.0, 100.0, 76.0),
    ("251FA04E14", "AMARANENI HARISH", 7.57, 7.19, 92.86, 82.76, 66.67, 79.31, 95.24, 95.24, 83.33, 100.0, 80.00, 76.19, 50.0, 100.0, 86.0),
    ("251FA04E19", "ANDRAJU MONIKA", 8.72, 8.65, 92.86, 65.52, 76.19, 89.66, 85.71, 85.71, 83.33, 90.91, 80.00, 90.48, 75.0, 66.67, 84.0),
    ("251FA04E21", "ANKIT RAJ", 8.96, 8.81, 100.0, 89.66, 100.0, 96.55, 100.0, 95.24, 72.22, 100.0, 100.0, 90.48, 75.0, 100.0, 95.0),
    ("251FA04E22", "ANNA NAGA VENKATA PRAGNA", 8.73, 9.10, 92.86, 82.76, 95.24, 93.10, 85.71, 95.24, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 91.0),
    ("251FA04E24", "ARIKATLA MANI CHAND", 7.82, 7.69, 96.43, 89.66, 80.95, 89.66, 95.24, 100.0, 83.33, 100.0, 100.0, 90.48, 50.0, 100.0, 92.0),
    ("251FA04E26", "ARUN SHARMA", 8.01, 8.01, 82.14, 72.41, 52.38, 72.41, 90.48, 95.24, 66.67, 72.73, 100.0, 66.67, 0.0, 100.0, 76.0),
    ("251FA04E27", "ATTI ADITHYA KUMAR", 6.82, 6.79, 71.43, 68.97, 80.95, 86.21, 85.71, 95.24, 55.56, 72.73, 80.00, 66.67, 25.0, 66.67, 76.0),
    ("251FA04E28", "AYUSH KUMAR", 8.47, 8.33, 78.57, 79.31, 66.67, 79.31, 85.71, 95.24, 55.56, 72.73, 100.0, 76.19, 0.0, 100.0, 78.0),
    ("251FA04E32", "BALE SIRISHA", 6.69, 6.75, 85.71, 72.41, 66.67, 93.10, 90.48, 90.48, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 86.0),
    ("251FA04E37", "BATHULA ROHITH", 7.99, 8.11, 89.29, 86.21, 66.67, 86.21, 95.24, 90.48, 55.56, 72.73, 80.00, 71.43, 75.0, 100.0, 81.0),
    ("251FA04E41", "BEVARA PRASANNA", 8.30, 8.50, 92.86, 89.66, 90.48, 86.21, 95.24, 100.0, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 92.0),
    ("251FA04E47", "BITU KUMAR", 6.93, 6.64, 92.86, 82.76, 66.67, 86.21, 95.24, 100.0, 83.33, 100.0, 100.0, 85.71, 50.0, 100.0, 88.0),
    ("251FA04E50", "BODDU VENKATA SIREESH CHAND", 7.71, 7.83, 96.43, 89.66, 90.48, 89.66, 90.48, 95.24, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 92.0),
    ("251FA04E51", "BODE VEDESH JEEVAN", 6.62, 6.28, 82.14, 89.66, 85.71, 93.10, 80.95, 76.19, 88.89, 72.73, 80.00, 90.48, 100.0, 66.67, 86.0),
    ("251FA04E52", "BOGALA AMULYA", 6.87, 6.83, 85.71, 82.76, 76.19, 89.66, 90.48, 100.0, 88.89, 100.0, 73.33, 90.48, 50.0, 100.0, 87.0),
    ("251FA04E53", "BOJJA LAKSHMI", 7.74, 7.49, 89.29, 86.21, 100.0, 96.55, 90.48, 90.48, 83.33, 81.82, 93.33, 90.48, 100.0, 100.0, 91.0),
    ("251FA04E57", "BOPPANA PRADEESH", 7.05, 7.07, 82.14, 79.31, 85.71, 89.66, 85.71, 95.24, 77.78, 100.0, 100.0, 85.71, 75.0, 66.67, 87.0),
    ("251FA04E64", "CHALLA DEEKSHITHA", 7.89, 7.85, 100.0, 93.10, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 33.33, 99.0),
    ("251FA04E65", "CHALLAGALLA DEEPTHI", 8.58, 8.55, 96.43, 79.31, 95.24, 96.55, 95.24, 100.0, 83.33, 90.91, 93.33, 100.0, 75.0, 100.0, 93.0),
    ("251FA04E68", "CHAPPIDI CHANDRA SEKHAR", 6.40, 6.15, 50.00, 41.38, 47.62, 62.07, 80.95, 71.43, 66.67, 90.91, 60.00, 57.14, 25.0, 100.0, 61.0),
    ("251FA04E69", "CHARUGUNDLA AJAY KUMAR", 8.77, 8.99, 96.43, 100.0, 100.0, 100.0, 100.0, 95.24, 88.89, 100.0, 100.0, 100.0, 100.0, 100.0, 99.0),
    ("251FA04E72", "CHEGONDI NAGA DURGA SATHVIKA", 7.09, 6.89, 75.00, 75.86, 61.90, 82.76, 90.48, 85.71, 72.22, 72.73, 80.00, 85.71, 50.0, 100.0, 79.0),
    ("251FA04E74", "CHENNAREDDY LAVANYA", 7.28, 7.17, 96.43, 89.66, 90.48, 89.66, 95.24, 100.0, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 93.0),
    ("251FA04E75", "CHEPALA MADHU SANJAY KRISHNA", 7.08, 6.66, 71.43, 79.31, 85.71, 93.10, 95.24, 95.24, 83.33, 36.36, 40.00, 71.43, 100.0, 66.67, 79.0),
    ("251FA04E79", "CHITYALA VENKATA PRATAP REDDY", 7.71, 7.82, 67.86, 79.31, 80.95, 89.66, 90.48, 95.24, 83.33, 100.0, 80.00, 100.0, 75.0, 100.0, 86.0),
    ("251FA04E80", "CHODA NEHAMRUTHA", 8.16, 7.96, 96.43, 89.66, 90.48, 93.10, 95.24, 100.0, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 94.0),
    ("251FA04E85", "DARAM ABHINAI SAI REDDY", 7.51, 7.46, 78.57, 65.52, 61.90, 68.97, 66.67, 76.19, 66.67, 90.91, 100.0, 85.71, 0.0, 100.0, 74.0),
    ("251FA04E86", "DARAM RUPA SRINIDHI", 7.93, 7.96, 92.86, 86.21, 85.71, 89.66, 95.24, 95.24, 83.33, 100.0, 80.00, 80.95, 75.0, 66.67, 89.0),
    ("251FA04E89", "DESAVATH VENKATESWARA NAIK", 7.51, 7.66, 85.71, 79.31, 66.67, 79.31, 95.24, 100.0, 83.33, 72.73, 100.0, 85.71, 0.0, 100.0, 84.0),
    ("251FA04E92", "DHULUPALLA SIREESHA", 6.36, 6.22, 75.00, 62.07, 61.90, 62.07, 85.71, 95.24, 77.78, 72.73, 100.0, 66.67, 25.0, 66.67, 74.0),
    ("251FA04E94", "EDIGA VIJAY CHANDRA", 6.54, 6.55, 67.86, 68.97, 52.38, 62.07, 90.48, 80.95, 77.78, 72.73, 60.00, 76.19, 0.0, 66.67, 70.0),
    ("251FA04E96", "ESHANA RAI", 7.98, 8.08, 71.43, 68.97, 47.62, 79.31, 76.19, 80.95, 66.67, 45.45, 100.0, 76.19, 25.0, 100.0, 72.0),
    ("251FA04F05", "GANGAVARAM CHIRUDEEP", 7.35, 7.08, 75.00, 72.41, 57.14, 75.86, 85.71, 80.95, 83.33, 72.73, 100.0, 85.71, 0.0, 66.67, 77.0),
    ("251FA04F06", "GANGIREDDY MANUSREE", 8.35, 8.49, 96.43, 89.66, 80.95, 89.66, 95.24, 95.24, 83.33, 81.82, 100.0, 90.48, 50.0, 100.0, 90.0),
    ("251FA04F08", "GANITHI SREE YAMINI", 7.91, 7.79, 92.86, 86.21, 100.0, 89.66, 90.48, 83.33, 83.33, 100.0, 80.00, 100.0, 100.0, 100.0, 93.0),
    ("251FA04F15", "GODA POOJITH", 8.01, 7.92, 92.86, 86.21, 95.24, 89.66, 95.24, 100.0, 83.33, 100.0, 80.00, 90.48, 75.0, 66.67, 91.0),
    ("251FA04F20", "GOLLA YOGANANDU", 7.40, 7.55, 85.71, 72.41, 66.67, 82.76, 95.24, 95.24, 83.33, 72.73, 100.0, 85.71, 0.0, 100.0, 83.0),
    ("251FA04F21", "GONE HARISHA", 8.18, 8.53, 96.43, 82.76, 95.24, 93.10, 85.71, 90.48, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 91.0),
    ("251FA04F25", "GOSU NAGAKOWSHIK", 7.48, 7.46, 85.71, 79.31, 61.90, 79.31, 95.24, 100.0, 83.33, 72.73, 100.0, 76.19, 0.0, 100.0, 82.0),
    ("251FA04F26", "GOTTAM VARSHITHA", 8.20, 8.59, 92.86, 86.21, 80.95, 89.66, 90.48, 90.48, 83.33, 100.0, 80.00, 80.95, 75.0, 66.67, 87.0),
    ("251FA04F34", "GUNJA CHANDU", 8.10, 7.75, 96.43, 82.76, 90.48, 93.10, 80.95, 90.48, 83.33, 100.0, 80.00, 90.48, 75.0, 100.0, 89.0),
    ("251FA04F38", "GUDIPATI MANASA", 8.35, 8.49, 96.43, 89.66, 80.95, 93.10, 90.48, 95.24, 83.33, 100.0, 100.0, 90.48, 75.0, 100.0, 92.0),
    ("251FA04F40", "HEMASRI ANNAPAREDDY", 8.11, 7.99, 96.43, 93.10, 90.48, 100.0, 95.24, 90.48, 83.33, 100.0, 100.0, 90.48, 100.0, 66.67, 95.0),
    ("251FA04F43", "IRUVURI GOKUL MANIDEEP", 7.12, 7.23, 67.86, 58.62, 47.62, 65.52, 71.43, 80.95, 44.44, 72.73, 80.00, 57.14, 50.0, 66.67, 64.0),
    ("251FA04F45", "JAMPANI VENKATA LOKESH REDDY", 6.88, 6.97, 78.57, 82.76, 71.43, 93.10, 90.48, 100.0, 83.33, 100.0, 80.00, 80.95, 75.0, 100.0, 86.0),
    ("251FA04F90", "KISHAN KUMAR", 8.36, 8.04, 92.86, 75.86, 76.19, 96.55, 80.95, 90.48, 83.33, 100.0, 100.0, 90.48, 50.0, 100.0, 88.0),
    ("251FA04G37", "MANUKONDA CHARISHMA SIVANI", 7.54, 7.57, 100.0, 100.0, 90.48, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0),
    ("251FA04G38", "MANVI MANOGNA", 8.31, 8.24, 85.71, 89.66, 95.24, 93.10, 90.48, 100.0, 77.78, 100.0, 100.0, 90.48, 75.0, 100.0, 92.0),
]

COURSES = [
    ("CS201", "Data Structures", "PCC", 3, "THEORY", "Dr. Meera Iyer", "meera@vignan.ac.in"),
    ("CS202", "Database Management Systems & Information Systems", "PCC", 3, "THEORY", "Dr. K. V. Krishna Kishore", "kkishore@vignan.ac.in"),
    ("CS203", "Object Oriented Programming Through Java", "PCC", 3, "THEORY", "Prof. P. Subbarao", "subbarao@vignan.ac.in"),
    ("EC204", "Digital Logic Design & Embedded Systems", "ESC", 3, "THEORY", "Dr. T. Pitchaiah", "pitchaiah@vignan.ac.in"),
    ("AI205", "Artificial Intelligence", "PCC", 3, "THEORY", "Dr. S. Venkateswarlu", "venkat@vignan.ac.in"),
    ("MA206", "Discrete Mathematical Structures", "BSC", 3, "THEORY", "Dr. P. L. N. Varma", "varma@vignan.ac.in"),
    ("CS201L", "Data Structures Lab", "PCC", 1.5, "PRACTICAL", "Dr. Meera Iyer", "meera@vignan.ac.in"),
    ("CS202L", "DBMS & IS Lab", "PCC", 1.5, "PRACTICAL", "Dr. K. V. Krishna Kishore", "kkishore@vignan.ac.in"),
    ("CS203L", "OOP Through Java Lab", "PCC", 1.5, "PRACTICAL", "Prof. P. Subbarao", "subbarao@vignan.ac.in"),
    ("CS208", "Data Wrangling and Visualization", "PCC", 2, "THEORY_CUM_PRACTICAL", "Dr. N. Veeranjaneyulu", "veeru@vignan.ac.in"),
]

def build_sqlite_database(db_path: str):
    print(f"Building SQLite database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS institution (
        institution_id TEXT PRIMARY KEY,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        type TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS department (
        department_id TEXT PRIMARY KEY,
        institution_id TEXT REFERENCES institution(institution_id),
        code TEXT NOT NULL,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS academic_year (
        academic_year_id TEXT PRIMARY KEY,
        institution_id TEXT REFERENCES institution(institution_id),
        label TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        is_current INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS term (
        term_id TEXT PRIMARY KEY,
        academic_year_id TEXT REFERENCES academic_year(academic_year_id),
        term_no INTEGER,
        label TEXT NOT NULL,
        parity TEXT,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS programme (
        programme_id TEXT PRIMARY KEY,
        institution_id TEXT,
        department_id TEXT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        level TEXT,
        degree TEXT,
        duration_years INTEGER
    );

    CREATE TABLE IF NOT EXISTS batch (
        batch_id TEXT PRIMARY KEY,
        programme_id TEXT,
        admission_year INTEGER,
        label TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS section (
        section_id TEXT PRIMARY KEY,
        batch_id TEXT,
        code TEXT NOT NULL,
        year_of_study INTEGER,
        strength INTEGER
    );

    CREATE TABLE IF NOT EXISTS course (
        course_id TEXT PRIMARY KEY,
        course_code TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        course_category TEXT,
        credits REAL,
        course_type TEXT,
        faculty_name TEXT,
        faculty_email TEXT
    );

    CREATE TABLE IF NOT EXISTS student (
        student_id TEXT PRIMARY KEY,
        roll_no TEXT NOT NULL UNIQUE,
        password TEXT DEFAULT '',
        admission_no TEXT,
        full_name TEXT NOT NULL,
        gender TEXT,
        email TEXT NOT NULL,
        department_code TEXT DEFAULT 'CSE',
        programme_code TEXT DEFAULT 'BTCSE',
        batch_label TEXT DEFAULT '2024-28 CSE',
        section_code TEXT DEFAULT '7',
        year_of_study INTEGER DEFAULT 2,
        semester INTEGER DEFAULT 3,
        sgpa_prev REAL,
        cgpa REAL,
        total_attendance_pct REAL,
        risk_level TEXT,
        backlog_count INTEGER DEFAULT 0,
        fee_outstanding REAL DEFAULT 0.0,
        mentor_name TEXT DEFAULT 'Dr. Radhika Sharma (Assoc. Prof, CSE)',
        status TEXT DEFAULT 'ACTIVE'
    );

    CREATE TABLE IF NOT EXISTS attendance_summary (
        summary_id TEXT PRIMARY KEY,
        student_id TEXT REFERENCES student(student_id),
        course_code TEXT REFERENCES course(course_code),
        course_title TEXT,
        faculty_name TEXT,
        attendance_pct REAL,
        classes_held INTEGER,
        classes_attended INTEGER,
        risk_level TEXT,
        classes_needed INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS internal_mark (
        mark_id TEXT PRIMARY KEY,
        student_id TEXT REFERENCES student(student_id),
        course_code TEXT,
        assessment_name TEXT,
        max_marks REAL,
        marks_obtained REAL,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS fee_demand (
        demand_id TEXT PRIMARY KEY,
        student_id TEXT REFERENCES student(student_id),
        fee_head TEXT,
        amount_demanded REAL,
        amount_paid REAL,
        due_date TEXT,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS institutional_policy (
        policy_id TEXT PRIMARY KEY,
        code TEXT UNIQUE,
        title TEXT NOT NULL,
        clause TEXT NOT NULL,
        effective_date TEXT,
        summary TEXT
    );

    CREATE TABLE IF NOT EXISTS circular (
        circular_id TEXT PRIMARY KEY,
        circular_no TEXT UNIQUE,
        title TEXT NOT NULL,
        issued_date TEXT,
        category TEXT,
        summary TEXT
    );

    CREATE TABLE IF NOT EXISTS service_request (
        request_id TEXT PRIMARY KEY,
        request_no TEXT UNIQUE,
        student_id TEXT REFERENCES student(student_id),
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS agent_registry (
        agent_id TEXT PRIMARY KEY,
        agent_no INTEGER,
        code TEXT UNIQUE,
        name TEXT,
        domain TEXT,
        scope_statement TEXT
    );
    """)

    inst_id = "11111111-1111-1111-1111-111111111111"
    dept_id = "22222222-2222-2222-2222-222222222222"
    ay_id   = "33333333-3333-3333-3333-333333333333"
    term_id = "44444444-4444-4444-4444-444444444444"
    prog_id = "55555555-5555-5555-5555-555555555555"
    batch_id= "77777777-7777-7777-7777-777777777777"
    sec_id  = "88888888-8888-8888-8888-888888888888"

    cur.execute("INSERT INTO institution VALUES (?, ?, ?, ?)",
                (inst_id, "VFSTR", "Vignan Foundation for Science, Technology and Research", "DEEMED_UNIVERSITY"))
    cur.execute("INSERT INTO department VALUES (?, ?, ?, ?)",
                (dept_id, inst_id, "CSE", "Computer Science and Engineering"))
    cur.execute("INSERT INTO academic_year VALUES (?, ?, ?, ?, ?, ?)",
                (ay_id, inst_id, "2025-26", "2025-07-01", "2026-06-30", 1))
    cur.execute("INSERT INTO term VALUES (?, ?, ?, ?, ?, ?)",
                (term_id, ay_id, 3, "ODD 2025-26 (Sem 3)", "ODD", "ACTIVE"))
    cur.execute("INSERT INTO programme VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (prog_id, inst_id, dept_id, "BTCSE", "B.Tech Computer Science and Engineering", "UG", "B.Tech", 4))
    cur.execute("INSERT INTO batch VALUES (?, ?, ?, ?)",
                (batch_id, prog_id, 2024, "2024-28 CSE"))
    cur.execute("INSERT INTO section VALUES (?, ?, ?, ?, ?)",
                (sec_id, batch_id, "7", 2, 70))

    # Insert Courses
    for c in COURSES:
        cid = f"course-{c[0].lower()}"
        cur.execute("INSERT INTO course VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (cid, c[0], c[1], c[2], c[3], c[4], c[5], c[6]))

    # Insert 70 Students
    for idx, s in enumerate(STUDENTS_DATA):
        regd, name, sgpa, cgpa = s[0], s[1], s[2], s[3]
        tot_att = s[16]
        stu_id = f"stu-{regd.lower()}"
        email = f"{regd.lower()}@vignan.ac.in"
        gender = "F" if any(w in name.upper() for w in ["SRI", "PRIYA", "LAKSHMI", "MONIKA", "DEEPTHI", "SATHVIKA", "LAVANYA", "MANASA", "VARSHITHA", "SIVANI", "MANOGNA", "AMULYA", "AKHILA", "HARINI", "SIRISHA", "PRASANNA", "DEEKSHITHA", "MANUSREE", "YAMINI", "HARISHA", "RAI", "VARSHINI", "SURYADEVARA"]) else "M"
        
        # Determine risk level
        if tot_att < 65.0:
            risk = "CRITICAL_DETAINED_DANGER"
        elif tot_att < 75.0:
            risk = "AT_RISK_SHORTFALL"
        else:
            risk = "NORMAL_ELIGIBLE"

        backlogs = 2 if sgpa == 0.0 else (1 if cgpa < 6.5 else 0)
        fee_due = 45000.0 if tot_att < 65.0 else (12500.0 if idx % 4 == 0 else 0.0)

        cur.execute("""
        INSERT INTO student VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stu_id, regd, regd, f"ADM2024{idx+1:03d}", name, gender, email,
            "CSE", "BTCSE", "2024-28 CSE", "7", 2, 3,
            sgpa, cgpa, tot_att, risk, backlogs, fee_due,
            "Dr. Radhika Sharma (Assoc. Prof, CSE, Cabin C-402)", "ACTIVE"
        ))

        # Subject-wise attendance mapping
        sub_atts = [
            ("CS201", s[4]),
            ("CS202", s[5]),
            ("CS203", s[6]),
            ("EC204", s[7]),
            ("AI205", s[8]),
            ("MA206", s[9]),
            ("CS201L", s[10]),
            ("CS202L", s[11]),
            ("CS203L", s[12]),
            ("CS208", s[13]),
        ]

        for code, pct in sub_atts:
            sum_id = f"att-{regd.lower()}-{code.lower()}"
            held = 40 if "L" not in code else 20
            att_cnt = int(round((pct / 100.0) * held))
            c_risk = "CRITICAL" if pct < 65.0 else ("AT_RISK" if pct < 75.0 else "NONE")
            
            # calculate classes needed for 75%
            needed = 0
            if pct < 75.0:
                needed = max(0, int(round((0.75 * held - att_cnt) / 0.25)))

            course_title = next(c[1] for c in COURSES if c[0] == code)
            faculty = next(c[5] for c in COURSES if c[0] == code)

            cur.execute("""
            INSERT INTO attendance_summary VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sum_id, stu_id, code, course_title, faculty, pct, held, att_cnt, c_risk, needed))

        # Generate realistic internal marks for Mid-1
        for code, _ in sub_atts[:6]:
            base_pct = (cgpa / 10.0) if cgpa > 0 else 0.5
            marks_obt = round(min(30.0, max(12.0, base_pct * 30 + (idx % 5 - 2))), 1)
            cur.execute("""
            INSERT INTO internal_mark VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f"mark-{regd.lower()}-{code.lower()}", stu_id, code, "Mid Term 1 (Descriptive)", 30.0, marks_obt, "EVALUATED"))

        # Fee demand
        cur.execute("""
        INSERT INTO fee_demand VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (f"fee-{regd.lower()}", stu_id, "Tuition & Development Fee (Sem 3)", 100000.0, 100000.0 - fee_due, "2026-10-15", "PAID" if fee_due == 0 else "PARTIAL"))

    # Policies
    POLICIES = [
        ("POL-ATT-2024", "VFSTR Academic Regulations: Attendance Norms", "Clause 4.1 to 4.4", "2024-07-01",
         "A student must secure minimum 75% overall attendance and 75% in each course. Condonation for medical reasons is permitted between 65% and 74.9% with Dean approval and fee of Rs. 1,000. Students below 65% are strictly detained and must repeat the semester."),
        ("POL-EXAM-2023", "Continuous Internal Evaluation (CIE) & Semester End Examinations (SEE)", "Clause 7.2", "2023-08-01",
         "CIE carries 40% weightage comprising two Mid-Term tests, quizzes, and assignments. SEE carries 60% weightage. Minimum passing marks in SEE is 40%, and overall aggregate minimum is 45%."),
        ("POL-FEE-2024", "Tuition Fee Payment Schedule & Late Penalty Policy", "Clause 3.1", "2024-06-15",
         "Semester tuition fees must be cleared before commencement of instructions. A grace period of 15 days is permitted, after which a late fine of Rs. 100 per day applies up to 30 days."),
        ("POL-GRIEV-2024", "Student Grievance Redressal and Anti-Ragging Regulation", "Clause 2.1", "2024-07-01",
         "VFSTR enforces zero-tolerance towards ragging or harassment. Grievances can be submitted anonymously or directly to the Proctorial Board with SLA resolution within 5 working days.")
    ]
    for p in POLICIES:
        cur.execute("INSERT INTO institutional_policy VALUES (?, ?, ?, ?, ?, ?)", (f"pol-{p[0].lower()}", p[0], p[1], p[2], p[3], p[4]))

    # Circulars
    CIRCULARS = [
        ("CIR-2026-088", "Mid-Term Examination Schedule - II B.Tech ODD Semester", "2026-09-05", "ACADEMIC",
         "Mid-Term 1 examinations for II B.Tech Section 7 commence from 22nd September 2026. Hall tickets will be issued only to students with >= 75% attendance."),
        ("CIR-2026-092", "Provisional Attendance Shortfall Warning List (Section 7)", "2026-09-08", "ATTENDANCE",
         "Students with aggregate attendance below 75% as of 1st September 2026 are instructed to meet their class counselor and HOD immediately to submit condonation certificates."),
        ("CIR-2026-095", "On-Duty (OD) Sanction for Smart India Hackathon & Paper Presentations", "2026-09-02", "STUDENT_AFFAIRS",
         "Students participating in authorized national hackathons and technical symposiums are granted On-Duty (OD) attendance credit upon submission of participation proof within 3 days.")
    ]
    for c in CIRCULARS:
        cur.execute("INSERT INTO circular VALUES (?, ?, ?, ?, ?, ?)", (f"cir-{c[0].lower()}", c[0], c[1], c[2], c[3], c[4]))

    # Service requests
    cur.execute("INSERT INTO service_request VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("sr-1", "SR-2026-0001", "stu-251fa04e03", "BONAFIDE_CERTIFICATE", "Bonafide Certificate for National Scholarship Portal", "RESOLVED", "2026-09-02"))
    cur.execute("INSERT INTO service_request VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("sr-2", "SR-2026-0002", "stu-251fa04e21", "FEE_ESTIMATE", "Fee Estimate Letter for Bank Education Loan", "READY_FOR_COLLECTION", "2026-09-04"))
    cur.execute("INSERT INTO service_request VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("sr-3", "SR-2026-0003", "stu-251fa04131", "COUNSELING_APPOINTMENT", "Urgent Attendance Shortfall Counseling with Class Mentor", "IN_PROGRESS", "2026-09-07"))

    # AgentOps Registry
    AGENTS = [
        ("VIGBOT_HELPDESK", 65, "VIGBOT Agent", "STUDENT_SUPPORT", "Conversational interface for students into academic, attendance, fees, and services."),
        ("A11_ATTENDANCE_ANALYSIS", 11, "Attendance Analysis Agent", "ATTENDANCE", "Computes course and overall attendance, projected trajectory, and detects shortfall risk."),
        ("A08_COURSE_OUTCOME", 8, "Course Outcome Attainment Agent", "OUTCOMES", "Calculates NBA direct CO/PO attainment levels from question-level marks."),
        ("A44_STUDENT_PROFILE", 44, "Student Profile Agent", "IDENTITY", "Federated student demographic, enrollment, and academic standing repository."),
        ("A46_SERVICE_REQUEST", 46, "Student Services & Ticketing Agent", "SERVICE", "Manages bonafide certificates, transcripts, bus passes, and administrative requests."),
        ("A66_COUNSELING_WELLBEING", 66, "Student Wellbeing & Crisis Counselor", "WELLBEING", "Emergency crisis intervention, mental wellbeing helpline, and proctorial counseling.")
    ]
    for a in AGENTS:
        cur.execute("INSERT INTO agent_registry VALUES (?, ?, ?, ?, ?, ?)",
                    (f"agent-{a[1]}", a[1], a[0], a[2], a[3], a[4]))

    conn.commit()
    conn.close()
    print(f"SQLite database created successfully with 70 students, {len(COURSES)} courses, and 700 attendance records!")


def build_postgres_sql_seed(output_sql_path: str):
    print(f"Generating PostgreSQL Showcase Seed script at: {output_sql_path}")
    os.makedirs(os.path.dirname(output_sql_path), exist_ok=True)
    lines = []
    lines.append("-- =====================================================================")
    lines.append("-- 99_showcase_seed.sql")
    lines.append("-- University: Vignan Foundation for Science, Technology and Research (VFSTR)")
    lines.append("-- Department: Computer Science & Engineering (CSE)")
    lines.append("-- Batch: 2024-28 (Second Year, Section 7, ODD 2025-26)")
    lines.append("-- 70 Authentic Students with real SGPA, CGPA, and Course-Wise Attendance")
    lines.append("-- =====================================================================")
    lines.append("SET search_path = public;")
    lines.append("")

    lines.append("-- 1. Institution, Department, Academic Year, Term")
    lines.append("INSERT INTO core.institution (institution_id, code, name, type)")
    lines.append("VALUES ('11111111-1111-1111-1111-111111111111','VFSTR','Vignan Foundation for Science, Technology and Research','DEEMED_UNIVERSITY')")
    lines.append("ON CONFLICT (code) DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO core.department (department_id, institution_id, code, name)")
    lines.append("VALUES ('22222222-2222-2222-2222-222222222222','11111111-1111-1111-1111-111111111111','CSE','Computer Science and Engineering')")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO core.academic_year (academic_year_id, institution_id, label, start_date, end_date, is_current)")
    lines.append("VALUES ('33333333-3333-3333-3333-333333333333','11111111-1111-1111-1111-111111111111','2025-26','2025-07-01','2026-06-30',true)")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO core.term (term_id, academic_year_id, term_no, label, parity, start_date, end_date, status)")
    lines.append("VALUES ('44444444-4444-4444-4444-444444444444','33333333-3333-3333-3333-333333333333',3,'ODD 2025-26 (Sem 3)','ODD','2025-07-15','2025-12-15','ACTIVE')")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")

    lines.append("-- 2. Programme, Regulation, Batch, Section")
    lines.append("INSERT INTO curriculum.programme (programme_id, institution_id, department_id, code, name, level, degree, duration_years, total_terms, sanctioned_intake)")
    lines.append("VALUES ('55555555-5555-5555-5555-555555555555','11111111-1111-1111-1111-111111111111','22222222-2222-2222-2222-222222222222','BTCSE','B.Tech Computer Science and Engineering','UG','B.Tech',4,8,420)")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO curriculum.regulation (regulation_id, institution_id, code, name, effective_from_admission_year, status)")
    lines.append("VALUES ('66666666-6666-6666-6666-666666666666','11111111-1111-1111-1111-111111111111','R23','Regulation 2023',2023,'ACTIVE')")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO curriculum.batch (batch_id, programme_id, regulation_id, admission_year, label)")
    lines.append("VALUES ('77777777-7777-7777-7777-777777777777','55555555-5555-5555-5555-555555555555','66666666-6666-6666-6666-666666666666',2024,'2024-28 CSE')")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")
    lines.append("INSERT INTO curriculum.section (section_id, batch_id, code, year_of_study, strength)")
    lines.append("VALUES ('88888888-8888-8888-8888-888888888888','77777777-7777-7777-7777-777777777777','7',2,70)")
    lines.append("ON CONFLICT DO NOTHING;")
    lines.append("")

    lines.append("-- 3. Courses & Versions")
    for idx, c in enumerate(COURSES):
        cid = f"aaaaaaaa-0000-0000-0000-{idx+1:012d}"
        cvid= f"bbbbbbbb-0000-0000-0000-{idx+1:012d}"
        lines.append(f"INSERT INTO curriculum.course (course_id, institution_id, owning_department_id, title)")
        lines.append(f"VALUES ('{cid}','11111111-1111-1111-1111-111111111111','22222222-2222-2222-2222-222222222222','{c[1]}') ON CONFLICT DO NOTHING;")
        lines.append(f"INSERT INTO curriculum.course_version (course_version_id, course_id, regulation_id, programme_id, course_code, term_no, year_of_study, course_category, course_type, credits, lecture_hours, tutorial_hours, practical_hours)")
        lines.append(f"VALUES ('{cvid}','{cid}','66666666-6666-6666-6666-666666666666','55555555-5555-5555-5555-555555555555','{c[0]}',3,2,'{c[2]}','{c[4]}',{c[3]},3,1,0) ON CONFLICT DO NOTHING;")
    lines.append("")

    lines.append("-- 4. VFSTR Section 7 Students & Credentials")
    for idx, s in enumerate(STUDENTS_DATA):
        regd, name = s[0], s[1]
        pid = f"cccccccc-0000-0000-0000-{idx+1:012d}"
        sid = f"dddddddd-0000-0000-0000-{idx+1:012d}"
        uid = f"eeeeeeee-0000-0000-0000-{idx+1:012d}"
        email = f"{regd.lower()}@vignan.ac.in"
        gender = "F" if any(w in name.upper() for w in ["SRI", "PRIYA", "LAKSHMI", "MONIKA", "DEEPTHI", "SATHVIKA", "LAVANYA", "MANASA", "VARSHITHA", "SIVANI", "MANOGNA", "AMULYA", "AKHILA", "HARINI", "SIRISHA", "PRASANNA", "DEEKSHITHA", "MANUSREE", "YAMINI", "HARISHA", "RAI", "VARSHINI", "SURYADEVARA"]) else "M"
        
        lines.append(f"INSERT INTO people.person (person_id, institution_id, full_name, gender) VALUES ('{pid}','11111111-1111-1111-1111-111111111111','{name}','{gender}') ON CONFLICT DO NOTHING;")
        lines.append(f"INSERT INTO people.student (student_id, person_id, admission_no, roll_no, batch_id, admission_date, current_section_id, current_year_of_study) VALUES ('{sid}','{pid}','ADM2024{idx+1:03d}','{regd}','77777777-7777-7777-7777-777777777777','2024-08-01','88888888-8888-8888-8888-888888888888',2) ON CONFLICT DO NOTHING;")
        lines.append(f"INSERT INTO identity.app_user (user_id, person_id, username, email) VALUES ('{uid}','{pid}','{regd.lower()}','{email}') ON CONFLICT DO NOTHING;")

    lines.append("")
    lines.append("-- 5. Helpdesk Policies & Knowledge")
    lines.append("INSERT INTO governance.policy_document (policy_id, institution_id, policy_number, title, category, effective_date, status, summary)")
    lines.append("VALUES ('ffffffff-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111','POL-ATT-2024','VFSTR Academic Regulations: Attendance Norms','ACADEMIC','2024-07-01','APPROVED','75% attendance mandatory. Condonation permitted between 65-74.9% on medical grounds with fee of Rs. 1000. Under 65% detained.') ON CONFLICT DO NOTHING;")
    lines.append("INSERT INTO governance.circular (circular_id, institution_id, circular_number, title, issued_date, category, status, summary)")
    lines.append("VALUES ('ffffffff-0000-0000-0000-000000000002','11111111-1111-1111-1111-111111111111','CIR-2026-088','Mid-Term 1 Examination Schedule - II B.Tech Sec 7','2026-09-05','EXAMINATION','ACTIVE','Mid-Term 1 examinations commence from 22nd September 2026. Hall tickets conditional on >= 75% attendance.') ON CONFLICT DO NOTHING;")

    with open(output_sql_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated 99_showcase_seed.sql successfully with {len(STUDENTS_DATA)} students!")

if __name__ == "__main__":
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))
    sql_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "source", "99_showcase_seed.sql"))
    build_sqlite_database(db_file)
    build_postgres_sql_seed(sql_file)
