import sqlite3
import json
import datetime
import os

STUDENT_ID = "251FA04E13"

db_path = os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

def seed():
    # Helper for times
    now = datetime.datetime.now()
    def delta(days=0, hours=0, minutes=0):
        return (now + datetime.timedelta(days=days, hours=hours, minutes=minutes)).isoformat()
        
    print("Clearing existing table data...")
    # Clean up first
    tables = [
        "ai_knowledge_base", "academic_records", "gamification", "library_resources",
        "calendar_events", "hostel_requests", "studentlife_grievance", "resumes",
        "wellness_resources", "studentlife_club_joining_step", "studentlife_club_member",
        "studentlife_club_application", "studentlife_club", "event_registrations",
        "marketplace_listings", "campus_locations", "lost_and_found", "bookings",
        "facilities", "transportation_routes", "alumni_mentors", "campus_polls",
        "broadcast_alerts", "fresher_faqs", "knowledge_procedure_step", "knowledge_procedure",
        "library_lended_books"
    ]
    for table in tables:
        try:
            c.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass # Table might not exist or be empty
            
    # 1. AI Knowledge Base (ai-helpdesk)
    ai_faqs = [
        ("General", "What are the library timings?", "The library is open from 8:00 AM to 10:00 PM on weekdays, and 9:00 AM to 5:00 PM on weekends.", '{"tags": ["library", "timings"]}'),
        ("Transport", "How can I track my college bus?", "You can track the live location of all buses in the 'Transport' tab of the sidebar.", '{"tags": ["bus", "transport", "tracking"]}'),
        ("Academics", "Where do I check my CGPA?", "You can check your semester-wise grades and CGPA in the 'Marks & CGPA' tab.", '{"tags": ["grades", "cgpa", "results"]}'),
        ("Hostel", "How to apply for a gate pass?", "Go to 'Hostel & Mess', select 'Gate Pass Request', fill the required details, and wait for warden approval.", '{"tags": ["hostel", "gate pass", "leave"]}'),
        ("General", "How to book a badminton court?", "Use the 'Facility Booking' tab to reserve courts up to 48 hours in advance.", '{"tags": ["sports", "booking", "badminton"]}'),
    ]
    c.executemany("INSERT INTO ai_knowledge_base (category, question, answer, metadata) VALUES (?, ?, ?, ?)", ai_faqs)

    # 2. Academic Records (grades/marks)
    academic_records = [
        (STUDENT_ID, 1, 8.2, 22, delta(-365)),
        (STUDENT_ID, 2, 8.5, 22, delta(-180)),
        (STUDENT_ID, 3, 8.8, 20, delta(-90)),
        (STUDENT_ID, 4, 8.42, 24, now.isoformat()),
    ]
    c.executemany("INSERT INTO academic_records (student_id, semester, cgpa, credits_completed, created_at) VALUES (?, ?, ?, ?, ?)", academic_records)

    # 3. Gamification
    badges = json.dumps([
        {"name": "Early Bird", "icon": "sunrise", "description": "Attended 10 8AM classes"},
        {"name": "Top Scorer", "icon": "star", "description": "Scored >9.0 SGPA in previous sem"},
        {"name": "Library Explorer", "icon": "book-open", "description": "Issued 20+ books"},
        {"name": "Bug Hunter", "icon": "bug", "description": "Reported an issue in Helpdesk"},
        {"name": "Community Helper", "icon": "heart", "description": "Answered 5 student queries"}
    ])
    c.execute("INSERT INTO gamification (student_id, points, badges_json) VALUES (?, ?, ?)", (STUDENT_ID, 3450, badges))

    # 4. Library Resources
    library = [
        ("Introduction to Algorithms", "CS201", "Book", "https://library.vignan.ac.in/books/algo"),
        ("Machine Learning Basics", "CS305", "Research Paper", "https://library.vignan.ac.in/papers/ml"),
        ("React Design Patterns", "CS402", "Video Course", "https://library.vignan.ac.in/videos/react"),
        ("Data Structures and Algorithms in Java", "CS202", "Book", "https://library.vignan.ac.in/books/ds"),
        ("Computer Networks", "CS301", "Book", "https://library.vignan.ac.in/books/cn"),
        ("Deep Learning with Python", "CS405", "Book", "https://library.vignan.ac.in/books/dl"),
        ("Artificial Intelligence: A Modern Approach", "CS401", "Book", "https://library.vignan.ac.in/books/ai"),
    ]
    c.executemany("INSERT INTO library_resources (title, course_code, type, link) VALUES (?, ?, ?, ?)", library)

    # 4b. Library Lended Books
    lended_books = [
        (STUDENT_ID, "Introduction to Algorithms", delta(-15), delta(5), "Issued"),
        (STUDENT_ID, "Computer Networks", delta(-30), delta(-5), "Overdue"),
        ("OTHER_STU", "Machine Learning Basics", delta(-10), delta(10), "Issued")
    ]
    c.executemany("INSERT INTO library_lended_books (student_id, book_title, issued_date, due_date, status) VALUES (?, ?, ?, ?, ?)", lended_books)


    # 5. Calendar Events
    calendar = [
        (STUDENT_ID, "Mid-Term Exam: OS", "Operating Systems Mid-term", delta(10, 10), delta(10, 12), "Academic", "Room N-312"),
        (STUDENT_ID, "AI Club Orientation", "Introduction to AI Club", delta(2, 16), delta(2, 18), "Extracurricular", "Main Auditorium"),
        (STUDENT_ID, "Web Dev Workshop", "Learn React and Next.js", delta(5, 14), delta(5, 17), "Workshop", "Lab 4"),
        (STUDENT_ID, "Assignment Due: ML", "Submit the classification assignment", delta(7, 23, 59), delta(7, 23, 59), "Deadline", "Online Portal"),
        (STUDENT_ID, "Sports Fest 2026", "Annual university sports meet", delta(15, 9), delta(17, 18), "Event", "Sports Ground"),
    ]
    c.executemany("INSERT INTO calendar_events (student_id, title, description, start_time, end_time, type, location) VALUES (?, ?, ?, ?, ?, ?, ?)", calendar)

    # 6. Hostel Requests
    hostel_reqs = [
        (STUDENT_ID, "Maintenance", "Fan regulator is broken in Room 204", "Open", delta(-1)),
        (STUDENT_ID, "GatePass", "Visiting home for the weekend", "Approved", delta(-5)),
        (STUDENT_ID, "Cleaning", "Requesting room cleaning, lots of dust.", "Resolved", delta(-10)),
        (STUDENT_ID, "Mess", "Quality of dinner on Tuesday was poor.", "Pending", delta(-2)),
    ]
    c.executemany("INSERT INTO hostel_requests (student_id, type, details, status, created_at) VALUES (?, ?, ?, ?, ?)", hostel_reqs)

    # 7. Studentlife Grievance (escalation)
    grievances = [
        ("GRV-1001", "Wi-Fi extremely slow in Block B library section", "In Progress", delta(-2), None, STUDENT_ID),
        ("GRV-1002", "Water cooler on 3rd floor N block is dispensing hot water", "Pending", delta(0, -5), None, STUDENT_ID),
        ("GRV-1003", "Stray dogs near the boys hostel entrance at night", "Resolved", delta(-15), "Animal control team handled it.", "OTHER_STU"),
    ]
    c.executemany("INSERT INTO studentlife_grievance (tracking_id, description, status, timestamp, withdrawal_reason, student_id) VALUES (?, ?, ?, ?, ?, ?)", grievances)

    # 8. Career / Resumes
    c.execute("INSERT INTO resumes (student_id, skills, projects, generated_pdf_link, created_at) VALUES (?, ?, ?, ?, ?)",
              (STUDENT_ID, "Python, React, TypeScript, SQL, Docker", "AI Helpdesk, E-Commerce Platform, Portfolio Website", "https://example.com/resume.pdf", delta(-2)))

    # 9. Wellness Resources
    wellness = [
        ("Managing Exam Stress", "Mental Health", "Techniques and deep breathing exercises to handle exam pressure effectively."),
        ("Campus Counseling Center", "Support", "Reach out to our trained counselors available 24/7 at +91 9876543210."),
        ("Morning Yoga Sessions", "Physical Wellbeing", "Join the morning yoga sessions at the sports complex every Mon-Wed-Fri 6 AM."),
        ("Sleep Hygiene Guide", "Lifestyle", "Learn how to improve your sleep cycle for better academic performance."),
        ("Peer Support Group", "Community", "A safe space to discuss personal challenges with trusted peers every Thursday."),
    ]
    c.executemany("INSERT INTO wellness_resources (title, category, description) VALUES (?, ?, ?)", wellness)

    # 10. Clubs & Communities
    clubs = [
        ("CLUB_AI", "AI Innovation Club", "Technical", "Exploring Artificial Intelligence, Machine Learning and Robotics", "indigo"),
        ("CLUB_MUSIC", "Symphony Music Club", "Cultural", "For the love of music, bands and vocalists", "rose"),
        ("CLUB_SPORTS", "Athletics & Sports", "Sports", "Organizing tournaments and fitness bootcamps", "emerald"),
        ("CLUB_CODE", "Competitive Programming", "Technical", "Crack FAANG interviews and algorithms", "amber"),
        ("CLUB_DRAMA", "Theatrix", "Cultural", "Stage plays, acting and scriptwriting", "purple"),
    ]
    c.executemany("INSERT INTO studentlife_club (club_id, name, category, description, theme_color) VALUES (?, ?, ?, ?, ?)", clubs)
    
    club_members = [
        ("MEM_1", "CLUB_AI", "VIGBOT", "Member", "Active contributor since Sem 2", STUDENT_ID),
        ("MEM_2", "CLUB_CODE", "VIGBOT", "Co-Lead", "Organizes weekly contests", STUDENT_ID),
        ("MEM_3", "CLUB_DRAMA", "Other Student", "Member", "Active actor", "OTHER_STU")
    ]
    c.executemany("INSERT INTO studentlife_club_member (member_id, club_id, member_name, role, details, student_id) VALUES (?, ?, ?, ?, ?, ?)", club_members)

    club_steps = [
        ("STP_1", "CLUB_MUSIC", 1, "Fill Interest Form", "Provide your musical background"),
        ("STP_2", "CLUB_MUSIC", 2, "Audition", "Sing or play an instrument for 2 mins"),
    ]
    c.executemany("INSERT INTO studentlife_club_joining_step (step_id, club_id, step_order, title, description) VALUES (?, ?, ?, ?, ?)", club_steps)

    club_apps = [
        ("CLUB_MUSIC", "VIGBOT", "Pending", delta(-1), None, STUDENT_ID),
        ("CLUB_DRAMA", "Other Student", "Pending", delta(-2), None, "OTHER_STU")
    ]
    try:
        c.executemany("INSERT INTO studentlife_club_application (club_id, student_name, status, timestamp, withdrawal_reason, student_id) VALUES (?, ?, ?, ?, ?, ?)", club_apps)
    except sqlite3.OperationalError:
        pass # Handle slightly varying schemas if any

    # 11. Event Registrations
    events = [
        (STUDENT_ID, "TechFest 2026", "QR_TF2026_12345", "Registered"),
        (STUDENT_ID, "AI Hackathon", "QR_AIHACK_888", "Checked In"),
        (STUDENT_ID, "Career Fair", "QR_CAREER_999", "Registered"),
    ]
    c.executemany("INSERT INTO event_registrations (student_id, event_name, qr_code, status) VALUES (?, ?, ?, ?)", events)

    # 12. Marketplace
    marketplace = [
        (STUDENT_ID, "Engineering Mathematics Book", "Books", 250.0, "Available", delta(-2)),
        (STUDENT_ID, "Scientific Calculator Casio 991EX", "Electronics", 800.0, "Sold", delta(-10)),
        ("OTHER_STU", "Drafting Table", "Stationery", 450.0, "Available", delta(-5)),
        ("OTHER_STU", "Arduino Starter Kit", "Electronics", 1200.0, "Available", delta(-1)),
        (STUDENT_ID, "Lab Coat (Size M)", "Clothing", 200.0, "Available", delta(0, -5)),
    ]
    c.executemany("INSERT INTO marketplace_listings (student_id, title, category, price, status, created_at) VALUES (?, ?, ?, ?, ?, ?)", marketplace)

    # 13. Campus Locations (Map)
    locations = [
        ("LOC_MAIN", "N-Block", "Main Block", "G to 4", "Main administrative and CSE department block"),
        ("LOC_LIB", "Central Library", "Library", "G to 2", "24/7 AC Library with thousands of books"),
        ("LOC_HOSTEL_A", "Boys Hostel A", "Hostel A", "G to 5", "First year boys accommodation"),
        ("LOC_LAB_1", "AI/ML Lab", "N-Block", "3rd Floor", "High-performance computing lab equipped with GPUs"),
        ("LOC_CAFE", "Main Canteen", "Cafeteria", "Ground", "Multicuisine food court open till 9 PM"),
    ]
    c.executemany("INSERT INTO campus_locations (location_id, room_number, block, floor, description) VALUES (?, ?, ?, ?, ?)", locations)

    # 14. Lost & Found
    lost = [
        (STUDENT_ID, "lost", "Blue Milton Water Bottle", "Lost near the central library seating area.", "bottle, blue", "251fa04e13@vignan.ac.in", "open", delta(-2), "https://picsum.photos/seed/bottle/400/300"),
        ("OTHER_STU", "found", "Scientific Calculator", "Found Casio calculator in N-312", "calculator", "admin@vignan.ac.in", "claimed", delta(-10), None),
        ("OTHER_STU", "lost", "Hostel Keys with Marvel keychain", "Lost somewhere near the canteen", "keys, marvel", "other@vignan.ac.in", "open", delta(0, -12), "/captain_america_key.jpg"),
        (STUDENT_ID, "found", "Apple AirPods Pro", "Found in AI Lab near the window seats", "airpods, apple", "251fa04e13@vignan.ac.in", "open", delta(0, -2), None),
    ]
    c.executemany("INSERT INTO lost_and_found (student_id, type, title, description, tags, contact_info, status, date_posted, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", lost)

    # 15. Facilities & Bookings
    facilities = [
        (1, "Badminton Court 1", "Sports", "Indoor synthetic court with proper lighting", 4, "https://picsum.photos/seed/badminton/800/600"),
        (2, "Study Room A", "Academic", "Quiet study room with whiteboards and AC", 6, "https://picsum.photos/seed/study/800/600"),
        (3, "Basketball Court", "Sports", "Outdoor cement court", 10, "https://picsum.photos/seed/basketball/800/600"),
        (4, "Music Room", "Extracurricular", "Soundproof room with drumkit and keyboards", 8, "https://picsum.photos/seed/music/800/600"),
    ]
    c.executemany("INSERT INTO facilities (id, name, type, description, capacity, image_url) VALUES (?, ?, ?, ?, ?, ?)", facilities)
    
    bookings = [
        (1, STUDENT_ID, delta(1)[:10], "17:00", "18:00", "Practice match", "confirmed"),
        (2, STUDENT_ID, delta(2)[:10], "14:00", "16:00", "Group study for mid-terms", "confirmed"),
        (4, "OTHER_STU", delta(1)[:10], "16:00", "17:00", "Band practice", "confirmed"),
    ]
    c.executemany("INSERT INTO bookings (facility_id, student_id, date, start_time, end_time, purpose, status) VALUES (?, ?, ?, ?, ?, ?, ?)", bookings)

    # 16. Transportation (Transport tab)
    transport = [
        ("Route A - Campus Link", "Ramesh Kumar", "Near Guntur Bus Stand", 15),
        ("Route B - City Express", "Suresh Babu", "Approaching Main Gate", 2),
        ("Route C - Weekend Shuttle", "Venkat Rao", "Parked at Hostel A", 0),
        ("Route D - Station Drop", "Ram Singh", "At Railway Station", 45),
    ]
    c.executemany("INSERT INTO transportation_routes (route_name, driver_name, current_location, eta_minutes) VALUES (?, ?, ?, ?)", transport)

    # 17. Alumni Mentors
    alumni = [
        ("Ravi Teja", "Google", "Software Engineer", 1),
        ("Sita Ram", "Microsoft", "Product Manager", 1),
        ("Arjun Reddy", "Amazon", "Data Scientist", 0),
        ("Priya Sharma", "Atlassian", "Frontend Developer", 1),
        ("Karthik N", "Stripe", "Backend Engineer", 1),
    ]
    c.executemany("INSERT INTO alumni_mentors (name, company, role, available_for_chat) VALUES (?, ?, ?, ?)", alumni)

    # 18. Campus Polls
    polls = [
        ("What should be the theme for TechFest 2026?", json.dumps(["AI Revolution", "Sustainable Future", "Cyber Cosmos", "Retro Gaming"]), 1),
        ("Preferred library extended hours during exams?", json.dumps(["Up to 12 AM", "Up to 2 AM", "24/7", "No change"]), 1),
        ("Which new cuisine should be added to the canteen?", json.dumps(["Mexican", "Italian", "Healthy/Salads", "Street Food"]), 1),
    ]
    c.executemany("INSERT INTO campus_polls (question, options_json, is_active) VALUES (?, ?, ?)", polls)

    # 19. Broadcast Alerts (Circulars)
    alerts = [
        ("Heavy rain expected tomorrow. Transport schedules may be delayed. Plan accordingly.", "warning", 1, delta(0, -2)),
        ("TechFest 2026 registration is now open! Early bird discounts available.", "info", 1, delta(-1)),
        ("Semester fee payment deadline extended to 15th October.", "info", 1, delta(-2)),
        ("Fire drill scheduled for tomorrow 3 PM at N-Block.", "warning", 1, delta(0, -12)),
        ("Emergency: Campus power maintenance from 1 AM to 3 AM tonight.", "emergency", 1, delta(0, -1)),
    ]
    c.executemany("INSERT INTO broadcast_alerts (message, type, is_active, timestamp) VALUES (?, ?, ?, ?)", alerts)

    # 20. Fresher FAQs
    f_faqs = [
        ("FAQ_1", "Orientation", "When does the orientation begin?", "Orientation starts on August 1st at 9:00 AM in the Main Auditorium.", "orientation, dates, start"),
        ("FAQ_2", "Hostel", "What should I pack for the hostel?", "Bring your clothes, toiletries, a lock, bucket, and basic stationery. Mattress is provided.", "hostel, packing, luggage"),
        ("FAQ_3", "Academics", "How to select elective subjects?", "Elective selection portal opens in week 2. Check the circulars tab for the link.", "electives, subjects, choosing"),
    ]
    c.executemany("INSERT INTO fresher_faqs (faq_id, topic, question, answer, keywords) VALUES (?, ?, ?, ?, ?)", f_faqs)

    # 21. Knowledge Procedures (Policies)
    procedures = [
        ("PROC_ID", "Lost ID Card Replacement", "Steps to get a new ID card if lost.", "Fine of ₹500 applies."),
        ("PROC_LEAVE", "Long Leave Application", "How to apply for leave > 3 days.", "Medical certificate required for health reasons."),
    ]
    c.executemany("INSERT INTO knowledge_procedure (procedure_id, title, description, rules) VALUES (?, ?, ?, ?)", procedures)
    
    proc_steps = [
        ("P_ID_1", "PROC_ID", 1, "File an FIR or lost report at the nearest police station or online."),
        ("P_ID_2", "PROC_ID", 2, "Submit the report copy and ₹500 challan at the admin office."),
        ("P_ID_3", "PROC_ID", 3, "Collect your new ID card after 2 working days."),
        ("P_LV_1", "PROC_LEAVE", 1, "Fill the leave form in the Helpdesk Portal."),
        ("P_LV_2", "PROC_LEAVE", 2, "Get it approved by your Faculty Advisor."),
        ("P_LV_3", "PROC_LEAVE", 3, "Submit to HOD for final approval."),
    ]
    c.executemany("INSERT INTO knowledge_procedure_step (step_id, procedure_id, step_order, instruction) VALUES (?, ?, ?, ?)", proc_steps)

    conn.commit()
    print("Successfully seeded mock data for all sidebar tabs!")

if __name__ == "__main__":
    seed()
    conn.close()
