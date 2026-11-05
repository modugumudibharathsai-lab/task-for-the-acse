import os
import sys
import uuid
import sqlite3
import re
import random

def get_db_connection():
    db_path = r"database\vigbot.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_mock_answer(question):
    q = question.lower()
    
    if "hostel open" in q or "mess open" in q or "library open" in q or "lab open" in q or "student lounge open" in q or "stationery shop open" in q or "admin office open" in q or "auditorium open" in q or "placement cell open" in q or "canteen open" in q or "seminar hall open" in q or "sports complex open" in q or "local zoo open" in q or "main block open" in q or "nearest atm open" in q or "gym open" in q:
        match = re.search(r'what time does the (.*?) open', q)
        place = match.group(1).title() if match else "Facility"
        return f"The {place} typically opens at 8:00 AM and closes around 8:00 PM. Please check the official notice board for exact timings on weekends."
    
    if "mess food on" in q:
        match = re.search(r'mess food on (.*)', q)
        day = match.group(1).capitalize().replace("?", "") if match else "that day"
        return f"The mess food on {day} features a special menu decided by the student committee. It generally includes both North Indian and South Indian options."
    
    if "where exactly is the" in q:
        match = re.search(r'where exactly is the (.*)', q)
        place = match.group(1).title().replace("?", "") if match else "Location"
        return f"The {place} is located on the campus map near the central courtyard. You can ask any security guard for specific directions."
    
    if "tough subject" in q:
        match = re.search(r'is (.*) a tough subject', q)
        subject = match.group(1).title() if match else "this subject"
        return f"{subject} can be challenging, but with consistent practice and utilizing the professor's office hours, it is very manageable."
    
    if "how do i clear the" in q:
        match = re.search(r'how do i clear the (.*)', q)
        exam = match.group(1).title().replace("?", "") if match else "exam"
        return f"To clear the {exam}, review the previous year's question papers, attend all revision classes, and ensure you understand the core concepts from the syllabus."
    
    if "at the canteen today" in q:
        match = re.search(r'how is the (.*) at the canteen', q)
        food = match.group(1).title() if match else "food"
        return f"The {food} at the canteen is quite popular today! Many students recommend trying it while it's fresh."
    
    if "calculators allowed in the" in q:
        match = re.search(r'calculators allowed in the (.*)', q)
        exam = match.group(1).title().replace("?", "") if match else "exam"
        return f"Non-programmable scientific calculators are generally allowed in the {exam}. Please verify with your invigilator before the exam starts."
    
    if "should i make notes for" in q:
        match = re.search(r'should i make notes for (.*)', q)
        subject = match.group(1).title().replace("?", "") if match else "this subject"
        return f"Yes, making your own handwritten notes for {subject} is highly recommended. It helps with retention and makes revision much easier."
    
    if "freshers' party" in q:
        return "The freshers' party is typically scheduled in the second month of the first semester. Keep an eye on the official student portal for the exact date."
    
    if "are you coming to the" in q:
        match = re.search(r'are you coming to the (.*)', q)
        place = match.group(1).title().replace("?", "") if match else "place"
        return f"As an AI, I don't physically travel, but I'm always here online to help you with any information you need about the {place}!"
    
    if "which book is best for" in q:
        match = re.search(r'which book is best for (.*)', q)
        subject = match.group(1).title().replace("?", "") if match else "this subject"
        return f"For {subject}, refer to the standard textbook prescribed in your course syllabus. The library has multiple copies in the reference section."
    
    if "syllabus for" in q:
        match = re.search(r'syllabus for (.*)', q)
        subject = match.group(1).title().replace("?", "") if match else "this subject"
        return f"The syllabus for {subject} is available on the student ERP portal under the 'Academics' tab. If not updated, please check with your class representative."
    
    if "attendance rule really strict for" in q:
        match = re.search(r'attendance rule really strict for (.*)', q)
        subject = match.group(1).title().replace("?", "") if match else "this subject"
        return f"Yes, the university mandates a minimum of 75% attendance across all subjects, including {subject}. Shortage can lead to debarment."
    
    if "penalty for short attendance" in q:
        return "The penalty for short attendance (below 75%) is debarment from the End-Semester Examination, and you may be awarded an 'FA' grade."
    
    if "wash my clothes" in q:
        return "You can use the hostel laundry service which operates twice a week. Drop off your clothes at the designated laundry counter."
    
    if "ragging issues" in q:
        return "VFSTR has a strict zero-tolerance policy against ragging. The campus is very safe, and there are active anti-ragging squads. You can report any issues to 1800-425-XXXX."
    
    if "wifi password" in q:
        return "To connect to the hostel Wi-Fi, use your Roll Number as the username and your ERP password to log in through the captive portal."
    
    if "change my branch" in q:
        return "Branch changes are possible at the end of the first year, subject to availability of seats and maintaining a high CGPA (usually above 8.5)."
    
    if "leave campus after 9 pm" in q:
        return "Hostel students cannot leave the campus after the curfew time (9:00 PM for boys, 8:30 PM for girls) without prior out-pass approval."
    
    if "lend me a charger" in q:
        return "I can't lend you a physical charger, but you can try asking at the library desk or check with your friends in the student lounge."
    
    if "buy a notebook right now" in q:
        return "You can buy a notebook at the campus stationery shop located on the Ground Floor of the A-Block."

    # Year 2, 3, 4 queries pattern matching
    if "practicals scheduled" in q or "upsc scheduled" in q or "gre scheduled" in q or "placements scheduled" in q or "surprise tests scheduled" in q or "cat scheduled" in q or "class tests scheduled" in q or "assessments scheduled" in q or "gate scheduled" in q or "mid-semesters scheduled" in q or "viva scheduled" in q or "end-semesters scheduled" in q:
        return "Please refer to the Academic Calendar on the ERP portal for the exact dates of all scheduled exams, practicals, and events."
        
    if "prerequisite for anything" in q:
        return "Yes, core subjects are often prerequisites for advanced electives. Check the course structure document provided by your department."

    if "worth participating in" in q:
        return "Absolutely! Participating in fests and extracurriculars helps build soft skills, expand your network, and looks great on your resume."

    if "how do we form groups for the" in q:
        return "Groups are usually formed by students themselves within a specific timeframe. Inform your course instructor once your group of 3-4 members is finalized."

    if "what should i study for" in q:
        return "Focus on the lecture slides, previous year question papers, and the primary textbook recommended in your syllabus."

    if "should i start competitive programming or" in q:
        return "It depends on your career goals! Competitive programming builds logic for product companies, while development builds your portfolio for startups and diverse roles. Doing a bit of both is ideal."

    if "when is the assignment deadline for" in q:
        return "Check your Google Classroom or Moodle for the exact assignment deadline. If not posted, ask your class representative."

    if "which ide do you use for" in q:
        return "Students commonly use VS Code, IntelliJ, PyCharm, or Eclipse depending on the language. VS Code is generally the most versatile."

    if "previous year paper for" in q:
        return "Previous year papers are available in the central library's reference section and on the digital DSpace repository online."

    if "which club should i join for" in q:
        return "You should check out the Student Activities Center (SAC) during the recruitment drive. There are dedicated clubs for various technical and cultural interests."

    if "how do i balance clubs and academics" in q:
        return "Time management is key. Prioritize your academics, create a weekly schedule, and only commit to 1-2 clubs that you are truly passionate about."

    if "best resource to learn" in q:
        return "There are many great resources! FreeCodeCamp, Coursera, YouTube, and official documentation are excellent starting points for any new skill."

    if "how can i apply for a student committee" in q:
        return "Keep an eye on official university emails. Committees usually send out forms for recruitment at the start of the academic year."

    if "how do i get a good grade in" in q:
        return "Attend all classes, submit assignments on time, clarify doubts during office hours, and practice previous years' question papers."

    if "has anyone solved the assignment for" in q:
        return "I recommend trying to solve it yourself first! If you're stuck, form a study group with your classmates to discuss the concepts."

    if "are there any hackathons happening soon" in q:
        return "Check the campus notice boards and official WhatsApp groups. The university's technical clubs frequently organize hackathons."

    if "who is up for" in q:
        return "That sounds like fun! You might want to ask your friends in your hostel block or message in your class group."

    if "does gpa matter for internships" in q:
        return "Yes, many companies have a baseline CGPA cutoff (often 7.0 or 8.0) for shortlisting candidates for internships and placements."

    if "are we getting a holiday for" in q:
        return "Check the official academic calendar or wait for a circular from the Registrar's office regarding upcoming holidays."

    if "best platforms to practice for" in q:
        return "Platforms like LeetCode, HackerRank, GeeksforGeeks, and Codeforces are excellent for practicing coding questions asked by top companies."

    if "how tough is the" in q:
        return "The syllabus complexity varies, but with regular study and attending all lectures, you can definitely master it."

    if "referrals available for" in q:
        return "You should network with university alumni on LinkedIn or check with the Placement Cell for potential referral opportunities."

    if "how do i publish a research paper in" in q:
        return "Start by discussing your ideas with a faculty member who specializes in that field. They can guide you on the research process and target conferences/journals."

    if "how do i clear the" in q:
        return "To clear technical rounds, practice coding algorithms, brush up on core CS concepts (OS, DBMS, CN), and practice mock interviews."

    if "has anyone heard back from" in q:
        return "Company results are usually communicated directly via email or through the Placement Cell. Please contact the T&P department for official updates."

    if "how do i apply for an internship at" in q:
        return "You can apply through their official career portal, look for off-campus drives, or apply through the university's placement cell if they visit campus."

    if "is doing an unpaid internship in" in q:
        return "Unpaid internships can be valuable for gaining experience and skills, but ensure the work is meaningful and doesn't conflict with your academics."

    if "can we do our minor project on" in q:
        return "Yes, you can choose a minor project topic of your interest, provided it gets approved by your assigned faculty guide."

    if "should i prepare for" in q:
        return "Align your preparation with your primary career goal. If you want a job immediately, focus on placements; for higher studies, focus on competitive exams."

    if "should i put" in q and "on my resume" in q:
        return "Only include skills and projects on your resume that you are confident about and can thoroughly explain during an interview."

    if "do we have a project submission for" in q:
        return "Please check the official course schedule or consult with your faculty instructor for the exact project submission deadlines."

    if "what is a good score in" in q:
        return "A 'good score' depends on the specific exam or test, but generally aiming for above 80% or a high percentile will keep you competitive."

    if "what kind of projects are required for" in q:
        return "Focus on building end-to-end projects that solve real-world problems and demonstrate your proficiency in the relevant tech stack."

    if "did the stipend get credited yet" in q:
        return "Stipend processing can sometimes take time. Check with the company's HR or the university finance department if it's delayed."

    if "when is the registration deadline for" in q:
        return "Registration deadlines are strictly communicated via official circulars and emails. Please check your student inbox."

    if "who can give me a letter of recommendation" in q:
        return "Approach professors who know you well, preferably those whose classes you excelled in or under whom you completed a project."

    if "can someone share their resume format" in q:
        return "The Placement Cell provides standard, ATS-friendly resume templates. You can collect them from their office or portal."

    if "how do i negotiate my salary with" in q:
        return "For campus placements, salaries are usually fixed. For off-campus roles, research industry standards and respectfully discuss your expectations with HR based on your skills."

    if "what did the hr ask in the" in q:
        return "HR rounds typically focus on behavioral questions, your strengths/weaknesses, willingness to relocate, and why you want to join the company."

    if "how do i prepare for a" in q and "role at" in q:
        return "Review the specific job description, brush up on required technical skills, and practice standard interview questions for that particular role."

    if "what should i wear to the" in q:
        return "Always wear formal business attire to all interviews and placement drives, unless explicitly specified otherwise by the company."

    if "did" in q and "announce their results yet" in q:
        return "The Placement Cell will send an official email as soon as the company shares the final selected candidate list."

    if "what is the base package offered by" in q:
        return "Compensation details are shared during the company's pre-placement talk. Please refer to the job description document for exact figures."

    if "how is the work-life balance at" in q:
        return "Work-life balance varies greatly depending on the team and project you are assigned to, even within the same company."

    if "is it too late to start preparing for" in q:
        return "It's never too late to start! Create a focused study plan and begin immediately to make the most of the time you have left."

    if "what are the bond breaking policies for" in q:
        return "Bond policies are detailed in the offer letter. Breaking a bond usually requires paying a penalty amount specified in the agreement."

    if "is" in q and "revoking offers this year" in q:
        return "Please rely only on official communications from the Placement Cell regarding offer status, rather than rumors."

    if "can someone guide me on the major project for" in q:
        return "Discuss potential topics with your faculty guide. They can help you define the scope and methodology for your major project."

    if "are there any off-campus drives for" in q:
        return "Keep checking platforms like LinkedIn, standard job portals, and the company's official career pages for off-campus drive announcements."

    if "can i get placed with a backlog in" in q:
        return "Most top companies require you to clear all active backlogs before the joining date or the interview process. Focus on clearing it ASAP."

    if "is there a bond agreement for" in q:
        return "Many IT service companies have service agreements (bonds) of 1-2 years. Check the official job description shared by the T&P cell."

    if "how do i get my provisional degree certificate" in q:
        return "You can apply for the Provisional Certificate through the Academic Section after all your 8th-semester results are published and you have no dues."

    if "what is the process for transcript clearance" in q:
        return "You need to obtain a 'No Dues' certificate from the library, hostel, finance, and your department before applying for transcripts."

    if "who is planning to go abroad for ms" in q:
        return "Many students pursue higher education abroad! You might want to connect with the university's Higher Education Cell or alumni network."

    if "when is the farewell party" in q:
        return "The farewell party is usually organized by the pre-final year students towards the end of your 8th semester. Dates will be announced later."

    if "what time does the last bus leave" in q:
        return "The last university bus usually leaves the campus at 5:30 PM. Please check the transport office for the exact schedule."

    if "did anyone find my keys in the" in q:
        return "Please check with the central Lost and Found desk at the main security gate or the reception of the respective block."

    if "i am craving" in q:
        return "You can head over to the campus canteens or the food court! They have a variety of snacks and meals available."

    if "does anyone have an umbrella" in q:
        return "You might want to ask your roommate or friends nearby. Always handy to keep one in your bag during the rainy season!"

    if "is the ac working in the" in q:
        return "If the AC is not working, please inform the respective block's maintenance staff or the administrative office."

    if "how do i reach the railway station from the" in q:
        return "You can take an auto from the main gate directly to the railway station, or take the RTC bus which stops near the campus."

    if "does anyone want to order" in q:
        return "Sounds like a great plan! Just remember to collect your order from Gate No. 1, as delivery partners aren't allowed inside."

    if "can you wake me up at" in q:
        return "I'm a virtual assistant, so I can't knock on your door, but I recommend setting a loud alarm on your phone!"

    if "are we getting a proxy for the next class" in q:
        return "If a faculty member is on leave, the department usually arranges a substitute (proxy). Check your class WhatsApp group for updates."

    if "are we having a surprise test in the next class" in q:
        return "It's called a surprise test for a reason! It's always best to be prepared by briefly reviewing the last few lectures."

    if "did the teacher take attendance yet" in q:
        return "Attendance is usually taken at the beginning of the class via biometric or roll call. Make sure you're on time!"

    if "who wants to split an auto ride" in q:
        return "You can check with your classmates or post in the hostel WhatsApp group to find someone heading in the same direction."

    if "are we watching a movie this weekend" in q:
        return "There might be a screening organized by the film club in the auditorium, or you can plan a movie night with your friends in the hostel!"

    if "is the washing machine in the hostel working" in q:
        return "Please check with the hostel warden or the maintenance logbook to see if the washing machines are operational today."

    if "is there any electricity in the hostel" in q:
        return "The hostel has power backup generators. If there's an outage, the backup usually kicks in within a few minutes."
        
    # Catch-all
    return "That's a good question! I recommend checking the official student handbook or contacting the relevant department for the most accurate information."

def process_questions():
    input_file = os.path.join(os.path.dirname(__file__), "raw_questions.txt")
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    # Extract the actual question part (remove "1. " etc)
    cleaned_questions = []
    pattern = re.compile(r'^\d+\.\s+(.*)')
    for q in questions:
        match = pattern.match(q)
        if match:
            cleaned_questions.append(match.group(1))
        else:
            cleaned_questions.append(q)

    conn = get_db_connection()
    
    # Process and insert
    inserted_count = 0
    for q in cleaned_questions:
        q_clean = q.replace("(Variation)", "").strip()
        answer = generate_mock_answer(q_clean)
        
        # Categorize roughly based on keywords
        topic = "General"
        if "hostel" in q_clean.lower() or "mess" in q_clean.lower(): topic = "Hostel Life"
        elif "exam" in q_clean.lower() or "syllabus" in q_clean.lower() or "grade" in q_clean.lower(): topic = "Academics"
        elif "internship" in q_clean.lower() or "placement" in q_clean.lower() or "interview" in q_clean.lower() or "salary" in q_clean.lower(): topic = "Placements"
        elif "club" in q_clean.lower() or "fest" in q_clean.lower(): topic = "Clubs"
        
        try:
            conn.execute("""
                INSERT INTO fresher_faqs (faq_id, topic, question, answer, keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (f"faq-{uuid.uuid4().hex[:8]}", topic, q_clean, answer, topic.lower()))
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting {q_clean}: {e}")

    conn.commit()
    print(f"Successfully processed and seeded {inserted_count} new FAQs into the database.")

if __name__ == "__main__":
    process_questions()
