import os
import sys
import uuid
import sqlite3

# Add BACKEND to path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.database import get_db_connection

def seed_campus_data():
    conn = get_db_connection()
    
    # 1. Add HODs to Faculty
    hods = [
        {"employee_no": "VFSTR-HOD-CSE", "name": "Dr. S. V. Phani Kumar", "designation": "Head of Department", "department": "Computer Science and Engineering", "email": "hod_cse@vignan.ac.in", "phone": "+91 94401 55678", "cabin": "A-309", "role": "HOD", "office_hours": "Mon-Fri 2PM-4PM"},
        {"employee_no": "VFSTR-HOD-ECE", "name": "Dr. T. Pitchaiah", "designation": "Head of Department", "department": "Electronics & Communication Engineering", "email": "hod_ece@vignan.ac.in", "phone": "+91 94401 55679", "cabin": "A-201", "role": "HOD", "office_hours": "Mon-Fri 3PM-5PM"},
        {"employee_no": "VFSTR-HOD-EEE", "name": "Dr. G. Srinivasa Rao", "designation": "Head of Department", "department": "Electrical & Electronics Engineering", "email": "hod_eee@vignan.ac.in", "phone": "+91 94401 55680", "cabin": "H-102", "role": "HOD", "office_hours": "Tue-Thu 10AM-12PM"},
        {"employee_no": "VFSTR-HOD-MECH", "name": "Dr. L. S. Raju", "designation": "Head of Department", "department": "Mechanical Engineering", "email": "hod_mech@vignan.ac.in", "phone": "+91 94401 55681", "cabin": "H-205", "role": "HOD", "office_hours": "Mon-Wed 2PM-4PM"},
        {"employee_no": "VFSTR-HOD-BIOTECH", "name": "Dr. S. Asha", "designation": "Head of Department", "department": "Biotechnology", "email": "hod_biotech@vignan.ac.in", "phone": "+91 94401 55682", "cabin": "U-105", "role": "HOD", "office_hours": "Mon-Fri 11AM-1PM"}
    ]
    
    for h in hods:
        try:
            conn.execute("""
                INSERT INTO faculty (faculty_id, employee_no, name, designation, department, email, phone, cabin, role, office_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f"fac-{uuid.uuid4().hex[:8]}", h["employee_no"], h["name"], h["designation"], h["department"], h["email"], h["phone"], h["cabin"], h["role"], h["office_hours"]))
        except sqlite3.IntegrityError:
            # Update if already exists
            conn.execute("""
                UPDATE faculty SET name=?, designation=?, department=?, email=?, phone=?, cabin=?, role=?, office_hours=? WHERE employee_no=?
            """, (h["name"], h["designation"], h["department"], h["email"], h["phone"], h["cabin"], h["role"], h["office_hours"], h["employee_no"]))

    # 2. Add Campus Locations
    locations = [
        {"room_number": "A-309", "block": "A-Block (Admin)", "floor": "3rd Floor", "description": "CSE Department Head Office"},
        {"room_number": "A-201", "block": "A-Block (Admin)", "floor": "2nd Floor", "description": "ECE Department Head Office"},
        {"room_number": "H-102", "block": "H-Block", "floor": "Ground Floor", "description": "EEE Department Head Office"},
        {"room_number": "H-205", "block": "H-Block", "floor": "2nd Floor", "description": "Mechanical Department Head Office"},
        {"room_number": "U-105", "block": "U-Block", "floor": "Ground Floor", "description": "Biotech Department Head Office"},
        {"room_number": "LIB-01", "block": "NTR Vignan Library", "floor": "Ground Floor", "description": "Main Reading Hall & Reference Section"},
        {"room_number": "FC-01", "block": "Food Court", "floor": "Ground Floor", "description": "Main University Cafeteria"}
    ]
    
    # clear existing locations for idempotency
    conn.execute("DELETE FROM campus_locations")
    
    for loc in locations:
        conn.execute("""
            INSERT INTO campus_locations (location_id, room_number, block, floor, description)
            VALUES (?, ?, ?, ?, ?)
        """, (f"loc-{uuid.uuid4().hex[:8]}", loc["room_number"], loc["block"], loc["floor"], loc["description"]))

    # 3. Add Fresher FAQs
    faqs = [
        {"topic": "Anti-Ragging", "question": "What should I do if I face ragging?", "answer": "VFSTR has a strict zero-tolerance policy against ragging. If you face any harassment, immediately contact the Anti-Ragging Helpline at 1800-425-XXXX or reach out to your faculty mentor or the Chief Warden. You can also report via the university portal anonymously.", "keywords": "ragging, harassment, help, emergency, senior"},
        {"topic": "Library", "question": "What are the NTR Vignan Library timings?", "answer": "The NTR Vignan Library is open from 8:00 AM to 8:00 PM on weekdays and 9:00 AM to 1:00 PM on Sundays. Remember to carry your student ID card.", "keywords": "library, books, reading, study, timing, hours"},
        {"topic": "Hostel", "question": "Where are the boys and girls hostels located?", "answer": "The boys hostels (Priyadarshini, Vignan Vihar Boys hostel in front of N block, etc.) are located on the eastern side of the campus near the sports complex. The girls hostels are situated in a highly secure zone near the main entrance.", "keywords": "hostel, accommodation, stay, room, dorm, Vignan Vihar, N block"},
        {"topic": "Food Court", "question": "Where is the canteen and what are its timings?", "answer": "There are canteens and print out copy shops in each block's ground floor. There is a big canteen named MHP to eat in break time, and beside it is Zest for day-to-day items. The main Food Court (FC-01) is near the central lawn (7:30 AM - 7:30 PM).", "keywords": "food, canteen, cafeteria, eating, lunch, snacks, MHP, Zest"},
        {"topic": "ID Card", "question": "Where do I collect my student ID card?", "answer": "Freshers can collect their student ID cards from the Admission Cell located in the Administrative Block (A-Block) Ground Floor.", "keywords": "id card, identity, admission, card"},
        {"topic": "Clubs", "question": "How can I join student clubs like SAC (Student Activities Council)?", "answer": "You can register for various clubs under SAC (cultural, technical, sports) during the induction program in the first week. Notices will be put up on the U-Block notice boards and on the university portal.", "keywords": "club, sports, cultural, sac, activities, join"}
    ]
    
    # clear existing faqs
    conn.execute("DELETE FROM fresher_faqs")
    for f in faqs:
        conn.execute("""
            INSERT INTO fresher_faqs (faq_id, topic, question, answer, keywords)
            VALUES (?, ?, ?, ?, ?)
        """, (f"faq-{uuid.uuid4().hex[:8]}", f["topic"], f["question"], f["answer"], f["keywords"]))

    conn.commit()
    print("Database seeded with HOD faculty data, campus locations, and fresher FAQs.")

if __name__ == "__main__":
    seed_campus_data()
