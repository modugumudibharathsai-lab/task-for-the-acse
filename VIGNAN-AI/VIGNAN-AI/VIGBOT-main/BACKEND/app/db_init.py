"""db_init.py - Bootstraps optional Postgres tables and seeds demo data on startup."""
import logging
logger = logging.getLogger(__name__)

def init_postgres_schema():
    from app.database import is_postgres_configured, get_db_connection
    if not is_postgres_configured():
        return
    logger.info("PostgreSQL detected - bootstrapping optional tables...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        _create_tables(cur)
        conn.commit()
        logger.info("Schema bootstrap complete. Seeding demo data...")
        _seed_calendar_events(cur, conn)
        _seed_lost_and_found(cur, conn)
        _seed_facilities(cur, conn)
        _seed_bookings(cur, conn)
        _seed_event_registrations(cur, conn)
        _seed_hostel_requests(cur, conn)
        _seed_marketplace_listings(cur, conn)
        _seed_library_resources(cur, conn)
        _seed_transportation_routes(cur, conn)
        _seed_alumni_mentors(cur, conn)
        _seed_wellness_resources(cur, conn)
        _seed_campus_polls(cur, conn)
        _seed_broadcast_alerts(cur, conn)
        _seed_fresher_faqs(cur, conn)
        _seed_campus_locations(cur, conn)
        _seed_circulars(cur, conn)
        _seed_policies(cur, conn)
        _seed_studentlife_club(cur, conn)
        _seed_studentlife_club_application(cur, conn)
        cur.close()
        conn.close()
        logger.info("Database bootstrap and seed complete.")
    except Exception as e:
        logger.error(f"db_init failed (non-fatal): {e}")

def _create_tables(cur):
    cur.execute("CREATE TABLE IF NOT EXISTS calendar_events (id SERIAL PRIMARY KEY, student_id TEXT, title TEXT, description TEXT, start_time TEXT, end_time TEXT, type TEXT, location TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS lost_and_found (id SERIAL PRIMARY KEY, student_id TEXT, type TEXT, title TEXT, description TEXT, tags TEXT, contact_info TEXT, status TEXT, date_posted TEXT, image_url TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS facilities (id SERIAL PRIMARY KEY, name TEXT, type TEXT, description TEXT, capacity INTEGER, image_url TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS bookings (id SERIAL PRIMARY KEY, facility_id INTEGER, student_id TEXT, date TEXT, start_time TEXT, end_time TEXT, purpose TEXT, status TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS event_registrations (id SERIAL PRIMARY KEY, student_id TEXT, event_name TEXT, qr_code TEXT, status TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS hostel_requests (id SERIAL PRIMARY KEY, student_id TEXT, type TEXT, details TEXT, status TEXT, created_at TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS marketplace_listings (id SERIAL PRIMARY KEY, student_id TEXT, title TEXT, category TEXT, price REAL, status TEXT, created_at TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS library_resources (id SERIAL PRIMARY KEY, title TEXT, course_code TEXT, type TEXT, link TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS transportation_routes (id SERIAL PRIMARY KEY, route_name TEXT, driver_name TEXT, current_location TEXT, eta_minutes INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS alumni_mentors (id SERIAL PRIMARY KEY, name TEXT, company TEXT, role TEXT, available_for_chat INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS wellness_resources (id SERIAL PRIMARY KEY, title TEXT, category TEXT, description TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS campus_polls (id SERIAL PRIMARY KEY, question TEXT, options_json TEXT, is_active INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS broadcast_alerts (id SERIAL PRIMARY KEY, message TEXT, type TEXT, is_active BOOLEAN, timestamp TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS fresher_faqs (faq_id TEXT PRIMARY KEY, topic TEXT, question TEXT, answer TEXT, keywords TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS campus_locations (location_id TEXT PRIMARY KEY, room_number TEXT, block TEXT, floor TEXT, description TEXT, latitude REAL, longitude REAL, features TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS circulars (circular_no TEXT, title TEXT, issued_date TEXT, effective_date TEXT, summary TEXT, issued_by TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS policies (policy_id TEXT, title TEXT, clause_no TEXT, effective_date TEXT, summary TEXT, authority TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS studentlife_club (club_id TEXT PRIMARY KEY, name TEXT, category TEXT, description TEXT, theme_color TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS studentlife_club_application (id SERIAL PRIMARY KEY, club_id TEXT, student_name TEXT, status TEXT, timestamp TIMESTAMP, withdrawal_reason TEXT, student_id TEXT)")
    cur.execute('ALTER TABLE studentlife_club_application ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP')
    cur.execute('ALTER TABLE studentlife_club_application ADD COLUMN IF NOT EXISTS withdrawal_reason TEXT')
    cur.execute('ALTER TABLE studentlife_club_application ADD COLUMN IF NOT EXISTS student_id TEXT')

def _seed_calendar_events(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM calendar_events")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO calendar_events (id,student_id,title,description,start_time,end_time,type,location) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        24,
        "251FA04E13",
        "Mid-Term Exam: OS",
        "Operating Systems Mid-term",
        "2026-09-29T02:20:00.052421",
        "2026-09-29T04:20:00.052421",
        "Academic",
        "Room N-312"
    ],
    [
        25,
        "251FA04E13",
        "AI Club Orientation",
        "Introduction to AI Club",
        "2026-09-21T08:20:00.052421",
        "2026-09-21T10:20:00.052421",
        "Extracurricular",
        "Main Auditorium"
    ],
    [
        26,
        "251FA04E13",
        "Web Dev Workshop",
        "Learn React and Next.js",
        "2026-09-24T06:20:00.052421",
        "2026-09-24T09:20:00.052421",
        "Workshop",
        "Lab 4"
    ],
    [
        27,
        "251FA04E13",
        "Assignment Due: ML",
        "Submit the classification assignment",
        "2026-09-26T16:19:00.052421",
        "2026-09-26T16:19:00.052421",
        "Deadline",
        "Online Portal"
    ],
    [
        28,
        "251FA04E13",
        "Sports Fest 2026",
        "Annual university sports meet",
        "2026-10-04T01:20:00.052421",
        "2026-10-06T10:20:00.052421",
        "Event",
        "Sports Ground"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in calendar_events: {e}")
    conn.commit()
    logger.info("Seeded 5 records in calendar_events.")

def _seed_lost_and_found(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM lost_and_found")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO lost_and_found (id,student_id,type,title,description,tags,contact_info,status,date_posted,image_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        15,
        "251FA04E13",
        "lost",
        "Blue Milton Water Bottle",
        "Lost near the central library seating area.",
        "bottle, blue",
        "251fa04e13@vignan.ac.in",
        "open",
        "2026-09-16T16:20:00.052421",
        "/milton_bottle.png"
    ],
    [
        16,
        "OTHER_STU",
        "found",
        "Scientific Calculator",
        "Found Casio calculator in N-312",
        "calculator",
        "admin@vignan.ac.in",
        "claimed",
        "2026-09-08T16:20:00.052421",
        None
    ],
    [
        17,
        "OTHER_STU",
        "lost",
        "Hostel Keys with Marvel keychain",
        "Lost somewhere near the canteen",
        "keys, marvel",
        "other@vignan.ac.in",
        "open",
        "2026-09-18T04:20:00.052421",
        "/captain_america_key.jpg"
    ],
    [
        18,
        "251FA04E13",
        "found",
        "Apple AirPods Pro",
        "Found in AI Lab near the window seats",
        "airpods, apple",
        "251fa04e13@vignan.ac.in",
        "open",
        "2026-09-18T14:20:00.052421",
        None
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in lost_and_found: {e}")
    conn.commit()
    logger.info("Seeded 4 records in lost_and_found.")

def _seed_facilities(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM facilities")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO facilities (id,name,type,description,capacity,image_url) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        1,
        "Badminton Court 1",
        "Sports",
        "Indoor synthetic court with proper lighting",
        4,
        "/badminton_court_1.jpg"
    ],
    [
        2,
        "Study Room A",
        "Academic",
        "Quiet study room with whiteboards and AC",
        6,
        "/study_room_a.jpg"
    ],
    [
        3,
        "Basketball Court",
        "Sports",
        "Outdoor cement court",
        10,
        "/basketball_court.jpg"
    ],
    [
        4,
        "Music Room",
        "Extracurricular",
        "Soundproof room with drumkit and keyboards",
        8,
        "/music_room.jpg"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in facilities: {e}")
    conn.commit()
    logger.info("Seeded 4 records in facilities.")

def _seed_bookings(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM bookings")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO bookings (id,facility_id,student_id,date,start_time,end_time,purpose,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        11,
        1,
        "251FA04E13",
        "2026-09-19",
        "17:00",
        "18:00",
        "Practice match",
        "confirmed"
    ],
    [
        12,
        2,
        "251FA04E13",
        "2026-09-20",
        "14:00",
        "16:00",
        "Group study for mid-terms",
        "confirmed"
    ],
    [
        13,
        4,
        "OTHER_STU",
        "2026-09-19",
        "16:00",
        "17:00",
        "Band practice",
        "confirmed"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in bookings: {e}")
    conn.commit()
    logger.info("Seeded 3 records in bookings.")

def _seed_event_registrations(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM event_registrations")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO event_registrations (id,student_id,event_name,qr_code,status) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        8,
        "251FA04E13",
        "TechFest 2026",
        "QR_TF2026_12345",
        "Registered"
    ],
    [
        9,
        "251FA04E13",
        "AI Hackathon",
        "QR_AIHACK_888",
        "Checked In"
    ],
    [
        10,
        "251FA04E13",
        "Career Fair",
        "QR_CAREER_999",
        "Registered"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in event_registrations: {e}")
    conn.commit()
    logger.info("Seeded 3 records in event_registrations.")

def _seed_hostel_requests(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM hostel_requests")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO hostel_requests (id,student_id,type,details,status,created_at) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        10,
        "251FA04E13",
        "Maintenance",
        "Fan regulator is broken in Room 204",
        "Open",
        "2026-09-17T16:20:00.052421"
    ],
    [
        11,
        "251FA04E13",
        "GatePass",
        "Visiting home for the weekend",
        "Approved",
        "2026-09-13T16:20:00.052421"
    ],
    [
        12,
        "251FA04E13",
        "Cleaning",
        "Requesting room cleaning, lots of dust.",
        "Resolved",
        "2026-09-08T16:20:00.052421"
    ],
    [
        13,
        "251FA04E13",
        "Mess",
        "Quality of dinner on Tuesday was poor.",
        "Pending",
        "2026-09-16T16:20:00.052421"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in hostel_requests: {e}")
    conn.commit()
    logger.info("Seeded 4 records in hostel_requests.")

def _seed_marketplace_listings(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM marketplace_listings")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO marketplace_listings (id,student_id,title,category,price,status,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        13,
        "251FA04E13",
        "Engineering Mathematics Book",
        "Books",
        250.0,
        "Available",
        "2026-09-16T16:20:00.052421"
    ],
    [
        14,
        "251FA04E13",
        "Scientific Calculator Casio 991EX",
        "Electronics",
        800.0,
        "Sold",
        "2026-09-08T16:20:00.052421"
    ],
    [
        15,
        "OTHER_STU",
        "Drafting Table",
        "Stationery",
        450.0,
        "Available",
        "2026-09-13T16:20:00.052421"
    ],
    [
        16,
        "OTHER_STU",
        "Arduino Starter Kit",
        "Electronics",
        1200.0,
        "Available",
        "2026-09-17T16:20:00.052421"
    ],
    [
        17,
        "251FA04E13",
        "Lab Coat (Size M)",
        "Clothing",
        200.0,
        "Available",
        "2026-09-18T11:20:00.052421"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in marketplace_listings: {e}")
    conn.commit()
    logger.info("Seeded 5 records in marketplace_listings.")

def _seed_library_resources(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM library_resources")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO library_resources (id,title,course_code,type,link) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        18,
        "Introduction to Algorithms",
        "CS201",
        "Book",
        "https://library.vignan.ac.in/books/algo"
    ],
    [
        19,
        "Machine Learning Basics",
        "CS305",
        "Research Paper",
        "https://library.vignan.ac.in/papers/ml"
    ],
    [
        20,
        "React Design Patterns",
        "CS402",
        "Video Course",
        "https://library.vignan.ac.in/videos/react"
    ],
    [
        21,
        "Data Structures and Algorithms in Java",
        "CS202",
        "Book",
        "https://library.vignan.ac.in/books/ds"
    ],
    [
        22,
        "Computer Networks",
        "CS301",
        "Book",
        "https://library.vignan.ac.in/books/cn"
    ],
    [
        23,
        "Deep Learning with Python",
        "CS405",
        "Book",
        "https://library.vignan.ac.in/books/dl"
    ],
    [
        24,
        "Artificial Intelligence: A Modern Approach",
        "CS401",
        "Book",
        "https://library.vignan.ac.in/books/ai"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in library_resources: {e}")
    conn.commit()
    logger.info("Seeded 7 records in library_resources.")

def _seed_transportation_routes(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM transportation_routes")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO transportation_routes (id,route_name,driver_name,current_location,eta_minutes) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        11,
        "Route A - Campus Link",
        "Ramesh Kumar",
        "Near Guntur Bus Stand",
        15
    ],
    [
        12,
        "Route B - City Express",
        "Suresh Babu",
        "Approaching Main Gate",
        2
    ],
    [
        13,
        "Route C - Weekend Shuttle",
        "Venkat Rao",
        "Parked at Hostel A",
        0
    ],
    [
        14,
        "Route D - Station Drop",
        "Ram Singh",
        "At Railway Station",
        45
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in transportation_routes: {e}")
    conn.commit()
    logger.info("Seeded 4 records in transportation_routes.")

def _seed_alumni_mentors(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM alumni_mentors")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO alumni_mentors (id,name,company,role,available_for_chat) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        14,
        "Ravi Teja",
        "Google",
        "Software Engineer",
        1
    ],
    [
        15,
        "Sita Ram",
        "Microsoft",
        "Product Manager",
        1
    ],
    [
        16,
        "Arjun Reddy",
        "Amazon",
        "Data Scientist",
        0
    ],
    [
        17,
        "Priya Sharma",
        "Atlassian",
        "Frontend Developer",
        1
    ],
    [
        18,
        "Karthik N",
        "Stripe",
        "Backend Engineer",
        1
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in alumni_mentors: {e}")
    conn.commit()
    logger.info("Seeded 5 records in alumni_mentors.")

def _seed_wellness_resources(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM wellness_resources")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO wellness_resources (id,title,category,description) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        14,
        "Managing Exam Stress",
        "Mental Health",
        "Techniques and deep breathing exercises to handle exam pressure effectively."
    ],
    [
        15,
        "Campus Counseling Center",
        "Support",
        "Reach out to our trained counselors available 24/7 at +91 9876543210."
    ],
    [
        16,
        "Morning Yoga Sessions",
        "Physical Wellbeing",
        "Join the morning yoga sessions at the sports complex every Mon-Wed-Fri 6 AM."
    ],
    [
        17,
        "Sleep Hygiene Guide",
        "Lifestyle",
        "Learn how to improve your sleep cycle for better academic performance."
    ],
    [
        18,
        "Peer Support Group",
        "Community",
        "A safe space to discuss personal challenges with trusted peers every Thursday."
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in wellness_resources: {e}")
    conn.commit()
    logger.info("Seeded 5 records in wellness_resources.")

def _seed_campus_polls(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM campus_polls")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO campus_polls (id,question,options_json,is_active) VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        9,
        "What should be the theme for TechFest 2026?",
        "[\"AI Revolution\", \"Sustainable Future\", \"Cyber Cosmos\", \"Retro Gaming\"]",
        1
    ],
    [
        10,
        "Preferred library extended hours during exams?",
        "[\"Up to 12 AM\", \"Up to 2 AM\", \"24/7\", \"No change\"]",
        1
    ],
    [
        11,
        "Which new cuisine should be added to the canteen?",
        "[\"Mexican\", \"Italian\", \"Healthy/Salads\", \"Street Food\"]",
        1
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in campus_polls: {e}")
    conn.commit()
    logger.info("Seeded 3 records in campus_polls.")

def _seed_broadcast_alerts(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM broadcast_alerts")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO broadcast_alerts (id,message,type,is_active,timestamp) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        15,
        "Heavy rain expected tomorrow. Transport schedules may be delayed. Plan accordingly.",
        "warning",
        True,
        "2026-09-18T14:20:00.052421"
    ],
    [
        16,
        "TechFest 2026 registration is now open! Early bird discounts available.",
        "info",
        True,
        "2026-09-17T16:20:00.052421"
    ],
    [
        17,
        "Semester fee payment deadline extended to 15th October.",
        "info",
        True,
        "2026-09-16T16:20:00.052421"
    ],
    [
        18,
        "Fire drill scheduled for tomorrow 3 PM at N-Block.",
        "warning",
        True,
        "2026-09-18T04:20:00.052421"
    ],
    [
        19,
        "Emergency: Campus power maintenance from 1 AM to 3 AM tonight.",
        "emergency",
        True,
        "2026-09-18T15:20:00.052421"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in broadcast_alerts: {e}")
    conn.commit()
    logger.info("Seeded 5 records in broadcast_alerts.")

def _seed_fresher_faqs(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM fresher_faqs")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO fresher_faqs (faq_id,topic,question,answer,keywords) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (faq_id) DO NOTHING""".strip()
    rows = [
    [
        "FAQ_1",
        "Orientation",
        "When does the orientation begin?",
        "Orientation starts on August 1st at 9:00 AM in the Main Auditorium.",
        "orientation, dates, start"
    ],
    [
        "FAQ_2",
        "Hostel",
        "What should I pack for the hostel?",
        "Bring your clothes, toiletries, a lock, bucket, and basic stationery. Mattress is provided.",
        "hostel, packing, luggage"
    ],
    [
        "FAQ_3",
        "Academics",
        "How to select elective subjects?",
        "Elective selection portal opens in week 2. Check the circulars tab for the link.",
        "electives, subjects, choosing"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in fresher_faqs: {e}")
    conn.commit()
    logger.info("Seeded 3 records in fresher_faqs.")

def _seed_campus_locations(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM campus_locations")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO campus_locations (location_id,room_number,block,floor,description,latitude,longitude,features) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (location_id) DO NOTHING""".strip()
    rows = [
    [
        "loc-u1",
        "U-101",
        "U Block",
        "Ground Floor",
        "U Block Lecture Hall",
        None,
        None,
        None
    ],
    [
        "loc-a1",
        "A-101",
        "A Block",
        "Ground Floor",
        "A Block Lecture Hall",
        None,
        None,
        None
    ],
    [
        "loc-h1",
        "H-101",
        "H Block",
        "Ground Floor",
        "H Block Boys Hostel",
        None,
        None,
        None
    ],
    [
        "loc-n1",
        "N-101",
        "N Block",
        "Ground Floor",
        "N Block CSE Dept",
        None,
        None,
        None
    ],
    [
        "loc-p1",
        "P-101",
        "P Block",
        "Ground Floor",
        "P Block ECE Dept",
        None,
        None,
        None
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in campus_locations: {e}")
    conn.commit()
    logger.info("Seeded 5 records in campus_locations.")

def _seed_circulars(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM circulars")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO circulars (circular_no,title,issued_date,effective_date,summary,issued_by) VALUES (%s,%s,%s,%s,%s,%s) """.strip()
    rows = [
    [
        "VFSTR/AAA/2026/AC-01",
        "B.Tech Academic Calendar 2026-27 (Semester-I)",
        "2026-06-01",
        "2026-07-10",
        "Official B.Tech Academic Calendar (Semester-I, 2026-27) for 2nd (R25), 3rd (R22C24) & 4th (R22) Year. Module-1 commenced on 10-Jul-2026. Module-2 commenced on 08-Sep-2026. M-2 FA-1 is scheduled for 06-Oct to 08-Oct-2026. Dasara vacation runs from 18-Oct to 21-Oct-2026. M-2 FA-2 is from 11-Nov to 13-Nov-2026. Preparation & Practical Summative Assessment is from 14-Nov to 20-Nov-2026. Summative Assessment (Theory End Semester) runs from 21-Nov to 04-Dec-2026. Semester-II commences on 14-Dec-2026.",
        "Dean-AAA & FA, VFSTR Vadlamudi"
    ],
    [
        "ACME/REG/2026/089",
        "Schedule for Second Continuous Internal Evaluation (CIE-2)",
        "2026-09-05",
        "2026-10-14",
        "CIE-2 for all UG Semesters 3 and 5 will be conducted from October 14, 2026 to October 21, 2026. Hall tickets will be issued through student portal from Oct 10.",
        "Registrar Academic Affairs"
    ],
    [
        "ACME/FIN/2026/041",
        "Second Installment Tuition Fee Payment Notification",
        "2026-09-01",
        "2026-10-31",
        "Last date to pay second installment of academic fees without fine is October 31, 2026. Online gateway available at bursar portal.",
        "Finance Bursar"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in circulars: {e}")
    conn.commit()
    logger.info("Seeded 3 records in circulars.")

def _seed_policies(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM policies")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO policies (policy_id,title,clause_no,effective_date,summary,authority) VALUES (%s,%s,%s,%s,%s,%s) """.strip()
    rows = [
    [
        "pol-01",
        "Academic Regulation R23 - Attendance & Promotion Norms",
        "Clause 4.2",
        "2023-07-15",
        "Every student must maintain minimum 75% attendance in each registered subject. Condonation up to 10% (between 65% and 75%) is permitted strictly on medical grounds verified by the college medical officer with valid hospitalization certificates.",
        "Academic Senate Resolution 23/12"
    ],
    [
        "pol-02",
        "Examination Code of Conduct and Evaluation Scheme",
        "Clause 7.1",
        "2023-07-15",
        "Continuous Internal Evaluation (CIE) carries 40% weightage, and Semester End Examination (SEE) carries 60% weightage. To qualify for a pass grade, students must score at least 35% in SEE and 40% aggregate.",
        "Controller of Examinations By-Laws"
    ],
    [
        "pol-03",
        "Institutional Grievance Redressal and Anti-Harassment Regulations",
        "Clause 2.1 - Statutory Triage",
        "2022-09-01",
        "Grievances relating to ragging, harassment, or discrimination bypass regular departmental triage and go directly to the Statutory Internal Complaints Committee with a mandatory 48-hour response window.",
        "Statutory Governance Committee"
    ],
    [
        "POL-AD47CB2D",
        "Academic & Classroom Policies - Attendance Mandates",
        "AC-01",
        "2026-08-01",
        "Students must maintain a minimum of 75% mandatory attendance per semester to sit for final examinations. Condonation for shortages between 65% and 75% is permitted strictly on valid medical grounds with Dean approval, but any attendance below 65% results in debarment from exams and withheld promotion.",
        "Dean of Academics"
    ],
    [
        "POL-AE0FE941",
        "Academic & Classroom Policies - Classroom Etiquette",
        "AC-02",
        "2026-08-01",
        "Students must assemble in classrooms within five minutes of the scheduled start time. They are required to rise when a teacher enters and remain standing until permitted to sit.",
        "Dean of Academics"
    ],
    [
        "POL-A6B353C1",
        "Academic & Classroom Policies - Transitions",
        "AC-03",
        "2026-08-01",
        "Moving between classrooms must be done silently to avoid disrupting other active sessions. Students must vacate common areas, like the canteen, at least five minutes prior to the start of their classes.",
        "Dean of Academics"
    ],
    [
        "POL-53A9F958",
        "Campus Discipline & Prohibited Conduct - Mobile Phones",
        "CD-01",
        "2026-08-01",
        "Device usage is strictly prohibited during academic hours, in the Library, Computer Centre, and Examination Halls. Confiscated phones will only be returned after the completion of the student's entire coursework.",
        "Discipline Committee"
    ],
    [
        "POL-E2521623",
        "Campus Discipline & Prohibited Conduct - Restricted Areas & Loitering",
        "CD-02",
        "2026-08-01",
        "Students must not sit on corridor walls, parapets, stairs, or footpaths, nor crowd in front of offices or on campus roads. During free time, they are expected to utilize the library or internet facilities rather than loitering.",
        "Discipline Committee"
    ],
    [
        "POL-73D38634",
        "Campus Discipline & Prohibited Conduct - Prohibited Items & Activities",
        "CD-03",
        "2026-08-01",
        "The campus bans the possession of weapons, explosives, firecrackers, alcohol, drugs, and tobacco products. Involvement in illegal financial activities, such as betting or money laundering, is strictly forbidden.",
        "Discipline Committee"
    ],
    [
        "POL-08B5E33A",
        "Campus Discipline & Prohibited Conduct - Vehicular Rules",
        "CD-04",
        "2026-08-01",
        "Student vehicles must be parked in earmarked locations, and driving or moving vehicles around the inner campus is restricted to prevent noise pollution.",
        "Discipline Committee"
    ],
    [
        "POL-FB1A4189",
        "Campus Discipline & Prohibited Conduct - Zero Tolerance for Ragging",
        "CD-05",
        "2026-08-01",
        "Ragging in any form, on or off campus, is strictly prohibited and punishable under Ragging Act 26 of 1997. Abusing or criticizing girl students with foul language is also explicitly banned.",
        "Anti-Ragging Committee"
    ],
    [
        "POL-874FF266",
        "Infrastructure Guidelines - Library",
        "IG-01",
        "2026-08-01",
        "Access & Documentation: Sign the logbook upon entry and exit; deposit bags at the counter; leave footwear on outside stands. Operational Rules: Phones must be switched off or on silent; the digital section is exclusively for accessing online technical journals; resting/sleeping is prohibited.",
        "Chief Librarian"
    ],
    [
        "POL-3DDE10C6",
        "Infrastructure Guidelines - Laboratories",
        "IG-02",
        "2026-08-01",
        "Access & Documentation: Sign the register and hand over equipment to the Lab Assistant before leaving; after-hours access requires HOD permission. Operational Rules: Aprons or overcoats are mandatory where applicable; equipment must be shared equally; manuals must be read prior to handling mechanical/electrical tools.",
        "Lab In-Charge"
    ],
    [
        "POL-7C415F42",
        "Hostel & Dining Regulations - Curfew & Movement",
        "HD-01",
        "2026-08-01",
        "Residents must report to the hostel before 6 p.m., or inform the administration and log their purpose in the Movement Register if returning later. Going out or staying out after 10 p.m. is not allowed.",
        "Chief Warden"
    ],
    [
        "POL-27A76841",
        "Hostel & Dining Regulations - Leaves of Absence",
        "HD-02",
        "2026-08-01",
        "Leaving the station requires written permission applied for two days in advance. If a resident leaves without intimation, the Chief Warden has the right to break the room lock without liability for lost items.",
        "Chief Warden"
    ],
    [
        "POL-D85C1C27",
        "Hostel & Dining Regulations - Visitors",
        "HD-03",
        "2026-08-01",
        "Parents and local guardians are only permitted to visit on Saturdays and Sundays between 4 p.m. and 6 p.m.. Non-boarders/guests are strictly banned from entering resident rooms.",
        "Chief Warden"
    ],
    [
        "POL-6D92A932",
        "Hostel & Dining Regulations - Room Restrictions",
        "HD-04",
        "2026-08-01",
        "Students should not keep valuables or cash exceeding Rs. 1000 in their rooms. Electrical stoves, immersion heaters, and iron boxes are strictly prohibited to prevent short circuits and fire hazards.",
        "Chief Warden"
    ],
    [
        "POL-FF715892",
        "Hostel & Dining Regulations - Dining Protocol",
        "HD-05",
        "2026-08-01",
        "All hostellers must dine in the mess during notified timings; outside cooked food is banned. Food and utensils cannot be taken out of the dining hall, and students are prohibited from entering the kitchen or store areas.",
        "Mess Warden"
    ],
    [
        "POL-72B95AFD",
        "Hostel & Dining Regulations - Services",
        "HD-06",
        "2026-08-01",
        "Residents must not use hostel staff for personal errands. In case of sickness, students must report immediately to the Warden, who must approve any requests for room service.",
        "Chief Warden"
    ],
    [
        "POL-574BF444",
        "Extracurriculars: Sports & Youth Fests - Sports Facilities",
        "EX-01",
        "2026-08-01",
        "Indoor games and equipment can be accessed between 3:00 p.m. and 6:30 p.m. by producing an ID card to the Physical Director. Tennis tables and cricket pitches are allotted on a first-come, first-served basis. All equipment must be returned by 6:30 p.m..",
        "Physical Director"
    ],
    [
        "POL-0505D6C6",
        "Extracurriculars: Sports & Youth Fests - Event Conduct",
        "EX-02",
        "2026-08-01",
        "During National level events (e.g., Vignan Mahotsav), students must not form narrow groups based on discipline, community, or region. Heckling performers, teasing, or violent behavior will lead to direct accountability with the discipline committee.",
        "Event Coordinator"
    ],
    [
        "POL-4D5D6310",
        "Grievance Redressal & Punitive Actions - Grievance Redressal",
        "GR-01",
        "2026-08-01",
        "All complaints must be submitted in writing to the respective Head of Department (HOD). If a student wishes to address the Dean, it must still be routed through this proper channel. Non-academic grievances can be routed to specialized committees, including the Anti-Ragging Committee, Women Protection Cell, or Canteen Committee.",
        "Grievance Redressal Committee"
    ],
    [
        "POL-BC50A0A2",
        "Grievance Redressal & Punitive Actions - Punitive Actions",
        "GR-02",
        "2026-08-01",
        "Violations of any policies within the Code of Conduct are assessed by the disciplinary committee and may result in: Fine with a formal warning. Fine coupled with suspension. Rustication for an entire semester. Permanent expulsion from the college.",
        "Disciplinary Committee"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in policies: {e}")
    conn.commit()
    logger.info("Seeded 23 records in policies.")

def _seed_studentlife_club(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM studentlife_club")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO studentlife_club (club_id,name,category,description,theme_color) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (club_id) DO NOTHING""".strip()
    rows = [
    [
        "CLUB_AI",
        "AI Innovation Club",
        "Technical",
        "Exploring Artificial Intelligence, Machine Learning and Robotics",
        "indigo"
    ],
    [
        "CLUB_MUSIC",
        "Symphony Music Club",
        "Cultural",
        "For the love of music, bands and vocalists",
        "rose"
    ],
    [
        "CLUB_SPORTS",
        "Athletics & Sports",
        "Sports",
        "Organizing tournaments and fitness bootcamps",
        "emerald"
    ],
    [
        "CLUB_CODE",
        "Competitive Programming",
        "Technical",
        "Crack FAANG interviews and algorithms",
        "amber"
    ],
    [
        "CLUB_DRAMA",
        "Theatrix",
        "Cultural",
        "Stage plays, acting and scriptwriting",
        "purple"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in studentlife_club: {e}")
    conn.commit()
    logger.info("Seeded 5 records in studentlife_club.")

def _seed_studentlife_club_application(cur, conn):
    cur.execute("SELECT COUNT(*) as cnt FROM studentlife_club_application")
    row = cur.fetchone()
    count = row.get("cnt", 0) if hasattr(row, "get") else (row[0] if row else 0)
    if count > 0:
        return
    sql = """INSERT INTO studentlife_club_application (id,club_id,student_name,status,timestamp,withdrawal_reason,student_id) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""".strip()
    rows = [
    [
        6,
        "CLUB_MUSIC",
        "VIGBOT",
        "Pending",
        "2026-09-17T16:20:00.052421",
        None,
        "251FA04E13"
    ],
    [
        7,
        "CLUB_DRAMA",
        "Other Student",
        "Pending",
        "2026-09-16T16:20:00.052421",
        None,
        "OTHER_STU"
    ]
]
    for r in rows:
        try:
            cur.execute(sql, r)
        except Exception as e:
            logger.warning(f"Failed to seed row in studentlife_club_application: {e}")
    conn.commit()
    logger.info("Seeded 2 records in studentlife_club_application.")
