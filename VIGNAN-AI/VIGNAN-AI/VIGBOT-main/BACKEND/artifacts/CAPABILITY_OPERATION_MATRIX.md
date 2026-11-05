# VIGBOT Exhaustive Application Capability-Operation Matrix
**Total Registered Features**: 28  
**Total Validated Feature-Operation Pairs**: 48  

---

| Feature | Operation | Type | Frontend Route | Backend Endpoint / DB | Auth | Confirmation | Write? |
|---|---|---|---|---|---|---|---|
| **Helpdesk Home & Command Center** (`home`) | `view_overview` | `view` | `/?tab=home` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Helpdesk Home & Command Center** (`home`) | `navigate_home` | `navigate` | `/?tab=home` | `GET /?tab=home` | 🌐 Public | No | 🟢 Read/Nav |
| **Lost & Found** (`lost-and-found`) | `view_listings` | `view` | `/?tab=lost-and-found` | `fetchLostAndFoundItems('all')` | 🌐 Public | No | 🟢 Read/Nav |
| **Lost & Found** (`lost-and-found`) | `filter_items` | `filter` | `/?tab=lost-and-found` | `fetchLostAndFoundItems(filterType)` | 🌐 Public | No | 🟢 Read/Nav |
| **Lost & Found** (`lost-and-found`) | `report_item` | `report` | `/?tab=lost-and-found` | `reportLostAndFoundItem(studentId, type, title, description, tags, contactInfo)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Lost & Found** (`lost-and-found`) | `claim_item` | `claim` | `/?tab=lost-and-found` | `claimLostAndFoundItem(itemId, studentId)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Student Services** (`services`) | `view_services` | `view` | `/?tab=services` | `GET /api/v1/service-requests` | 🔒 Auth | No | 🟢 Read/Nav |
| **Student Services** (`services`) | `submit_request` | `submit` | `/?tab=services` | `POST /api/v1/service-requests` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Student Services** (`services`) | `track_request` | `track` | `/?tab=services` | `GET /api/v1/service-requests/{request_no}` | 🔒 Auth | No | 🟢 Read/Nav |
| **Attendance** (`attendance`) | `view_attendance` | `view` | `/?tab=attendance` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Attendance** (`attendance`) | `calculate_recovery` | `calculate` | `/?tab=attendance` | `calculateConsecutiveClassesNeeded(held, attended, target=0.75)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Attendance** (`attendance`) | `filter_course` | `filter` | `/?tab=attendance` | `GET /api/v1/student/dashboard?course={course_code}` | 🔒 Auth | No | 🟢 Read/Nav |
| **Marks & CGPA** (`marks`) | `view_marks` | `view` | `/?tab=marks` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Marks & CGPA** (`marks`) | `filter_subject_marks` | `filter` | `/?tab=marks` | `GET /api/v1/student/dashboard?course={course_code}` | 🔒 Auth | No | 🟢 Read/Nav |
| **Timetable & Schedule** (`timetable`) | `view_schedule` | `view` | `/?tab=timetable` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Timetable & Schedule** (`timetable`) | `filter_day` | `filter` | `/?tab=timetable` | `GET /api/v1/student/dashboard?day={day_of_week}` | 🔒 Auth | No | 🟢 Read/Nav |
| **Examinations & Assessments** (`exams`) | `view_exams` | `view` | `/?tab=exams` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Fees & Payments** (`fees`) | `view_fees` | `view` | `/?tab=fees` | `GET /api/v1/student/dashboard` | 🔒 Auth | No | 🟢 Read/Nav |
| **Fees & Payments** (`fees`) | `pay_fee` | `pay` | `/?tab=fees` | `GET /?tab=fees&action=pay` | 🔒 Auth | ⚠️ Yes | 🟢 Read/Nav |
| **Curriculum & Degree Audit** (`curriculum`) | `view_curriculum` | `view` | `/?tab=curriculum` | `curriculum_tool.get_curriculum_summary(session)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Hostel & Mess Services** (`hostel`) | `view_hostel` | `view` | `/?tab=hostel` | `getHostelRequests(studentId)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Hostel & Mess Services** (`hostel`) | `submit_outpass_or_complaint` | `submit` | `/?tab=hostel` | `createHostelRequest(studentId, type, details)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Campus Transport & Bus Tracking** (`transport`) | `view_routes` | `view` | `/?tab=transport` | `getTransportRoutes()` | 🔒 Auth | No | 🟢 Read/Nav |
| **Central Library** (`library`) | `view_borrowed_books` | `view` | `/?tab=library` | `DataRepository.get_library_lended_books(session)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Central Library** (`library`) | `search_catalog` | `search` | `/?tab=library` | `getLibraryResources()` | 🌐 Public | No | 🟢 Read/Nav |
| **Facility Bookings** (`bookings`) | `view_facilities` | `view` | `/?tab=bookings` | `getFacilities()` | 🔒 Auth | No | 🟢 Read/Nav |
| **Facility Bookings** (`bookings`) | `create_booking` | `book` | `/?tab=bookings` | `createBooking(data)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Facility Bookings** (`bookings`) | `cancel_booking` | `cancel` | `/?tab=bookings` | `cancelBooking(bookingId, studentId)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Clubs & Extracurriculars** (`clubs`) | `browse_clubs` | `view` | `/?tab=clubs` | `DataRepository.get_clubs()` | 🌐 Public | No | 🟢 Read/Nav |
| **Clubs & Extracurriculars** (`clubs`) | `apply_club` | `apply` | `/?tab=clubs` | `DataRepository.create_club_application(session, club_id, student_name)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Event Registration** (`events`) | `view_events` | `view` | `/?tab=events` | `DataRepository.get_upcoming_events()` | 🌐 Public | No | 🟢 Read/Nav |
| **Event Registration** (`events`) | `register_event` | `submit` | `/?tab=events` | `registerForEvent(studentId, eventName)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Student Marketplace** (`marketplace`) | `view_listings` | `view` | `/?tab=marketplace` | `getMarketplaceListings()` | 🔒 Auth | No | 🟢 Read/Nav |
| **Student Marketplace** (`marketplace`) | `create_listing` | `submit` | `/?tab=marketplace` | `createMarketplaceListing(studentId, title, category, price)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Campus Map & Navigation** (`map`) | `view_locations` | `view` | `/?tab=map` | `getCampusLocations()` | 🌐 Public | No | 🟢 Read/Nav |
| **Student Wellness & Counseling** (`wellness`) | `view_resources` | `view` | `/?tab=wellness` | `getWellnessResources()` | 🌐 Public | No | 🟢 Read/Nav |
| **Policies & Academic Regulations** (`policies`) | `search_policies` | `search` | `/?tab=policies` | `DataRepository.search_policies(query)` | 🌐 Public | No | 🟢 Read/Nav |
| **Circulars & Notices** (`circulars`) | `view_circulars` | `view` | `/?tab=circulars` | `circulars_tool.get_circulars_summary(session)` | 🌐 Public | No | 🟢 Read/Nav |
| **Academic Calendar** (`calendar`) | `view_calendar` | `view` | `/?tab=calendar` | `fetchStudentSchedule(studentId)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Achievements & Streaks** (`gamification`) | `view_badges` | `view` | `/?tab=gamification` | `getGamificationData(studentId)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Career Hub & Placements** (`career`) | `view_placements` | `view` | `/?tab=career` | `getResumeData(studentId)` | 🔒 Auth | No | 🟢 Read/Nav |
| **Career Hub & Placements** (`career`) | `save_resume` | `submit` | `/?tab=career` | `saveResumeData(studentId, skills, projects)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Student Grievance Redressal** (`grievance`) | `view_grievance_portal` | `view` | `/?tab=services` | `GET /?tab=services&view=grievance` | 🔒 Auth | No | 🟢 Read/Nav |
| **Student Grievance Redressal** (`grievance`) | `lodge_grievance` | `submit` | `/?tab=services` | `submitAncComplaint(complaintText, studentId)` | 🔒 Auth | ⚠️ Yes | 🔴 Write |
| **Campus Polls & Voting** (`polling`) | `view_polls` | `view` | `/?tab=polling` | `getCampusPolls()` | 🔒 Auth | No | 🟢 Read/Nav |
| **Alumni Mentorship Network** (`alumni`) | `view_alumni` | `view` | `/?tab=alumni` | `getAlumniMentors()` | 🔒 Auth | No | 🟢 Read/Nav |
| **Student Profile & Advisors** (`student-profile`) | `view_profile` | `view` | `/?tab=student-profile` | `GET /api/v1/me` | 🔒 Auth | No | 🟢 Read/Nav |
| **Administrative Control Panel** (`admin`) | `admin_console` | `view` | `/admin` | `GET /admin` | 🔒 Auth | No | 🟢 Read/Nav |
