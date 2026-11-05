import os
import sys
import uuid
import sqlite3

def get_db_connection():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Create the table if it does not exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fresher_faqs (
            faq_id TEXT PRIMARY KEY,
            topic TEXT,
            question TEXT,
            answer TEXT,
            keywords TEXT
        )
    """)
    conn.commit()
    return conn

def seed_comprehensive_faqs():
    conn = get_db_connection()

    faqs = [
        # Campus Navigation & Facilities
        {
            "topic": "Campus Navigation",
            "question": "Where is the main academic block for first-year classes?",
            "answer": "The main academic block for first-year classes is the Vignan Block (also known as H-Block). It houses all the fundamental science and humanities classrooms.",
            "keywords": "first-year classes, academic block, main block, H-Block, Vignan Block"
        },
        {
            "topic": "Campus Navigation",
            "question": "Which floor is classroom Place or lecture hall Place located on?",
            "answer": "Generally, 100-series rooms are on the Ground Floor, 200-series on the 1st Floor, 300-series on the 2nd Floor, and so on. For example, Room H-204 is on the 2nd Floor of H-Block.",
            "keywords": "floor, classroom, lecture hall, room number"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where is the nearest ATM or bank branch on campus?",
            "answer": "The UCO Bank branch and a 24/7 ATM are located near the Main Gate of the campus, adjacent to the administrative A-Block.",
            "keywords": "ATM, bank, money, cash"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where can I get photocopies, document printing, and stationery?",
            "answer": "There are print out copy shops and a canteen on the ground floor of each block. The main stationery shop and reprography (photocopy/printing) center is located on the Ground Floor of the A-Block.",
            "keywords": "photocopies, print, printing, stationery, xerox, copy shops"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where is the main canteen and where can I buy day-to-day items?",
            "answer": "There is a big canteen named MHP where you can eat during break times. Just beside it is Zest, a utility store where you can buy day-to-day life things. Also, there are smaller canteens on the ground floor of each block.",
            "keywords": "canteen, food, MHP, Zest, daily items, groceries, eat, break"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where is the campus lost-and-found desk located?",
            "answer": "The lost-and-found desk is managed by the Chief Security Officer's cabin at the Main Gate. You can also check with the A-Block reception.",
            "keywords": "lost, found, missing, desk"
        },
        {
            "topic": "Campus Navigation",
            "question": "Which gate should I use for auto-rickshaws, cabs, or visitor entry?",
            "answer": "All auto-rickshaws, cabs (Uber/Ola), and general visitors must use Gate No. 1 (Main Gate) for entry and security clearance. Gate No. 2 is strictly for university buses and staff vehicles.",
            "keywords": "gate, auto, rickshaw, cab, uber, ola, visitor"
        },
        {
            "topic": "Campus Navigation",
            "question": "Where is the administrative office or Dean of Student Affairs' cabin?",
            "answer": "The Dean of Student Affairs and the main administrative offices are located on the 1st Floor of the A-Block (Admin Block).",
            "keywords": "administrative office, Dean of Student Affairs, cabin, admin"
        },
        {
            "topic": "Rules",
            "question": "Are first-year students allowed to park two-wheelers or bicycles on campus?",
            "answer": "First-year students residing in hostels are generally not allowed to keep powered two-wheelers. Bicycles are permitted. Day scholars can park their two-wheelers in the designated student parking area near Gate No. 1 after obtaining a parking sticker.",
            "keywords": "park, two-wheeler, bicycle, bike, scooter, parking"
        },
        {
            "topic": "Campus Navigation",
            "question": "Where are the departmental labs for physics, chemistry, and computer science?",
            "answer": "Physics and Chemistry labs are on the Ground and 1st floors of the Vignan (H) Block. Computer Science labs (IT Centers) are primarily located in the N-Block. In front of N block is the Vignan Vihar Boys hostel.",
            "keywords": "labs, physics, chemistry, computer science, laboratory, N block, Vignan Vihar"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where is the post office or courier collection point?",
            "answer": "The campus post office is situated near the UCO Bank branch at the Main Gate. Courier packages for hostellers are delivered to the respective hostel warden's office.",
            "keywords": "post office, courier, mail, package, amazon, flipkart"
        },
        {
            "topic": "Campus Navigation",
            "question": "How do I find the main auditorium and seminar halls?",
            "answer": "The Main Auditorium (Sangamam) is located centrally behind the A-Block. Individual seminar halls (like Spoorthi and Srujana) are located in the A-Block and H-Block.",
            "keywords": "auditorium, seminar hall, events, Sangamam"
        },
        {
            "topic": "Campus Facilities",
            "question": "Where can I find water dispensers and clean restrooms near my lecture block?",
            "answer": "RO water dispensers and restrooms are located at the end of the corridors on every floor of all academic blocks.",
            "keywords": "water, dispenser, restroom, toilet, washroom, drinking water"
        },
        # Academics, Timetable & Attendance
        {
            "topic": "Academics",
            "question": "Where can I find my official weekly class timetable and section division?",
            "answer": "Your official timetable and section division are available on the student ERP portal (vignan.ac.in/erp) under the 'Academics' tab. They are also posted on your department's physical notice board.",
            "keywords": "timetable, section, schedule, classes"
        },
        {
            "topic": "Academics",
            "question": "What is the minimum attendance percentage required to sit for semester exams?",
            "answer": "As per academic regulations (Clause 4.2), a minimum of 75% overall attendance is required to be eligible to write the end-semester examinations. Condonation up to 65% is only granted for valid medical reasons with Dean approval.",
            "keywords": "attendance, minimum, exams, semester, condonation"
        },
        {
            "topic": "Academics",
            "question": "What is the procedure if a teacher accidentally marks me absent?",
            "answer": "If you are marked absent by mistake, immediately approach the concerned faculty member within 24 hours to get it rectified. You can also inform your class teacher or mentor.",
            "keywords": "absent, mistake, marked absent, attendance correction"
        },
        {
            "topic": "Academics",
            "question": "How do I apply for official duty leave (OD) or medical leave?",
            "answer": "For OD (sports, fests, hackathons), submit an OD form signed by the event coordinator to your HOD. For medical leave, submit a leave letter with a valid medical certificate to your class mentor immediately upon your return.",
            "keywords": "leave, OD, official duty, medical leave, sick leave"
        },
        {
            "topic": "Academics",
            "question": "Who is my assigned faculty mentor or proctor, and where is their cabin?",
            "answer": "Your faculty mentor is assigned by your department. You can check their name and cabin details on your ERP dashboard under 'My Profile'. They are usually located in your department's staff rooms.",
            "keywords": "mentor, proctor, cabin, advisor, faculty mentor"
        },
        {
            "topic": "Academics",
            "question": "Where can I view the academic calendar with exam dates and holidays?",
            "answer": "The academic calendar is published at the start of the semester and can be downloaded from the university website's academic section and the student ERP portal.",
            "keywords": "academic calendar, exam dates, holidays, schedule"
        },
        {
            "topic": "Academics",
            "question": "How are internal assessment marks, assignments, and mid-term exams weighted?",
            "answer": "Typically, internal evaluation carries 40% weightage (comprising mid-term exams, quizzes, and assignments), while the end-semester exam carries 60% weightage. Check your specific course syllabus for exact breakdowns.",
            "keywords": "internal marks, assessment, mid-term, weightage, assignments"
        },
        {
            "topic": "Academics",
            "question": "Are physical textbooks mandatory, or are lecture slides and PDF notes sufficient?",
            "answer": "While faculty provide slides and notes, referring to standard textbooks (available in the library) is highly recommended for deep understanding and scoring well in exams. Faculty will specify if a textbook is absolutely mandatory.",
            "keywords": "textbooks, slides, notes, pdf, reading"
        },
        {
            "topic": "Academics",
            "question": "What happens if I miss an internal test or practical lab due to illness?",
            "answer": "If you miss an internal test or lab due to severe illness, you must submit a medical certificate to your HOD and request a re-test. Approval is at the discretion of the department head.",
            "keywords": "missed test, internal, lab, illness, sick, re-test"
        },
        {
            "topic": "Academics",
            "question": "How do open electives, minor degrees, and honors tracks work?",
            "answer": "Open electives allow you to study subjects outside your major. Minor degrees and Honors tracks require taking additional credits starting from your 2nd or 3rd year. Eligibility usually requires maintaining a high CGPA (e.g., above 8.0).",
            "keywords": "open elective, minor degree, honors, extra credits"
        },
        {
            "topic": "Academics",
            "question": "When and where are lab observation notebooks and record sheets submitted?",
            "answer": "Observation notebooks must be signed during the lab session. Final record sheets are usually submitted during the next week's lab session directly to the lab instructor.",
            "keywords": "lab, observation, record, submission, notebook"
        },
        {
            "topic": "Academics",
            "question": "How do I contact a course professor outside class hours?",
            "answer": "You can contact professors during their official office hours (listed outside their cabins), via their official university email, or by leaving a message with the department clerk.",
            "keywords": "contact professor, office hours, email faculty"
        },
        {
            "topic": "Academics",
            "question": "How is the semester grade point average (SGPA) and cumulative GPA (CGPA) calculated?",
            "answer": "SGPA is calculated by dividing the total credit points earned in a semester by the total credits registered. CGPA is the weighted average of all SGPA across completed semesters. Grades range from O (10 points) to F (0 points).",
            "keywords": "SGPA, CGPA, calculate GPA, grades"
        },
        {
            "topic": "Academics",
            "question": "What is the process for grade re-evaluation or answer script verification?",
            "answer": "After results are declared, the exam cell issues a notification for re-evaluation. You must apply through the ERP portal and pay the stipulated fee within the given deadline (usually one week).",
            "keywords": "re-evaluation, answer script, verification, check paper, recounting"
        },
        # Hostel Life & Room Maintenance
        {
            "topic": "Hostel Life",
            "question": "Whom do I contact if the fan, light, or electrical socket in my room stops working?",
            "answer": "You need to log a maintenance request in the hostel register kept with the block warden or security guard. Electricians and plumbers attend to issues daily between 10 AM and 5 PM.",
            "keywords": "fan, light, socket, electrical, repair, maintenance"
        },
        {
            "topic": "Hostel Life",
            "question": "What are the official hostel curfew hours on weekdays and weekends?",
            "answer": "The general hostel curfew is 8:30 PM for girls and 9:00 PM for boys. Students must be inside the hostel premises by this time. Biometric attendance is taken daily.",
            "keywords": "curfew, hostel timings, late entry, biometric"
        },
        {
            "topic": "Hostel Life",
            "question": "How do I apply for a weekend out-pass or home leave?",
            "answer": "You must apply for an out-pass via the ERP portal or a physical form at least 24 hours in advance. It requires approval from your mentor, HOD, and the Chief Warden. A confirmation message is sent to your parents.",
            "keywords": "out-pass, home leave, weekend pass, leave hostel"
        },
        {
            "topic": "Hostel Life",
            "question": "Are electric kettles, irons, or hair dryers permitted in hostel rooms?",
            "answer": "High-power electrical appliances like kettles, irons, induction stoves, and immersion rods are strictly prohibited in rooms due to fire safety rules. Ironing rooms are provided separately.",
            "keywords": "kettle, iron, hair dryer, appliances, forbidden"
        },
        {
            "topic": "Hostel Life",
            "question": "How does the laundry service operate, and what are the drop-off and pickup days?",
            "answer": "Laundry service operates twice a week. You must drop off your clothes at the designated laundry counter in your block in the morning. Washed and ironed clothes are usually returned in 2-3 days.",
            "keywords": "laundry, washing clothes, dhobi"
        },
        {
            "topic": "Hostel Life",
            "question": "What is the weekly cleaning schedule for rooms and shared washrooms?",
            "answer": "Shared washrooms are cleaned twice daily. Room cleaning is done every alternate day; you must be present in the room or leave your key with the warden if you want it cleaned.",
            "keywords": "cleaning, sweep, mop, washroom, housekeeping"
        },
        {
            "topic": "Hostel Life",
            "question": "Can parents or day-scholar friends visit my hostel room?",
            "answer": "Day-scholar friends are strictly not allowed inside the hostel blocks. Parents/guardians can visit you in the hostel visitor's lounge but are generally not permitted inside student rooms without warden permission.",
            "keywords": "parents visit, day-scholar, friends, visitor lounge"
        },
        {
            "topic": "Hostel Life",
            "question": "Whom should I alert if my roommate falls sick in the middle of the night?",
            "answer": "Immediately alert the block warden or the night security guard. They will arrange for the campus ambulance to take the student to the campus health center.",
            "keywords": "roommate sick, night emergency, medical emergency"
        },
        {
            "topic": "Hostel Life",
            "question": "What is the procedure to request a room or roommate change?",
            "answer": "Room change requests are entertained only at the end of the semester or under exceptional circumstances. You must submit a written request to the Chief Warden explaining the reason.",
            "keywords": "room change, roommate change, swap room"
        },
        {
            "topic": "Hostel Life",
            "question": "Where can students hang wet clothes to dry?",
            "answer": "Designated drying lines are available on the terrace and in the balconies of the hostel blocks. Hanging wet clothes inside rooms or on corridor railings is discouraged.",
            "keywords": "dry clothes, wet clothes, terrace, drying lines"
        },
        {
            "topic": "Hostel Life",
            "question": "What hours is hot water available in the hostel bathrooms?",
            "answer": "Hot water from solar heaters is generally available in the mornings from 6:00 AM to 9:00 AM. During winter or rainy days, electric boilers are turned on as backup.",
            "keywords": "hot water, bath, solar heater, winter"
        },
        {
            "topic": "Hostel Life",
            "question": "What is the protocol for leaving luggage in the hostel during semester break?",
            "answer": "During summer break, students must pack all belongings into trunks or locked bags and move them to the designated cloakroom in the hostel. Rooms must be completely emptied for maintenance.",
            "keywords": "luggage, semester break, summer holidays, cloakroom, storage"
        },
        # Mess, Food & Canteens
        {
            "topic": "Mess",
            "question": "What are the daily breakfast, lunch, evening snacks, and dinner hours?",
            "answer": "Generally: Breakfast is 7:30 AM - 9:00 AM. Lunch is 12:30 PM - 2:00 PM. Evening Snacks are 4:30 PM - 5:30 PM. Dinner is 7:30 PM - 9:00 PM.",
            "keywords": "mess timings, breakfast, lunch, dinner, snacks"
        },
        {
            "topic": "Mess",
            "question": "Is the mess menu fixed, and who manages menu feedback?",
            "answer": "The menu is set on a monthly basis by the student mess committee in consultation with the catering manager. You can provide feedback in the register at the mess exit or to your student reps.",
            "keywords": "mess menu, feedback, student committee"
        },
        {
            "topic": "Mess",
            "question": "How do I switch between vegetarian and non-vegetarian food options?",
            "answer": "If there are separate messes, you must opt for one at the beginning of the month. Otherwise, non-veg items are served on specific days (like Wed/Sun) alongside veg options.",
            "keywords": "veg, non-veg, vegetarian, switch mess"
        },
        {
            "topic": "Mess",
            "question": "How do I request sick diet (like porridge or khichdi) delivered to my room?",
            "answer": "If you are unwell, inform the warden. They will authorize a sick diet (khichdi, bread, milk) and a friend or staff member can bring it to your room.",
            "keywords": "sick diet, sick food, khichdi, room delivery"
        },
        {
            "topic": "Mess",
            "question": "Are campus canteens or cafeterias open late at night during exams?",
            "answer": "The main canteens close by 8 PM, but night canteens or small kiosks near the hostels stay open until midnight, especially during exam weeks.",
            "keywords": "night canteen, late night food, exams"
        },
        {
            "topic": "Mess",
            "question": "How can a visiting family member or guest pay for a meal in the mess?",
            "answer": "Guests can eat in the mess by purchasing a guest meal coupon from the mess manager or warden's office for a nominal charge.",
            "keywords": "guest meal, family eat in mess, coupon"
        },
        {
            "topic": "Mess",
            "question": "Where can I report food quality or hygiene concerns?",
            "answer": "Report hygiene issues immediately to the Mess Manager on duty and document it in the complaint register. Severe issues should be escalated to the Chief Warden.",
            "keywords": "food quality, hygiene, complain about food, bug in food"
        },
        {
            "topic": "Mess",
            "question": "Can I claim a mess fee rebate if I go home for an extended leave?",
            "answer": "Mess rebate is usually applicable only for continuous approved absence of more than 5-7 days. You must apply for the rebate in advance before leaving campus.",
            "keywords": "mess rebate, fee reduction, leave"
        },
        {
            "topic": "Mess",
            "question": "Are outside food deliveries (Swiggy, Zomato) permitted to enter the hostel gate?",
            "answer": "Delivery executives are not allowed past the main campus gate. Students must walk to Gate No. 1 to collect their Swiggy, Zomato, or parcel deliveries.",
            "keywords": "swiggy, zomato, food delivery, outside food"
        },
        {
            "topic": "Mess",
            "question": "What should I do if the floor drinking water dispenser runs out?",
            "answer": "Inform the hostel security guard or block attender, and they will arrange to replace the water bubble or check the RO supply line.",
            "keywords": "drinking water, empty, RO, dispenser"
        },
        # IT Services, Wi-Fi & Portals
        {
            "topic": "IT Services",
            "question": "How do I activate my official college email ID and student ERP account?",
            "answer": "Your official email and ERP credentials will be emailed to your registered personal email address during orientation week. Follow the link provided to set your password.",
            "keywords": "activate email, ERP account, college email, login"
        },
        {
            "topic": "IT Services",
            "question": "What is the login process and password format for the campus Wi-Fi network?",
            "answer": "Connect to the 'VFSTR-Student' Wi-Fi network. A captive portal will pop up. Enter your Roll Number as the username and your ERP password (or the default password provided by IT) to log in.",
            "keywords": "wifi login, password format, connect to wifi"
        },
        {
            "topic": "IT Services",
            "question": "How many personal devices can I register under my student account?",
            "answer": "Typically, students are allowed to register up to two devices (e.g., one laptop and one mobile phone) on the campus Wi-Fi using their credentials concurrently.",
            "keywords": "devices limit, number of phones, wifi limit"
        },
        {
            "topic": "IT Services",
            "question": "Whom do I contact if my student ERP portal gets locked or forgets my password?",
            "answer": "Use the 'Forgot Password' link on the ERP portal to reset via your registered mobile/email. If locked, visit the IT Helpdesk in the A-Block Server Room to get it unlocked.",
            "keywords": "locked ERP, forgot password, reset password"
        },
        {
            "topic": "IT Services",
            "question": "Does the college provide free student access to Microsoft 365, MATLAB, or GitHub?",
            "answer": "Yes, your official university email (e.g., your_rollno@vignan.ac.in) gives you free access to Microsoft 365, GitHub Student Developer Pack, and campus-licensed software like MATLAB.",
            "keywords": "Microsoft 365, MATLAB, GitHub, free software, student pack"
        },
        {
            "topic": "IT Services",
            "question": "Why are certain websites blocked on the college Wi-Fi, and how do I request access?",
            "answer": "Social media, streaming, and gaming sites may be blocked during academic hours to conserve bandwidth. If a legitimate educational site is blocked, email the IT department (it_support@vignan.ac.in) to whitelist it.",
            "keywords": "blocked websites, whitelist, unblock, internet restrictions"
        },
        {
            "topic": "IT Services",
            "question": "How do I submit assignments through the college LMS (e.g., Moodle or Google Classroom)?",
            "answer": "Faculty will invite you to their Google Classroom or Moodle course using your official college email. You can upload assignments in PDF/Word format under the 'Classwork' tab before the deadline.",
            "keywords": "submit assignment, LMS, Moodle, Google Classroom"
        },
        {
            "topic": "IT Services",
            "question": "Where is the campus IT helpdesk located for hardware or OS setup?",
            "answer": "The main IT Helpdesk and network administration team are located on the 2nd Floor of the A-Block. They can assist with Wi-Fi configuration and basic OS issues.",
            "keywords": "IT helpdesk, OS setup, hardware repair, laptop fix"
        },
        {
            "topic": "IT Services",
            "question": "How do I check my daily attendance and fee receipts on the student mobile app?",
            "answer": "Download the official Vignan ERP app from the Play Store/App Store. Log in with your credentials to view attendance, timetable, marks, and download fee receipts.",
            "keywords": "mobile app, check attendance, fee receipt, app"
        },
        {
            "topic": "IT Services",
            "question": "Can I access the university digital library network from off-campus?",
            "answer": "Yes, you can access digital journals (IEEE, Springer) off-campus using the university's EZproxy link provided on the central library website, logging in with your ERP credentials.",
            "keywords": "off-campus access, digital library, EZproxy, journals from home"
        },
        # Library & Study Spaces
        {
            "topic": "Library",
            "question": "What are the library opening and closing hours during exams vs. normal days?",
            "answer": "On normal working days, the library is open from 8:00 AM to 8:00 PM. During the end-semester examination period, hours are extended to 11:00 PM. It is also open on Sundays from 9:00 AM to 1:00 PM.",
            "keywords": "library hours, exams, timings, open, close"
        },
        {
            "topic": "Library",
            "question": "How many books can a first-year student check out at a time, and for how long?",
            "answer": "First-year B.Tech students can typically issue up to 4 books at a time for a duration of 14 days.",
            "keywords": "book limit, borrow books, issue books, how many"
        },
        {
            "topic": "Library",
            "question": "What is the daily overdue fine for returning a book late?",
            "answer": "A fine of Rs. 1 per day is charged for the first week of delay, which increases to Rs. 2 or more per day thereafter.",
            "keywords": "overdue fine, late book, penalty, library fee"
        },
        {
            "topic": "Library",
            "question": "How do I activate book borrowing on my student identity card?",
            "answer": "Your smart ID card doubles as your library card. It is activated automatically once your admission is confirmed. You must scan the barcode at the circulation desk to issue books.",
            "keywords": "activate ID, library card, borrow, smart card"
        },
        {
            "topic": "Library",
            "question": "Are there dedicated silent reading zones and group discussion rooms?",
            "answer": "Yes, the first floor of the central library is a strict silence zone for individual study. The ground floor has designated areas for reference and quiet group discussions.",
            "keywords": "silent zone, group discussion, reading room"
        },
        {
            "topic": "Library",
            "question": "Where can I find previous years' university examination question papers?",
            "answer": "Previous year question papers (PYQs) are bound and kept in the reference section of the library. Digital copies are also available on the library portal (DSpace repository).",
            "keywords": "previous year papers, PYQs, old question papers, past exams"
        },
        {
            "topic": "Library",
            "question": "Does the library provide printing, scanning, or photocopying services?",
            "answer": "Yes, there is a reprographic section inside the library where you can get notes photocopied or printed at nominal rates.",
            "keywords": "printing, scanning, photocopying, xerox library"
        },
        {
            "topic": "Library",
            "question": "Can I take my personal backpack and textbooks inside the reading halls?",
            "answer": "Personal bags and textbooks are generally not allowed inside the main book stacks. You must deposit your bag in the property counter at the entrance. You can take a notebook and laptop inside.",
            "keywords": "backpack, bags allowed, library rules, property counter"
        },
        {
            "topic": "Library",
            "question": "How do I access IEEE, Springer, and other research journal repositories?",
            "answer": "You can access these repositories directly when connected to the campus Wi-Fi. The library homepage has direct links to subscribed databases like IEEE Xplore, ScienceDirect, etc.",
            "keywords": "IEEE, Springer, research journals, access papers"
        },
        {
            "topic": "Library",
            "question": "Can I renew a borrowed book online without bringing it to the physical counter?",
            "answer": "Yes, you can renew a book once online via the library web OPAC portal before the due date, provided no other student has reserved it.",
            "keywords": "renew book, online renewal, OPAC"
        },
        # Administration, Fees & Documentation
        {
            "topic": "Administration",
            "question": "When and where will official physical student ID cards be distributed?",
            "answer": "ID cards are usually distributed in your respective classrooms by the class teacher during the second or third week of the first semester.",
            "keywords": "ID cards, physical ID, get ID, distribution"
        },
        {
            "topic": "Administration",
            "question": "What is the payment schedule and deadline for next semester's tuition fees?",
            "answer": "Tuition fees are paid annually or semester-wise. The deadline is usually the day before semester registration begins. Notifications will be sent via ERP and email.",
            "keywords": "fee deadline, tuition fees, payment schedule"
        },
        {
            "topic": "Administration",
            "question": "Where do I download official fee receipts for education loans or tax claims?",
            "answer": "Fee receipts can be downloaded directly from the 'Fee Details' section of your student ERP dashboard. They are digitally signed and valid for banks and taxes.",
            "keywords": "fee receipt, education loan, tax claim, download receipt"
        },
        {
            "topic": "Administration",
            "question": "How do I apply for a Bonafide Certificate for a passport, visa, or bank loan?",
            "answer": "Submit a requisition letter to your HOD. Once forwarded, submit it to the Academic Section in the A-Block. The certificate is usually issued within 2 working days.",
            "keywords": "bonafide certificate, passport, visa, bank loan"
        },
        {
            "topic": "Administration",
            "question": "Where do I submit state or national scholarship verification forms?",
            "answer": "Scholarship documents (like AP ePASS or National Scholarship Portal forms) are verified and processed by the Scholarship Cell located in the A-Block ground floor.",
            "keywords": "scholarship, verification, forms, ePASS"
        },
        {
            "topic": "Administration",
            "question": "How do I correct a typo in my name or parent's name in official records?",
            "answer": "Submit an application along with a copy of your 10th standard marks memo as proof to the Academic Section. They will update the ERP and university records.",
            "keywords": "name correction, typo, parent name, change name"
        },
        {
            "topic": "Administration",
            "question": "What is the process to get a student concession pass for local buses or railways?",
            "answer": "Obtain a railway/bus concession form from the student affairs office, fill it out, get it signed by the designated officer, and submit it to the APSRTC or Railway authorities.",
            "keywords": "concession pass, bus pass, railway pass, train pass"
        },
        {
            "topic": "Administration",
            "question": "Where do I submit bank demand drafts or education loan disbursement letters?",
            "answer": "Demand Drafts and loan cheques should be submitted to the Finance/Accounts Office located on the Ground Floor of the A-Block.",
            "keywords": "demand draft, DD, education loan, cheque, submit"
        },
        {
            "topic": "Administration",
            "question": "Where and when do I submit original migration and transfer certificates?",
            "answer": "Original certificates (TC, Migration, 12th Marks) must be submitted to the Admissions Office during document verification in the first week of college.",
            "keywords": "migration certificate, TC, transfer certificate, original documents"
        },
        {
            "topic": "Administration",
            "question": "What should I do if I lose my student ID card, and how do I get a replacement?",
            "answer": "Report the loss to the Chief Security Officer immediately. Pay the duplicate ID card fee at the Accounts office, and submit the receipt to the IT department for a replacement.",
            "keywords": "lost ID, replace ID card, duplicate ID"
        },
        # Health & Wellness
        {
            "topic": "Health",
            "question": "Where is the campus health center or dispensary located, and what are doctor timings?",
            "answer": "The campus health center is located near the hostel complex. A doctor is available during working hours (9 AM - 5 PM), and nursing staff are present 24/7.",
            "keywords": "health center, doctor, dispensary, medical"
        },
        {
            "topic": "Health",
            "question": "Are basic doctor consultations and emergency medications free for students?",
            "answer": "Yes, primary consultations and basic first-aid/medicines provided at the campus health center are free for all enrolled students.",
            "keywords": "free medicine, doctor cost, free consultation"
        },
        {
            "topic": "Health",
            "question": "What is the emergency contact number for the campus ambulance service?",
            "answer": "In emergencies, contact your hostel warden or the main security gate (Ext. 200). The campus ambulance is available 24/7 for transport to nearby hospitals.",
            "keywords": "ambulance, emergency number, hospital transport"
        },
        {
            "topic": "Health",
            "question": "Is there a university counselor or mental health support service available?",
            "answer": "Yes, a professional psychological counselor is available in the Student Wellness Center (C-Block). Sessions are strictly confidential.",
            "keywords": "counselor, mental health, depression, stress, therapy"
        },
        {
            "topic": "Health",
            "question": "Does the campus clinic provide valid medical certificates for missed examinations?",
            "answer": "Yes, if you are treated at the campus health center, the resident doctor can issue a medical certificate which is valid for attendance and exam condonation.",
            "keywords": "medical certificate, missed exam, sick note"
        },
        {
            "topic": "Health",
            "question": "Where is the closest full-service hospital and 24-hour pharmacy outside campus?",
            "answer": "The closest major hospitals (like NRI General Hospital or Ramesh Hospitals) and 24-hour pharmacies are located in Guntur city, about 15-20 minutes from the campus.",
            "keywords": "hospital outside, 24-hour pharmacy, major hospital"
        },
        {
            "topic": "Health",
            "question": "Whom do I contact immediately if I experience or witness ragging or harassment?",
            "answer": "Immediately contact the National Anti-Ragging Helpline (1800-180-5522), your HOD, the Chief Warden, or the Dean of Student Affairs. VFSTR maintains a strict zero-tolerance policy.",
            "keywords": "ragging, harassment, anti-ragging, emergency, bullying"
        },
        {
            "topic": "Health",
            "question": "Where can I reach campus security guards if I need an escort across campus late at night?",
            "answer": "You can contact the main gate security cabin (Ext. 200). For female students studying late in the library, security escorts to the hostel are provided upon request.",
            "keywords": "security escort, late night, campus security, safe walk"
        },
        # Clubs & Sports
        {
            "topic": "Clubs",
            "question": "How and when do first-year students sign up for student clubs and societies?",
            "answer": "Club recruitment drives (Student Activities Center - SAC) take place in the first month of the odd semester. Stalls will be set up, and you can sign up via QR codes.",
            "keywords": "clubs, societies, sign up, SAC, join club"
        },
        {
            "topic": "Clubs",
            "question": "Which sports grounds and indoor courts are open to all students without team tryouts?",
            "answer": "The main athletics ground, basketball courts, and volleyball courts are open to all students after academic hours. Equipment can be issued by showing your ID card to the physical director.",
            "keywords": "sports grounds, basketball, volleyball, play, physical director"
        },
        {
            "topic": "Clubs",
            "question": "What are the campus gym timings, and are there separate slots for women and men?",
            "answer": "The campus gym operates in the mornings (5:30 AM - 7:30 AM) and evenings (4:30 PM - 7:00 PM). Yes, there are dedicated timings for female and male students.",
            "keywords": "gym timings, fitness center, gym slots, workout"
        },
        {
            "topic": "Clubs",
            "question": "Do official club activities or hackathons grant academic attendance exemptions?",
            "answer": "Yes, participation in official external hackathons or university-approved cultural events qualifies for 'On Duty' (OD) leave, which compensates for missed attendance.",
            "keywords": "club attendance, OD for fest, hackathon attendance"
        },
        {
            "topic": "Clubs",
            "question": "How do auditions work for university music, drama, literary, and dance clubs?",
            "answer": "Clubs announce audition dates on official WhatsApp groups and notice boards. You will be asked to perform a short piece or submit a portfolio depending on the club.",
            "keywords": "auditions, dance club, music club, drama, join team"
        },
        {
            "topic": "Clubs",
            "question": "When are the annual cultural and technical festivals organized?",
            "answer": "The national-level technical fest (Srujanankura) is typically held in February/March, and the main cultural fest (Mahotsav) takes place in January/February.",
            "keywords": "fest, cultural fest, Mahotsav, technical fest, Srujanankura"
        },
        {
            "topic": "Clubs",
            "question": "Can freshers participate directly in inter-college hackathons and athletic meets?",
            "answer": "Absolutely! Freshers are encouraged to participate. You just need approval from your HOD and the faculty advisor of the respective club/sports team.",
            "keywords": "freshers participate, inter-college, hackathon, sports meet"
        },
        {
            "topic": "Clubs",
            "question": "What is the process for founding a new student chapter or hobby club?",
            "answer": "To start a new club, you need a proposal, a minimum number of interested students, and a faculty advisor. Submit the proposal to the Dean of Student Affairs for approval.",
            "keywords": "start a club, new club, founder, student chapter"
        },
        # Rules & Local Life
        {
            "topic": "Rules",
            "question": "Is there a mandatory dress code or uniform for regular lectures and laboratory work?",
            "answer": "Yes, VFSTR observes a formal dress code for regular classes. For workshops and labs, closed-toe shoes and safety gear (like lab coats) are strictly mandatory.",
            "keywords": "dress code, uniform, formal dress, lab coat"
        },
        {
            "topic": "Rules",
            "question": "Where is the nearest shopping market to purchase daily toiletries, buckets, and snacks?",
            "answer": "The campus has a utility store that sells basic stationery and toiletries. For major shopping (buckets, mattresses), students usually go to Vadlamudi village or Guntur city.",
            "keywords": "shopping, buy buckets, toiletries, market, store"
        },
        {
            "topic": "Rules",
            "question": "What is the cheapest and most reliable way to travel to the nearest railway station or bus terminal?",
            "answer": "Shared auto-rickshaws and RTC buses frequently ply between the campus main gate and Tenali/Guntur railway stations. They are the most economical option.",
            "keywords": "travel, railway station, bus terminal, transport, auto"
        },
        {
            "topic": "Rules",
            "question": "What electronic appliances or items are strictly confiscated during room inspections?",
            "answer": "Items like electric heaters, induction stoves, iron boxes, alcohol, cigarettes, and any prohibited substances are strictly confiscated and lead to disciplinary action.",
            "keywords": "confiscated, illegal items, room inspection, banned"
        },
        {
            "topic": "Rules",
            "question": "Can day scholars stay overnight in the hostel during fest rehearsals or project deadlines?",
            "answer": "Overnight stays for day scholars are permitted only with prior written approval from the HOD, event coordinator, and the Chief Warden, and subject to bed availability.",
            "keywords": "day scholar stay, overnight, hostel stay"
        },
        {
            "topic": "Rules",
            "question": "Where can students store heavy luggage or trunks over long summer and winter breaks?",
            "answer": "The hostel provides designated cloakrooms. Students can store their locked trunks there during the summer vacation free of charge.",
            "keywords": "store luggage, summer break, trunk, cloakroom"
        }
    ]

    for f in faqs:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO fresher_faqs (faq_id, topic, question, answer, keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (f"faq-{uuid.uuid4().hex[:8]}", f["topic"], f["question"], f["answer"], f["keywords"]))
        except Exception as e:
            print(f"Error inserting {f['question']}: {e}")

    conn.commit()
    print(f"Successfully seeded {len(faqs)} FAQs into the database.")

if __name__ == "__main__":
    seed_comprehensive_faqs()
