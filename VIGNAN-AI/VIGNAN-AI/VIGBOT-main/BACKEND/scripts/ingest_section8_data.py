"""
Ingest Section 8 Data for VFSTR B.Tech CSE II-I (Room N-313)
Official attendance report (10-07-2026 to 10-09-2026) & Section 8 Timetable
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import sqlite3
import math

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))

# 69 Authenticated Students of VFSTR CSE Section 8 (Room N-313, Class Teacher: Dr. T.R. Rajesh)
# Format: (RegdNo, Name, Att_DS, Att_DBMSIS, Att_OOPTJ, Att_DLDES, Att_AI, Att_DMS, Att_DSL, Att_DBMSL, Att_OOPTJL, Att_DWAV, Att_Lib, Att_Coun, Total_Att)
SECTION_8_STUDENTS = [
    # Page 1
    ("251FA04035", "AASIM ALI", 69.70, 68.42, 65.00, 72.22, 74.29, 77.78, 68.42, 65.00, 72.73, 68.00, 0.00, 62.50, 70.0),
    ("251FA04047", "GOLLA RATAN SURYA", 51.52, 52.63, 40.00, 61.11, 57.14, 44.44, 42.11, 40.00, 68.18, 76.00, 0.00, 62.50, 54.0),
    ("251FA04104", "DIPESH KUMAR", 75.76, 73.68, 70.00, 75.00, 71.43, 77.78, 78.95, 85.00, 86.36, 84.00, 0.00, 100.00, 77.0),
    ("251FA04139", "ZOGBEDJI LEWLESSE BENI", 93.94, 94.74, 95.00, 94.44, 85.71, 96.30, 94.74, 100.00, 90.91, 100.00, 100.00, 87.50, 95.0),
    ("251FA04D19", "VEGESANA LAKSHMI SOUSEELYA", 57.58, 63.16, 55.00, 77.78, 68.57, 74.07, 57.89, 85.00, 59.09, 72.00, 0.00, 87.50, 68.0),
    ("251FA04F46", "JASHTI LAKSHMI ASHWATH CHOWDARY", 78.79, 57.89, 65.00, 72.22, 80.00, 85.19, 63.16, 85.00, 72.73, 68.00, 66.67, 100.00, 74.0),
    ("251FA04F47", "JASTI SIVA KRISHNA", 69.70, 76.32, 75.00, 83.33, 88.57, 70.37, 84.21, 65.00, 95.45, 72.00, 33.33, 87.50, 78.0),
    ("251FA04F53", "KADAVAKUDURU JAGADEESH", 63.64, 65.79, 65.00, 77.78, 68.57, 74.07, 94.74, 55.00, 68.18, 80.00, 66.67, 100.00, 72.0),
    ("251FA04F55", "KADIYALA DIVIJA", 90.91, 84.21, 90.00, 94.44, 100.00, 96.30, 100.00, 85.00, 100.00, 80.00, 33.33, 75.00, 91.0),
    ("251FA04F56", "KALE SUDHEER", 78.79, 60.53, 75.00, 55.56, 62.86, 74.07, 52.63, 65.00, 81.82, 76.00, 33.33, 62.50, 68.0),
    ("251FA04F57", "KALLI JOSHNA", 75.76, 73.68, 70.00, 77.78, 85.71, 92.59, 84.21, 70.00, 86.36, 76.00, 0.00, 87.50, 79.0),
    ("251FA04F58", "KALLI THANISH KUMAR REDDY", 54.55, 63.16, 70.00, 63.89, 77.14, 81.48, 78.95, 35.00, 81.82, 68.00, 33.33, 37.50, 67.0),
    ("251FA04F65", "KANALA DHAKSHAYANI", 84.85, 76.32, 80.00, 83.33, 85.71, 88.89, 89.47, 75.00, 100.00, 72.00, 33.33, 62.50, 83.0),
    ("251FA04F66", "KANCHARLA THANDAVA KRISHNA SAI RAM GOUD", 45.45, 63.16, 50.00, 55.56, 57.14, 51.85, 73.68, 70.00, 95.45, 72.00, 0.00, 75.00, 62.0),

    # Page 2
    ("251FA04F69", "KANDUKURI VINAY KUMAR", 81.82, 89.47, 95.00, 91.67, 88.57, 92.59, 89.47, 85.00, 100.00, 88.00, 100.00, 100.00, 91.0),
    ("251FA04F70", "KANDUKURU SAI SAKETH", 57.58, 63.16, 60.00, 77.78, 71.43, 77.78, 84.21, 45.00, 81.82, 72.00, 0.00, 75.00, 69.0),
    ("251FA04F72", "KANHAIYA KUMAR", 87.88, 89.47, 85.00, 91.67, 97.14, 100.00, 94.74, 85.00, 86.36, 84.00, 0.00, 100.00, 90.0),
    ("251FA04F77", "KARI RAMYA SRI", 69.70, 73.68, 75.00, 83.33, 82.86, 96.30, 94.74, 70.00, 68.18, 80.00, 0.00, 100.00, 80.0),
    ("251FA04F78", "KASA SHANMUKHA LAXMAN", 36.36, 63.16, 50.00, 58.33, 48.57, 44.44, 52.63, 10.00, 54.55, 72.00, 0.00, 62.50, 50.0),
    ("251FA04F81", "KATTE POGU MEGHANA", 87.88, 86.84, 85.00, 88.89, 97.14, 100.00, 100.00, 85.00, 86.36, 84.00, 0.00, 100.00, 90.0),
    ("251FA04F82", "KATTULA PUSHYA HASINI", 63.64, 55.26, 60.00, 72.22, 68.57, 70.37, 52.63, 60.00, 86.36, 52.00, 0.00, 50.00, 64.0),
    ("251FA04F83", "KATURI NANDA KISHORE", 93.94, 86.84, 80.00, 88.89, 97.14, 92.59, 94.74, 85.00, 100.00, 92.00, 33.33, 100.00, 91.0),
    ("251FA04F88", "KINTALI KARTHIK", 87.88, 76.32, 80.00, 86.11, 97.14, 85.19, 89.47, 85.00, 95.45, 92.00, 33.33, 100.00, 88.0),
    ("251FA04F91", "KODALI NISHITHA", 63.64, 76.32, 80.00, 72.22, 91.43, 88.89, 89.47, 65.00, 77.27, 76.00, 0.00, 87.50, 78.0),
    ("251FA04F92", "KOKKONDA SOHAN MAHI", 81.82, 81.58, 75.00, 86.11, 80.00, 85.19, 89.47, 85.00, 100.00, 88.00, 33.33, 100.00, 85.0),
    ("251FA04G02", "KOPPARAPU VENKATA SANJANA", 84.85, 81.58, 85.00, 94.44, 97.14, 96.30, 100.00, 85.00, 86.36, 84.00, 0.00, 100.00, 89.0),
    ("251FA04G04", "KOTAGIRI HEMANJANI", 60.61, 65.79, 55.00, 66.67, 74.29, 74.07, 78.95, 65.00, 72.73, 60.00, 0.00, 87.50, 68.0),
    ("251FA04G05", "KOTHAMASU VISHALINI", 63.64, 60.53, 75.00, 86.11, 85.71, 85.19, 100.00, 85.00, 54.55, 60.00, 0.00, 87.50, 75.0),
    ("251FA04G06", "KOTHAPALLI SAI HARSHINI", 60.61, 60.53, 55.00, 72.22, 74.29, 77.78, 84.21, 60.00, 72.73, 52.00, 0.00, 75.00, 67.0),

    # Page 3
    ("251FA04G08", "KOVURI HARSHAVARDHAN PRASAD", 90.91, 86.84, 80.00, 97.22, 97.14, 92.59, 84.21, 90.00, 86.36, 92.00, 33.33, 87.50, 90.0),
    ("251FA04G11", "KUPPILI CHINANAGENDRA", 75.76, 84.21, 85.00, 83.33, 85.71, 85.19, 100.00, 85.00, 81.82, 84.00, 0.00, 100.00, 84.0),
    ("251FA04G15", "M YAMINI", 75.76, 78.95, 75.00, 80.56, 80.00, 85.19, 78.95, 85.00, 86.36, 92.00, 0.00, 87.50, 81.0),
    ("251FA04G16", "MACHAVARAPU DEVISREE", 90.91, 92.11, 90.00, 86.11, 100.00, 96.30, 84.21, 70.00, 100.00, 76.00, 33.33, 87.50, 89.0),
    ("251FA04G27", "MALLAREDDY VENKATA SAI LOKESH", 93.94, 84.21, 80.00, 91.67, 85.71, 92.59, 100.00, 85.00, 100.00, 100.00, 33.33, 50.00, 90.0),
    ("251FA04G44", "MD ARMAN ALAM", 96.97, 94.74, 90.00, 100.00, 100.00, 96.30, 100.00, 100.00, 86.36, 100.00, 33.33, 100.00, 97.0),
    ("251FA04G47", "MEESALA SANDEEP", 54.55, 65.79, 70.00, 72.22, 74.29, 55.56, 57.89, 45.00, 54.55, 84.00, 33.33, 62.50, 64.0),
    ("251FA04G48", "MEKALA SRI VYSHNAVI", 84.85, 81.58, 85.00, 91.67, 88.57, 100.00, 100.00, 85.00, 86.36, 80.00, 0.00, 100.00, 88.0),
    ("251FA04G51", "MERIGALA ANUSREE", 100.00, 97.37, 100.00, 97.22, 97.14, 100.00, 100.00, 100.00, 100.00, 96.00, 100.00, 100.00, 99.0),
    ("251FA04G66", "NANCY KUMARI", 69.70, 71.05, 65.00, 72.22, 71.43, 77.78, 78.95, 85.00, 86.36, 84.00, 0.00, 87.50, 75.0),
    ("251FA04G69", "NARSHINGU MANI VENKATA ESHWAR", 90.91, 73.68, 85.00, 88.89, 88.57, 96.30, 94.74, 85.00, 86.36, 88.00, 33.33, 62.50, 87.0),
    ("251FA04G70", "NEELI ROHITHA", 93.94, 94.74, 90.00, 88.89, 88.57, 88.89, 84.21, 100.00, 100.00, 92.00, 100.00, 87.50, 92.0),
    ("251FA04G73", "OGGU MOUNISHA SAI SARANYA", 69.70, 63.16, 75.00, 80.56, 82.86, 70.37, 84.21, 70.00, 86.36, 60.00, 0.00, 87.50, 74.0),
    ("251FA04G75", "OOTLA RAJESH", 84.85, 76.32, 75.00, 88.89, 94.29, 77.78, 100.00, 85.00, 95.45, 92.00, 33.33, 100.00, 87.0),
    ("251FA04G77", "PADARTHI ASRITHA", 81.82, 92.11, 85.00, 88.89, 97.14, 92.59, 100.00, 80.00, 86.36, 76.00, 33.33, 75.00, 88.0),
    ("251FA04G80", "PALADUGU CHAITANYA SHANMUK SAI", 54.55, 50.00, 65.00, 80.56, 74.29, 66.67, 78.95, 70.00, 100.00, 64.00, 33.33, 75.00, 69.0),

    # Page 4
    ("251FA04G84", "PALUVADI BINDU MEGHANA", 75.76, 92.11, 75.00, 86.11, 88.57, 85.19, 94.74, 85.00, 77.27, 88.00, 0.00, 75.00, 84.0),
    ("251FA04G88", "PAPOLU RITHWIK", 90.91, 89.47, 90.00, 91.67, 94.29, 92.59, 100.00, 85.00, 100.00, 92.00, 33.33, 100.00, 92.0),
    ("251FA04G91", "PARUCHURI BHANUCHANDRA", 84.85, 89.47, 85.00, 94.44, 94.29, 92.59, 100.00, 85.00, 95.45, 92.00, 33.33, 100.00, 91.0),
    ("251FA04G92", "PASALA KEERTHI", 78.79, 92.11, 75.00, 86.11, 94.29, 92.59, 100.00, 85.00, 81.82, 80.00, 33.33, 100.00, 87.0),
    ("251FA04G93", "PASUMARTHI PUJITHNAGASAI", 81.82, 76.32, 65.00, 77.78, 80.00, 77.78, 68.42, 65.00, 68.18, 84.00, 0.00, 75.00, 75.0),
    ("251FA04H01", "PERAM SIDDARDHA REDDY", 69.70, 65.79, 70.00, 77.78, 88.57, 88.89, 94.74, 85.00, 86.36, 84.00, 0.00, 87.50, 80.0),
    ("251FA04H07", "PONNAM VYSHALI", 87.88, 89.47, 70.00, 86.11, 88.57, 88.89, 94.74, 85.00, 100.00, 84.00, 33.33, 100.00, 88.0),
    ("251FA04H08", "POTHIREDDY NARENDRA REDDY", 78.79, 65.79, 60.00, 83.33, 91.43, 88.89, 89.47, 85.00, 100.00, 80.00, 0.00, 100.00, 82.0),
    ("251FA04H09", "POTHURAJU RAGA SUDHA", 81.82, 84.21, 85.00, 94.44, 97.14, 100.00, 100.00, 85.00, 86.36, 80.00, 0.00, 100.00, 89.0),
    ("251FA04H20", "PURNE SUNINDRA", 63.64, 60.53, 65.00, 72.22, 68.57, 88.89, 68.42, 70.00, 86.36, 52.00, 0.00, 62.50, 69.0),
    ("251FA04H23", "PYDI DOOMDI SRIRAJ SATHWIK GUPTHA", 100.00, 97.37, 90.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 99.0),
    ("251FA04H24", "RAHUL KUMAR YADAV", 93.94, 92.11, 90.00, 97.22, 100.00, 96.30, 94.74, 75.00, 100.00, 84.00, 33.33, 100.00, 93.0),
    ("251FA04H25", "RAMBALAPU SRIYAN SATYENDRA SIVARAM", 100.00, 97.37, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.0),
    ("251FA04H27", "RAPARLA AMRUTHA", 81.82, 92.11, 85.00, 88.89, 94.29, 85.19, 100.00, 85.00, 81.82, 80.00, 0.00, 100.00, 88.0),
    ("251FA04H28", "RAVI RAJ", 69.70, 63.16, 65.00, 77.78, 80.00, 81.48, 68.42, 55.00, 72.73, 68.00, 0.00, 87.50, 71.0),
    ("251FA04H29", "RAVI RAJ", 84.85, 81.58, 80.00, 91.67, 91.43, 96.30, 84.21, 85.00, 86.36, 92.00, 0.00, 100.00, 88.0),

    # Page 5
    ("251FA04H33", "REGATI GNANA PRADEEP REDDY", 84.85, 81.58, 75.00, 86.11, 97.14, 77.78, 94.74, 100.00, 95.45, 92.00, 33.33, 100.00, 88.0),
    ("251FA04H34", "REGATI RAVI TEJA REDDY", 84.85, 81.58, 85.00, 94.44, 94.29, 92.59, 94.74, 75.00, 86.36, 76.00, 0.00, 100.00, 87.0),
    ("251FA04H38", "ROHINI PAMULA", 93.94, 92.11, 85.00, 91.67, 94.29, 100.00, 100.00, 85.00, 100.00, 92.00, 33.33, 100.00, 94.0),
    ("251FA04H39", "RUDRABOINA KOWSHIK", 54.55, 55.26, 75.00, 69.44, 68.57, 74.07, 78.95, 45.00, 100.00, 68.00, 100.00, 87.50, 69.0),
    ("251FA04H40", "RUNKU DEEKSHITH", 84.85, 81.58, 80.00, 91.67, 91.43, 100.00, 100.00, 85.00, 86.36, 84.00, 0.00, 100.00, 88.0),
    ("251FA04H48", "SEEMAKURTHI DALI KOUSHIKA", 78.79, 71.05, 65.00, 80.56, 80.00, 92.59, 94.74, 85.00, 86.36, 84.00, 0.00, 100.00, 81.0),
    ("251FA04H61", "SHAIK MAHAJ", 60.61, 73.68, 75.00, 75.00, 85.71, 81.48, 89.47, 70.00, 68.18, 64.00, 33.33, 37.50, 73.0),
    ("251FA04I40", "VENKATA KARTHEEK PARISA", 78.79, 73.68, 65.00, 80.56, 80.00, 92.59, 78.95, 85.00, 100.00, 64.00, 33.33, 62.50, 79.0),
]

# Section 8 Subject metadata
SUBJECTS_CONFIG = [
    ("DS-25CS201", "Data Structures", "Dr. Satish Kumar Satti", 33),
    ("DBMS-25CS203", "Database Management System", "Dr. Md. Oqail Ahmad", 38),
    ("OOPS-25CS204", "Object Oriented Programming Through Java", "Dr. O. Bhaskar", 20),
    ("DLD-25CS205", "Digital Logic design", "Mr. Akula Gopi", 36),
    ("AI-24CS302", "Artificial Intelligence", "Dr. T.R. Rajesh", 35),
    ("DMS-25MT202", "Discrete Mathematical Structures", "Dr. Sannu Venkateswarlu", 27),
    ("DW-25CS202", "Data Wrangling and Visualization", "Vara Lakshmi", 25),
]

# Section 8 Timetable Slots
TIMETABLE_SLOTS_SEC8 = [
    # Monday
    ("Monday", "08:15 AM - 09:05 AM", "DLD-25CS205", "Digital Logic design [L]", "N-314A", "Mr. Akula Gopi", "Lecture"),
    ("Monday", "09:05 AM - 09:55 AM", "AI-24CS302", "Artificial Intelligence [L]", "N-314A", "Dr. T.R. Rajesh", "Lecture"),
    ("Monday", "09:55 AM - 10:45 AM", "DBMS-25CS203", "Database Management System [L]", "N-314A", "Dr. Md. Oqail Ahmad", "Lecture"),
    ("Monday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Monday", "12:30 PM - 02:10 PM", "DS-25CS201", "Data Structures [T]", "N-314A", "Sk. Farheen Sulthana, Sk. Afrin Neha, Tirumala Soma Venkata Sesi Kumar, A. Manikanta", "Tutorial"),
    ("Monday", "02:20 PM - 03:10 PM", "DMS-25MT202", "Discrete Mathematical Structures [L]", "N-313", "Dr. Sannu Venkateswarlu", "Lecture"),
    ("Monday", "03:10 PM - 04:00 PM", "OOPS-25CS204", "Object Oriented Programming Through Java [L]", "N-313", "Dr. O. Bhaskar", "Lecture"),

    # Tuesday
    ("Tuesday", "08:15 AM - 10:45 AM", "OOPS-25CS204", "Object Oriented Programming Through Java [P]", "N-405", "Dr. O. Bhaskar, Kondapalli Sravya, Pragathi, M.Phanindra Chowdary", "Lab"),
    ("Tuesday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Tuesday", "12:30 PM - 02:10 PM", "DW-25CS202", "Data Wrangling and Visualization [T]", "N-313", "Vara Lakshmi, Ms. Yemineni Sravani, K.Pushpavalli, B. Devi Prasanna", "Tutorial"),
    ("Tuesday", "02:20 PM - 04:00 PM", "DBMS-25CS203", "Database Management System [T]", "N-313", "Naga Sivakumari, Arepati Kishor Kumar, Nemalikanti Deena, A Mounika", "Tutorial"),

    # Wednesday
    ("Wednesday", "08:15 AM - 09:55 AM", "DMS-25MT202", "Discrete Mathematical Structures [T]", "N-314", "Dr. Sannu Venkateswarlu", "Tutorial"),
    ("Wednesday", "09:55 AM - 10:45 AM", "DS-25CS201", "Data Structures [L]", "N-314", "Dr. Satish Kumar Satti", "Lecture"),
    ("Wednesday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Wednesday", "12:30 PM - 02:10 PM", "AI-24CS302", "Artificial Intelligence [T]", "N-313", "Dr. T.R. Rajesh, Y.Vivek, T.Soma Venkata Sesi Kumar", "Tutorial"),
    ("Wednesday", "02:20 PM - 03:10 PM", "OOPS-25CS204", "Object Oriented Programming Through Java [L]", "N-414", "Dr. O. Bhaskar", "Lecture"),
    ("Wednesday", "03:10 PM - 04:00 PM", "DLD-25CS205", "Digital Logic design [L]", "N-414", "Mr. Akula Gopi", "Lecture"),

    # Thursday
    ("Thursday", "08:15 AM - 10:45 AM", "DS-25CS201", "Data Structures [P]", "N-405", "Dr. Satish Kumar Satti, Sk. Farheen Sulthana, Sk. Afrin Neha, Tirumala Soma Venkata Sesi Kumar", "Lab"),
    ("Thursday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Thursday", "12:30 PM - 01:20 PM", "COUN", "Counseling / Mentorship", "N-314B", "Dr. T.R. Rajesh (Class Teacher)", "Counseling"),
    ("Thursday", "01:20 PM - 02:10 PM", "AI-24CS302", "Artificial Intelligence [L]", "N-314B", "Dr. T.R. Rajesh", "Lecture"),
    ("Thursday", "02:20 PM - 03:10 PM", "DMS-25MT202", "Discrete Mathematical Structures [L]", "N-414", "Dr. Sannu Venkateswarlu", "Lecture"),
    ("Thursday", "03:10 PM - 04:00 PM", "DBMS-25CS203", "Database Management System [L]", "N-414", "Dr. Md. Oqail Ahmad", "Lecture"),

    # Friday
    ("Friday", "08:15 AM - 09:05 AM", "AI-24CS302", "Artificial Intelligence [L]", "N-306", "Dr. T.R. Rajesh", "Lecture"),
    ("Friday", "09:05 AM - 09:55 AM", "DMS-25MT202", "Discrete Mathematical Structures [L]", "N-306", "Dr. Sannu Venkateswarlu", "Lecture"),
    ("Friday", "09:55 AM - 10:45 AM", "OOPS-25CS204", "Object Oriented Programming Through Java [L]", "N-306", "Dr. O. Bhaskar", "Lecture"),
    ("Friday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Friday", "12:30 PM - 02:10 PM", "DLD-25CS205", "Digital Logic design [T]", "N-313", "Mr. Akula Gopi", "Tutorial"),
    ("Friday", "02:20 PM - 03:10 PM", "DBMS-25CS203", "Database Management System [L]", "N-313", "Dr. Md. Oqail Ahmad", "Lecture"),
    ("Friday", "03:10 PM - 04:00 PM", "DS-25CS201", "Data Structures [L]", "N-313", "Dr. Satish Kumar Satti", "Lecture"),

    # Saturday
    ("Saturday", "08:15 AM - 10:45 AM", "DBMS-25CS203", "Database Management System [P]", "N-405", "Dr. Md. Oqail Ahmad, Naga Sivakumari, Arepati Kishor Kumar, Nemalikanti Deena", "Lab"),
    ("Saturday", "11:00 AM - 11:50 AM", "SELF-LEARN", "Self Learning / Advanced Learning", "N-313", "Faculty Mentors", "Self Learning"),
    ("Saturday", "12:30 PM - 01:20 PM", "DLD-25CS205", "Digital Logic design [L]", "N-313", "Mr. Akula Gopi", "Lecture"),
    ("Saturday", "01:20 PM - 02:10 PM", "DS-25CS201", "Data Structures [L]", "N-313", "Dr. Satish Kumar Satti", "Lecture"),
    ("Saturday", "02:20 PM - 04:00 PM", "DW-25CS202", "Data Wrangling and Visualization [P]", "N-313", "Vara Lakshmi, Ms. Yemineni Sravani, K.Pushpavalli, B. Devi Prasanna", "Lab")
]

# Section 8 Faculty members to register
NEW_FACULTY = [
    ("fac-tr-rajesh", "EMP2001", "Dr. T.R. Rajesh", "Associate Professor & Section 8 Class Teacher", "CSE", "rajesh_tr@vignan.ac.in", "+91 96765 60542", "N-313 Faculty Staff Room / CSE Department", "CLASS_TEACHER,MENTOR,COURSE_FACULTY", "10:00 AM - 12:00 PM (Mon-Fri)"),
    ("fac-satish-satti", "EMP2002", "Dr. Satish Kumar Satti", "Professor", "CSE", "satish.satti@vignan.ac.in", "+91 95812 36143", "N-313 Faculty Staff Room / CSE Department", "COURSE_FACULTY", "02:00 PM - 04:00 PM (Mon-Fri)"),
    ("fac-sannu-venkat", "EMP2003", "Dr. Sannu Venkateswarlu", "Associate Professor", "S&H (Mathematics)", "sannu.venkat@vignan.ac.in", "+91 94400 33445", "S&H Block Room 204", "COURSE_FACULTY", "11:00 AM - 01:00 PM (Mon-Fri)"),
    ("fac-oqail-ahmad", "EMP2004", "Dr. Md. Oqail Ahmad", "Associate Professor", "CSE", "oqail.ahmad@vignan.ac.in", "+91 84392 43408", "N-313 Faculty Staff Room / CSE Department", "COURSE_FACULTY", "03:00 PM - 05:00 PM (Mon-Fri)"),
    ("fac-o-bhaskar", "EMP2005", "Dr. O. Bhaskar", "Associate Professor", "CSE", "bhaskar.o@vignan.ac.in", "+91 63015 77419", "N-313 Faculty Staff Room / CSE Department", "COURSE_FACULTY", "10:00 AM - 12:00 PM (Mon-Fri)"),
    ("fac-akula-gopi", "EMP2006", "Mr. Akula Gopi", "Assistant Professor", "ECE/CSE", "akula.gopi@vignan.ac.in", "+91 72870 58820", "ECE Block Room 112", "COURSE_FACULTY", "01:00 PM - 03:00 PM (Mon-Fri)"),
    ("fac-vara-lakshmi", "EMP2007", "Mrs. Vara Lakshmi", "Assistant Professor", "CSE", "varalakshmi@vignan.ac.in", "+91 81422 14788", "N-313 Faculty Staff Room / CSE Department", "COURSE_FACULTY", "02:00 PM - 04:00 PM (Mon-Fri)"),
]

def calculate_consecutive_needed(attended, total, target_pct=75.0):
    current = (attended / total * 100.0) if total > 0 else 0.0
    if current >= target_pct:
        return 0
    needed = math.ceil((target_pct * total - 100.0 * attended) / (100.0 - target_pct))
    return max(0, needed)

def ingest_section_8():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"Ingesting Section 8 data into {DB_PATH}...")

    # 1. Insert Faculty
    for f in NEW_FACULTY:
        cur.execute("""
            INSERT OR REPLACE INTO faculty 
            (faculty_id, employee_no, name, designation, department, email, phone, cabin, role, office_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, f)
    print(f"[OK] Registered {len(NEW_FACULTY)} Section 8 faculty members.")

    # 2. Ingest Students & All Dependent Tables
    students_count = 0
    attendance_count = 0
    timetable_count = 0
    marks_count = 0
    fees_count = 0
    exams_count = 0

    for item in SECTION_8_STUDENTS:
        (roll, name, att_ds, att_dbmsis, att_ooptj, att_dldes, att_ai, att_dms,
         att_dsl, att_dbmsl, att_ooptjl, att_dwav, att_lib, att_coun, total_att) = item

        sid = f"stu-{roll.lower()}"
        uid = f"usr-stu-{roll.lower()}"
        email = f"{roll.lower()}@vignan.ac.in"

        # Mock CGPA strongly aligned with total attendance
        # e.g., 95%+ attendance -> 9.0 - 9.85 CGPA, 50% attendance -> 5.8 - 6.4 CGPA
        reg_num = int(roll[-3:]) if roll[-3:].isdigit() else 40
        seed_offset = ((reg_num % 11) - 5) * 0.04
        base_cgpa = 5.2 + (total_att / 100.0) * 4.4 + seed_offset
        cgpa = round(min(9.90, max(5.40, base_cgpa)), 2)

        # Backlog count: 0 for healthy attendance, 1-2 for critical attendance
        backlogs = 0
        if total_att < 55.0:
            backlogs = 2
        elif total_att < 65.0:
            backlogs = 1 if (reg_num % 2 == 0) else 0

        # Fee outstanding: mock realistic distribution
        fee_due = 0.0
        fee_status = "PAID"
        fee_paid = 100000.0
        if reg_num % 7 == 0:
            fee_due = 45000.0
            fee_paid = 55000.0
            fee_status = "PARTIAL"
        elif reg_num % 9 == 0:
            fee_due = 25000.0
            fee_paid = 75000.0
            fee_status = "PARTIAL"

        # Gender heuristic
        female_clues = ["KUMARI", "SRI", "LAKSHMI", "MEGHANA", "DIVIJA", "JOSHNA", "DHAKSHAYANI", "HASINI", "VISHALINI", "HARSHINI", "DEVISREE", "VYSHNAVI", "ANUSREE", "ROHITHA", "SARANYA", "ASRITHA", "AMRUTHA", "SUDHA", "PAMULA", "KOUSHIKA"]
        gender = "F" if any(c in name for c in female_clues) else "M"

        # Insert / update student
        cur.execute("""
            INSERT OR REPLACE INTO students (
                student_id, user_id, roll_no, username, password_hash, full_name, gender, email,
                programme_code, programme_name, department_code, batch_label, section_code,
                current_year_of_study, cgpa, backlog_count, overall_attendance_pct, fee_outstanding,
                mentor_name, status, semester,
                class_teacher_name, class_teacher_phone, class_teacher_email, class_teacher_cabin,
                counsellor_name, counsellor_phone, counsellor_email, counsellor_cabin,
                mentor_phone, mentor_email, mentor_cabin,
                hod_name, hod_phone, hod_email
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sid, uid, roll, roll.lower(), roll.upper(), name, gender, email,
            "BTCSE", "B.Tech Computer Science and Engineering", "CSE", "2024-28 CSE", "8",
            2, cgpa, backlogs, total_att, fee_due,
            "Dr. T.R. Rajesh", "ACTIVE", 3,
            "Dr. T.R. Rajesh", "+91 96765 60542", "rajesh_tr@vignan.ac.in", "N-313 Faculty Staff Room / CSE Department",
            "Dr. Radhika Sharma", "+91 98480 12345", "radhika.sharma@vignan.ac.in", "C-402, Student Wellness Center & Counseling Cell",
            "+91 96765 60542", "rajesh_tr@vignan.ac.in", "N-313 Faculty Staff Room / CSE Department",
            "Dr. S. V. Phani Kumar", "+91 94401 55678", "hod_cse@vignan.ac.in"
        ))
        students_count += 1

        # Delete existing attendance & timetable for this student if re-running
        cur.execute("DELETE FROM attendance WHERE student_id = ?", (sid,))
        cur.execute("DELETE FROM timetable WHERE student_id = ?", (sid,))
        cur.execute("DELETE FROM marks WHERE student_id = ?", (sid,))
        cur.execute("DELETE FROM fees WHERE student_id = ?", (sid,))
        cur.execute("DELETE FROM exams WHERE student_id = ?", (sid,))

        # Attendance mapping for the 7 core subjects
        course_attendances = [
            ("DS-25CS201", "Data Structures", "Dr. Satish Kumar Satti", 33, att_ds),
            ("DBMS-25CS203", "Database Management System", "Dr. Md. Oqail Ahmad", 38, att_dbmsis),
            ("OOPS-25CS204", "Object Oriented Programming Through Java", "Dr. O. Bhaskar", 20, att_ooptj),
            ("DLD-25CS205", "Digital Logic design", "Mr. Akula Gopi", 36, att_dldes),
            ("AI-24CS302", "Artificial Intelligence", "Dr. T.R. Rajesh", 35, att_ai),
            ("DMS-25MT202", "Discrete Mathematical Structures", "Dr. Sannu Venkateswarlu", 27, att_dms),
            ("DW-25CS202", "Data Wrangling and Visualization", "Vara Lakshmi", 25, att_dwav),
        ]

        for ccode, ctitle, cfac, held, pct in course_attendances:
            attended = int(round(pct * held / 100.0))
            needed = calculate_consecutive_needed(attended, held, 75.0)
            risk = "SAFE" if pct >= 75.0 else ("WARNING" if pct >= 65.0 else "CRITICAL")
            cur.execute("""
                INSERT INTO attendance (
                    student_id, course_code, course_title, faculty_name,
                    classes_held, classes_attended, current_pct, required_pct,
                    classes_needed, risk_level, deadline, recovery_possible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, ccode, ctitle, cfac, held, attended, pct, 75.0, needed, risk, "2026-11-20", 1 if needed <= 20 else 0))
            attendance_count += 1

        # Timetable slots
        for t_slot in TIMETABLE_SLOTS_SEC8:
            cur.execute("""
                INSERT INTO timetable (
                    student_id, day_of_week, time_slot, course_code, course_title, room_no, faculty_name, slot_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, t_slot[0], t_slot[1], t_slot[2], t_slot[3], t_slot[4], t_slot[5], t_slot[6]))
            timetable_count += 1

        # Internal Marks
        for ccode, ctitle, _, _, _ in course_attendances:
            # Scaled marks based on student's CGPA
            perf_factor = cgpa / 10.0
            mid1_marks = int(round(40 * perf_factor * (0.85 + (reg_num % 5) * 0.03)))
            mid1_marks = min(40, max(14, mid1_marks))
            quiz_marks = int(round(10 * perf_factor * (0.90 + (reg_num % 4) * 0.02)))
            quiz_marks = min(10, max(4, quiz_marks))
            lab_marks = int(round(20 * perf_factor * (0.90 + (reg_num % 3) * 0.03)))
            lab_marks = min(20, max(8, lab_marks))

            cur.execute("""
                INSERT INTO marks (student_id, course_code, course_title, assessment_name, max_marks, obtained_marks, percentage, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, ccode, ccode, "Mid-1 (Descriptive)", 40, mid1_marks, round(mid1_marks/40.0*100, 1), "PASS" if mid1_marks >= 16 else "FAIL"))
            cur.execute("""
                INSERT INTO marks (student_id, course_code, course_title, assessment_name, max_marks, obtained_marks, percentage, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, ccode, ccode, "Online Quiz-1", 10, quiz_marks, round(quiz_marks/10.0*100, 1), "PASS"))
            cur.execute("""
                INSERT INTO marks (student_id, course_code, course_title, assessment_name, max_marks, obtained_marks, percentage, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, ccode, ccode, "Lab Assignment", 20, lab_marks, round(lab_marks/20.0*100, 1), "PASS"))
            marks_count += 3

        # Fee Record
        cur.execute("""
            INSERT INTO fees (
                student_id, academic_year, total_demand, paid_amount, outstanding_balance,
                due_date, status, next_installment_amount, next_installment_date, penalty_warning
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sid, "2025-26", 100000.0, fee_paid, fee_due,
            "2026-10-15", fee_status, fee_due, "2026-10-15",
            "No fine before 15 Oct." if fee_due > 0 else "All dues cleared."
        ))
        fees_count += 1

        # Exam Schedule (Matching Official VFSTR Academic Calendar)
        exam_entries = [
            ("Formative Assessment (M-2 FA-1)", "M2-FA1", "Module-2 Formative Assessment 1", "2026-10-06", "10:00 AM - 12:00 PM", "Department of CSE, VFSTR", "APPROVED"),
            ("Formative Assessment (M-2 FA-2)", "M2-FA2", "Module-2 Formative Assessment 2", "2026-11-11", "10:00 AM - 12:00 PM", "Department of CSE, VFSTR", "APPROVED"),
            ("Practical Summative Assessment", "DW-25CS202", "Data Wrangling & Visualization Practical", "2026-11-17", "02:00 PM - 05:00 PM", "Computing Lab N-314A", "APPROVED"),
            ("Summative End-Semester Theory", "DLD-25CS205", "Digital Logic design", "2026-11-21", "10:00 AM - 01:00 PM", "Examination Hall A2", "APPROVED"),
            ("Summative End-Semester Theory", "DS-25CS201", "Data Structures", "2026-11-24", "10:00 AM - 01:00 PM", "Examination Hall B1", "APPROVED"),
            ("Summative End-Semester Theory", "DMS-25MT202", "Discrete Mathematical Structures", "2026-11-26", "10:00 AM - 01:00 PM", "Examination Hall A2", "APPROVED"),
            ("Summative End-Semester Theory", "OOPS-25CS204", "Object Oriented Programming Through Java", "2026-11-28", "10:00 AM - 01:00 PM", "Examination Hall A1", "APPROVED"),
            ("Summative End-Semester Theory", "DBMS-25CS203", "Database Management System", "2026-12-01", "10:00 AM - 01:00 PM", "Examination Hall B3", "APPROVED"),
            ("Summative End-Semester Theory", "AI-24CS302", "Artificial Intelligence", "2026-12-03", "10:00 AM - 01:00 PM", "Examination Hall A1", "APPROVED"),
        ]

        for ex in exam_entries:
            cur.execute("""
                INSERT INTO exams (student_id, exam_type, course_code, course_title, exam_date, time, venue, hall_ticket_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid, ex[0], ex[1], ex[2], ex[3], ex[4], ex[5], ex[6]))
            exams_count += 1

    conn.commit()
    conn.close()

    print("\n=== INGESTION SUCCESSFUL ===")
    print(f"Students ingested: {students_count}")
    print(f"Attendance rows created: {attendance_count}")
    print(f"Timetable rows created: {timetable_count}")
    print(f"Marks rows created: {marks_count}")
    print(f"Fees rows created: {fees_count}")
    print(f"Exams rows created: {exams_count}")

if __name__ == "__main__":
    ingest_section_8()
