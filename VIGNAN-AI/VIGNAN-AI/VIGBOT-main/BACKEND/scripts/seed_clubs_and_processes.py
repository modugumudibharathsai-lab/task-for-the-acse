import sqlite3
import uuid

def get_db_connection():
    db_path = r"database\vigbot.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS studentlife_club (
            club_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            theme_color TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS studentlife_club_member (
            member_id TEXT PRIMARY KEY,
            club_id TEXT NOT NULL,
            member_name TEXT NOT NULL,
            role TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY(club_id) REFERENCES studentlife_club(club_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS studentlife_club_joining_step (
            step_id TEXT PRIMARY KEY,
            club_id TEXT NOT NULL,
            step_order INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY(club_id) REFERENCES studentlife_club(club_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_procedure (
            procedure_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            rules TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_procedure_step (
            step_id TEXT PRIMARY KEY,
            procedure_id TEXT NOT NULL,
            step_order INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            FOREIGN KEY(procedure_id) REFERENCES knowledge_procedure(procedure_id)
        )
    """)
    conn.commit()

def seed_data(conn):
    cursor = conn.cursor()
    
    # 1. Clubs
    clubs = [
        ("ANC", "Anti-Ragging Cell (ANC)", "Statutory", "The university maintains a strict zero-tolerance policy towards ragging. ANC ensures a safe, welcoming environment for all freshers.", "rose"),
        ("SAC", "Student Activities Center (SAC)", "Administrative", "The core committee governing all student cultural, technical, and sports events across the campus.", "blue"),
        ("TECH", "Code & Build Club", "Technical", "A community for aspiring software developers, hardware tinkerers, and AI enthusiasts.", "emerald"),
        ("CULT", "Cultural Society", "Cultural", "Promoting arts, dance, music, and dramatics. The heartbeat of university fests.", "purple")
    ]
    
    cursor.execute("DELETE FROM studentlife_club")
    for c in clubs:
        cursor.execute("INSERT INTO studentlife_club (club_id, name, category, description, theme_color) VALUES (?, ?, ?, ?, ?)", c)

    # 2. Club Members
    cursor.execute("DELETE FROM studentlife_club_member")
    members = [
        ("m1", "ANC", "Prof. Rajiv Sharma", "Chief Nodal Officer", "Contact for any immediate grievance or ragging reports."),
        ("m2", "ANC", "Dr. Smita Rao", "Faculty Coordinator", "Oversees hostel patrols and anti-ragging squads."),
        ("m3", "SAC", "Rahul Verma", "Student President", "4th Year, CSE. Leads the SAC executive council."),
        ("m4", "SAC", "Priya Singh", "Cultural Secretary", "3rd Year, ECE. Organizes all major university fests."),
        ("m5", "TECH", "Amit Patel", "Lead Organizer", "Full-stack developer and open-source contributor."),
        ("m6", "CULT", "Neha Gupta", "Dance Troupe Lead", "Choreographer and state-level dancer.")
    ]
    for m in members:
        cursor.execute("INSERT INTO studentlife_club_member (member_id, club_id, member_name, role, details) VALUES (?, ?, ?, ?, ?)", m)

    # 3. Joining Steps
    cursor.execute("DELETE FROM studentlife_club_joining_step")
    steps = [
        # SAC Joining Steps
        ("s1", "SAC", 1, "Fill the Online Application", "Login to the student portal and submit the SAC membership form detailing your past experiences."),
        ("s2", "SAC", 2, "Portfolio Review", "The executive council will review your submission and shortlist candidates based on skill sets."),
        ("s3", "SAC", 3, "Interview Round", "A formal interview with the current SAC committee to gauge your leadership and teamwork skills."),
        ("s4", "SAC", 4, "Final Induction", "Selected candidates are officially inducted during the annual SAC orientation ceremony."),
        
        # TECH Club
        ("s5", "TECH", 1, "Join the Discord Server", "All technical discussions happen on our public Discord server. Link is on the club notice board."),
        ("s6", "TECH", 2, "Solve the Entry Challenge", "Complete a basic algorithmic or web development task to prove your fundamental knowledge."),
        ("s7", "TECH", 3, "Attend the First Meetup", "Come to the lab during our weekly meetup and present your solution to the senior members."),
        
        # CULT Club
        ("s8", "CULT", 1, "Auditions", "Keep an eye out for audition posters. Prepare a 2-minute performance (dance, singing, drama)."),
        ("s9", "CULT", 2, "Callback Round", "Perform alongside current members to see if your style matches the troupe's dynamics."),
        ("s10", "CULT", 3, "Rehearsal Bootcamp", "Attend a 3-day intensive boot camp. Selection is confirmed after successfully completing this camp.")
    ]
    for s in steps:
        cursor.execute("INSERT INTO studentlife_club_joining_step (step_id, club_id, step_order, title, description) VALUES (?, ?, ?, ?, ?)", s)

    # 4. Procedures
    cursor.execute("DELETE FROM knowledge_procedure")
    procedures = [
        ("p1", "How to reach HOD Sir's Cabin (CSE Department)", "Detailed navigation instructions to reach the Head of Department (CSE) office from the main gate.", "Rule 1: Visiting hours are strictly 3:00 PM to 4:30 PM. Rule 2: Prior appointment is recommended. Rule 3: Carry your student ID."),
        ("p2", "Filing an Anti-Ragging Complaint", "The exact steps to safely and securely file a ragging complaint without middleman interference.", "Rule 1: Zero tolerance policy. Rule 2: Identity is kept strictly confidential. Rule 3: False complaints carry severe penalties."),
        ("p3", "Applying for Bonafide Certificate", "Steps to request a bonafide certificate for bank loans or passport application.", "Rule 1: Cleared all fee dues. Rule 2: Takes 2 working days to process.")
    ]
    for p in procedures:
        cursor.execute("INSERT INTO knowledge_procedure (procedure_id, title, description, rules) VALUES (?, ?, ?, ?)", p)

    # 5. Procedure Steps
    cursor.execute("DELETE FROM knowledge_procedure_step")
    proc_steps = [
        # Reaching HOD's cabin
        ("ps1", "p1", 1, "Enter through the Main Gate and walk straight towards the Central Library block."),
        ("ps2", "p1", 2, "Take a left from the Library and enter Academic Block 'A'."),
        ("ps3", "p1", 3, "Take the elevator or stairs to the 3rd Floor."),
        ("ps4", "p1", 4, "Walk down the right corridor. The CSE Department Office is Room A-301."),
        ("ps5", "p1", 5, "The HOD's cabin is inside the main department office, clearly marked as 'Head of Department'."),
        
        # Filing ANC complaint
        ("ps6", "p2", 1, "Immediately distance yourself from the situation and reach a safe space (Hostel Warden's office or Security Desk)."),
        ("ps7", "p2", 2, "Open the VIGBOT Dashboard and navigate to the 'Clubs & Communities' section."),
        ("ps8", "p2", 3, "Locate the Anti-Ragging Cell (ANC) card and click on the 'Register Complaint' button."),
        ("ps9", "p2", 4, "Fill out the secure incident form. You can choose to remain completely anonymous. No faculty middleman is involved; the report goes directly to the Nodal Officer."),
        ("ps10", "p2", 5, "You will receive a secure Tracking ID to follow up on the action taken."),
        
        # Bonafide
        ("ps11", "p3", 1, "Log in to the ERP portal and go to 'Service Requests'."),
        ("ps12", "p3", 2, "Select 'Bonafide Certificate' and specify the purpose (e.g., Bank Loan)."),
        ("ps13", "p3", 3, "Pay the nominal processing fee of ₹50 online."),
        ("ps14", "p3", 4, "Collect the signed, stamped physical copy from the Admin block after 48 hours.")
    ]
    for ps in proc_steps:
        cursor.execute("INSERT INTO knowledge_procedure_step (step_id, procedure_id, step_order, instruction) VALUES (?, ?, ?, ?)", ps)

    conn.commit()
    print("Database seeded successfully with Clubs, Mock Members, Joining Steps, and Procedures.")

if __name__ == "__main__":
    conn = get_db_connection()
    create_tables(conn)
    seed_data(conn)
    conn.close()
