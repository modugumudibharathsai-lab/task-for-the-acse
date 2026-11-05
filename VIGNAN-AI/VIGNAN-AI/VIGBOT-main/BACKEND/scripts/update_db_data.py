import sqlite3

db_path = r"database\vigbot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Update Attendance Records
attendance_data = [
    ('251FA04E51', 80.0),
    ('251FA04E52', 86.0),
    ('251FA04E53', 89.0),
    ('251FA04E57', 82.0),
    ('251FA04E64', 98.0),
    ('251FA04131', 70.0),
    ('251FA04D46', 88.0),
    ('251FA04D56', 80.0),
    ('251FA04D69', 89.0),
    ('251FA04D73', 85.0),
]

for roll_no, pct in attendance_data:
    cursor.execute("""
        UPDATE students
        SET overall_attendance_pct = ?
        WHERE roll_no = ?
    """, (pct, roll_no))

# 2. Add HOD Cabin Instructions
procedures = [
    (
        'p2_hod_ece', 
        'How to reach HOD Sir\'s Cabin (ECE Department)', 
        'Detailed navigation instructions to reach the Head of Department (ECE) office from the main gate.',
        'Rule 1: Visiting hours are strictly 3:00 PM to 4:30 PM. Rule 2: Prior appointment is recommended.'
    ),
    (
        'p3_hod_eee', 
        'How to reach HOD Sir\'s Cabin (EEE Department)', 
        'Detailed navigation instructions to reach the Head of Department (EEE) office from the main gate.',
        'Rule 1: Visiting hours are strictly 3:00 PM to 4:30 PM. Rule 2: Prior appointment is recommended.'
    ),
    (
        'p4_hod_mech', 
        'How to reach HOD Sir\'s Cabin (Mechanical Department)', 
        'Detailed navigation instructions to reach the Head of Department (Mechanical) office from the main gate.',
        'Rule 1: Visiting hours are strictly 3:00 PM to 4:30 PM. Rule 2: Prior appointment is recommended.'
    ),
    (
        'p5_hod_biotech', 
        'How to reach HOD Sir\'s Cabin (Biotechnology Department)', 
        'Detailed navigation instructions to reach the Head of Department (Biotechnology) office from the main gate.',
        'Rule 1: Visiting hours are strictly 3:00 PM to 4:30 PM. Rule 2: Prior appointment is recommended.'
    )
]

steps = [
    # ECE
    ('ps2_1', 'p2_hod_ece', 1, 'Enter through the Main Gate and walk straight towards the A-Block.'),
    ('ps2_2', 'p2_hod_ece', 2, 'Take the stairs or elevator to the 2nd Floor of A-Block.'),
    ('ps2_3', 'p2_hod_ece', 3, 'Walk down the corridor and look for Room A-201.'),
    ('ps2_4', 'p2_hod_ece', 4, 'The HOD\'s cabin is inside the main department office, clearly marked as \'Head of Department\'.'),
    
    # EEE
    ('ps3_1', 'p3_hod_eee', 1, 'Enter through the Main Gate and head towards the H-Block.'),
    ('ps3_2', 'p3_hod_eee', 2, 'Enter H-Block on the Ground Floor.'),
    ('ps3_3', 'p3_hod_eee', 3, 'Proceed straight down the main hallway and locate Room H-102.'),
    ('ps3_4', 'p3_hod_eee', 4, 'The HOD\'s cabin is inside the main department office, clearly marked as \'Head of Department\'.'),
    
    # Mechanical
    ('ps4_1', 'p4_hod_mech', 1, 'Enter through the Main Gate and head towards the H-Block.'),
    ('ps4_2', 'p4_hod_mech', 2, 'Take the stairs to the 2nd Floor of H-Block.'),
    ('ps4_3', 'p4_hod_mech', 3, 'Locate Room H-205 down the corridor.'),
    ('ps4_4', 'p4_hod_mech', 4, 'The HOD\'s cabin is inside the main department office, clearly marked as \'Head of Department\'.'),
    
    # Biotech
    ('ps5_1', 'p5_hod_biotech', 1, 'Enter through the Main Gate and head towards the U-Block.'),
    ('ps5_2', 'p5_hod_biotech', 2, 'Enter U-Block on the Ground Floor.'),
    ('ps5_3', 'p5_hod_biotech', 3, 'Locate Room U-105 near the main entrance.'),
    ('ps5_4', 'p5_hod_biotech', 4, 'The HOD\'s cabin is inside the main department office, clearly marked as \'Head of Department\'.'),
]

# Insert procedures ignoring duplicates
for p in procedures:
    cursor.execute("""
        INSERT OR IGNORE INTO knowledge_procedure (procedure_id, title, description, rules)
        VALUES (?, ?, ?, ?)
    """, p)

for s in steps:
    cursor.execute("""
        INSERT OR IGNORE INTO knowledge_procedure_step (step_id, procedure_id, step_order, instruction)
        VALUES (?, ?, ?, ?)
    """, s)

conn.commit()
print("Successfully updated attendance and inserted HOD procedures.")
conn.close()
