"""
VIGBOT Application Capability & Feature Registry.
Authoritative registry of all verified frontend features, navigation routes,
backend APIs, supported operations, and execution permissions.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class CommunicationIntent(str, Enum):
    INFORMATION_REQUEST = "INFORMATION_REQUEST"        # Where is X? How does X work? What is the rule?
    NAVIGATION_REQUEST = "NAVIGATION_REQUEST"          # Open X, Take me to X, Go to X
    ACTION_REQUEST = "ACTION_REQUEST"                  # I want to report X, Submit X, Apply for X
    PERSONAL_DATA_REQUEST = "PERSONAL_DATA_REQUEST"    # What is my attendance? Show my marks
    GENERAL_ACADEMIC = "GENERAL_ACADEMIC"              # Explain normalization, What is binary search
    STATUS_LOOKUP = "STATUS_LOOKUP"                    # Has my request been approved? Check ticket SR-123
    CANCEL_REQUEST = "CANCEL_REQUEST"                  # Cancel my booking, withdraw application
    AMBIGUOUS = "AMBIGUOUS"                            # Genuinely unclear, needs clarification
    CONVERSATION = "CONVERSATION"                      # Hello, thank you, who are you


class OperationType(str, Enum):
    VIEW = "view"
    SEARCH = "search"
    FILTER = "filter"
    NAVIGATE = "navigate"
    REPORT = "report"
    SUBMIT = "submit"
    CLAIM = "claim"
    CALCULATE = "calculate"
    BOOK = "book"
    CANCEL = "cancel"
    TRACK = "track"
    APPLY = "apply"
    VOTE = "vote"
    PAY = "pay"
    CLARIFY = "clarify"


# ---------------------------------------------------------------------------
# EXHAUSTIVE CAPABILITY-OPERATION REGISTRY (27 VERIFIED APPLICATION FEATURES)
# ---------------------------------------------------------------------------

APPLICATION_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "home": {
        "feature_id": "home",
        "name": "Helpdesk Home & Command Center",
        "category": "OVERVIEW",
        "description": "Central AI conversational workspace, proactive academic alerts, and quick action launcher.",
        "frontend_tab": "home",
        "frontend_route": "/?tab=home",
        "component": "CentralWorkspace",
        "backend_table": "conversations",
        "backend_tool": "nlu_engine",
        "keywords": ["home", "main page", "start", "menu", "command center", "dashboard", "overview", "helpdesk"],
        "supported_operations": [OperationType.VIEW, OperationType.NAVIGATE],
        "operations_matrix": {
            "view_overview": {
                "operation": OperationType.VIEW,
                "description": "View university summary, academic alerts, and today's schedule.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            },
            "navigate_home": {
                "operation": OperationType.NAVIGATE,
                "description": "Switch UI view to main helpdesk home.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /?tab=home"
            }
        },
        "requires_auth": False,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Go to Home",
        "guidance_text": "You can view your academic briefing and active helpdesk conversations in the **Helpdesk Home** tab."
    },

    "lost-and-found": {
        "feature_id": "lost-and-found",
        "name": "Lost & Found",
        "category": "LOST_AND_FOUND",
        "description": "Campus repository for reporting, listing, browsing, and claiming lost or found personal belongings.",
        "frontend_tab": "lost-and-found",
        "frontend_route": "/?tab=lost-and-found",
        "component": "LostAndFoundView",
        "backend_table": "lost_and_found",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "lost", "found", "lost and found", "lost & found", "lost item", "found item",
            "lost wallet", "lost phone", "lost id card", "found bag", "misplaced", "report found",
            "report lost", "claim item", "belongings", "keys", "wallet", "calculator", "drafter", "umbrella"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.FILTER,
            OperationType.NAVIGATE,
            OperationType.REPORT,
            OperationType.CLAIM
        ],
        "operations_matrix": {
            "view_listings": {
                "operation": OperationType.VIEW,
                "description": "Browse all active lost and found items posted across campus.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "fetchLostAndFoundItems('all')"
            },
            "filter_items": {
                "operation": OperationType.FILTER,
                "description": "Filter items specifically by 'lost' or 'found' status.",
                "required_params": ["type"],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "fetchLostAndFoundItems(filterType)"
            },
            "report_item": {
                "operation": OperationType.REPORT,
                "description": "Submit a new lost or found item report with location and contact information.",
                "required_params": ["type", "title", "description", "contact_info"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "reportLostAndFoundItem(studentId, type, title, description, tags, contactInfo)"
            },
            "claim_item": {
                "operation": OperationType.CLAIM,
                "description": "Claim a found item by verifying ownership and contacting the finder.",
                "required_params": ["item_id"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "claimLostAndFoundItem(itemId, studentId)"
            }
        },
        "requires_auth": False,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Lost & Found",
        "guidance_text": (
            "You can browse lost and found items or report an item you found in the **Lost & Found** section.\n"
            "• To report a found item: Open the Lost & Found section and click **'Report Item'** to describe the item and where you found it.\n"
            "• If you lost an item: Check the open listings or submit a lost item alert."
        )
    },

    "services": {
        "feature_id": "services",
        "name": "Student Services",
        "category": "SERVICES",
        "description": "Official administrative service requests including Bonafide Certificates, ID Card Replacement, Concession Forms, and Transcripts.",
        "frontend_tab": "services",
        "frontend_route": "/?tab=services",
        "component": "StudentServicesView",
        "backend_table": "service_requests",
        "backend_tool": "services_tool",
        "keywords": [
            "service request", "services", "bonafide", "study certificate", "id card replacement",
            "duplicate id", "transit pass", "railway concession", "bus concession", "transcript",
            "official transcript", "marks memo", "noc", "no objection certificate", "fee receipt"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE,
            OperationType.SUBMIT,
            OperationType.TRACK
        ],
        "operations_matrix": {
            "view_services": {
                "operation": OperationType.VIEW,
                "description": "View catalogue of available administrative services and SLAs.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/service-requests"
            },
            "submit_request": {
                "operation": OperationType.SUBMIT,
                "description": "Submit a formal service request for certificates, ID cards, or official documents.",
                "required_params": ["category", "title", "description"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "POST /api/v1/service-requests"
            },
            "track_request": {
                "operation": OperationType.TRACK,
                "description": "Check current status and assigned office of an existing ticket by tracking number.",
                "required_params": ["request_no"],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/service-requests/{request_no}"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Go to Student Services",
        "guidance_text": (
            "You can view, request, and track official university documents in the **Student Services** section.\n"
            "Available services include Bonafide Certificates, ID Card Replacement, Railway/Bus Concession Forms, and Transcripts."
        )
    },

    "attendance": {
        "feature_id": "attendance",
        "name": "Attendance",
        "category": "ATTENDANCE",
        "description": "Real-time subject-wise and aggregate attendance tracking, 75% cutoff monitoring, and recovery calculators.",
        "frontend_tab": "attendance",
        "frontend_route": "/?tab=attendance",
        "component": "AttendanceView",
        "backend_table": "attendance",
        "backend_tool": "attendance_tool",
        "keywords": [
            "attendance", "attendence", "classes held", "classes attended", "percentage",
            "75%", "condonation", "shortage", "bunk", "present", "absent", "attendance recovery",
            "detention", "consecutive classes"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.CALCULATE,
            OperationType.FILTER,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_attendance": {
                "operation": OperationType.VIEW,
                "description": "View overall attendance percentage and individual course records.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            },
            "calculate_recovery": {
                "operation": OperationType.CALCULATE,
                "description": "Calculate exact consecutive classes needed to reach 75% target.",
                "required_params": ["held", "attended"],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "calculateConsecutiveClassesNeeded(held, attended, target=0.75)"
            },
            "filter_course": {
                "operation": OperationType.FILTER,
                "description": "Filter attendance details for a specific course code or subject.",
                "required_params": ["course_code"],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard?course={course_code}"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Attendance Dashboard",
        "guidance_text": "You can track your live course attendance and simulate recovery classes in the **Attendance** tab."
    },

    "marks": {
        "feature_id": "marks",
        "name": "Marks & CGPA",
        "category": "MARKS",
        "description": "Continuous Internal Evaluation (CIE) scores, SGPA, CGPA, and semester-wise grade distributions.",
        "frontend_tab": "marks",
        "frontend_route": "/?tab=marks",
        "component": "MarksView",
        "backend_table": "marks",
        "backend_tool": "marks_tool",
        "keywords": [
            "marks", "score", "scores", "cgpa", "sgpa", "gpa", "grade", "grades",
            "internal marks", "cie marks", "mid marks", "quiz", "results"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.FILTER,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_marks": {
                "operation": OperationType.VIEW,
                "description": "View overall CGPA and assessment scores.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            },
            "filter_subject_marks": {
                "operation": OperationType.FILTER,
                "description": "View individual internal test and quiz breakdown for a subject.",
                "required_params": ["course_code"],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard?course={course_code}"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Marks & CGPA",
        "guidance_text": "Your latest Continuous Internal Evaluation (CIE) scores and cumulative CGPA are available in the **Marks & CGPA** tab."
    },

    "timetable": {
        "feature_id": "timetable",
        "name": "Timetable & Schedule",
        "category": "TIMETABLE",
        "description": "Weekly course timetable, class timings, assigned classrooms/labs, and course instructors.",
        "frontend_tab": "timetable",
        "frontend_route": "/?tab=timetable",
        "component": "TimetableView",
        "backend_table": "timetable",
        "backend_tool": "timetable_tool",
        "keywords": [
            "timetable", "schedule", "classes today", "next class", "room number", "period",
            "free period", "lab session", "faculty cabin", "class timing", "routine"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.FILTER,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_schedule": {
                "operation": OperationType.VIEW,
                "description": "View entire weekly class schedule with classrooms and faculties.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            },
            "filter_day": {
                "operation": OperationType.FILTER,
                "description": "View scheduled periods for a specific weekday (e.g. Monday).",
                "required_params": ["day_of_week"],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard?day={day_of_week}"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Open Timetable",
        "guidance_text": "Check your daily and weekly class routines, room numbers, and instructor allocations in the **Timetable** tab."
    },

    "exams": {
        "feature_id": "exams",
        "name": "Examinations & Assessments",
        "category": "EXAMS",
        "description": "Mid-term and end-semester examination timetables, seat allocations, exam venues, and hall tickets.",
        "frontend_tab": "exams",
        "frontend_route": "/?tab=exams",
        "component": "ExaminationsView",
        "backend_table": "exams",
        "backend_tool": "exams_tool",
        "keywords": [
            "exam", "exams", "examination", "examinations", "assessment", "assessments", "hall ticket", "admit card", "seat allocation",
            "exam date", "mid exam", "end semester", "seating", "venue"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.FILTER,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_exams": {
                "operation": OperationType.VIEW,
                "description": "View upcoming exam schedule, exam dates, time slots, and hall ticket status.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Exam Schedule",
        "guidance_text": "Access your official exam timetables, seating venues, and hall ticket status in the **Examinations** tab."
    },

    "fees": {
        "feature_id": "fees",
        "name": "Fees & Payments",
        "category": "FEES",
        "description": "Tuition, hostel, and transport fee demand ledgers, payment receipts, due dates, and fine schedules.",
        "frontend_tab": "fees",
        "frontend_route": "/?tab=fees",
        "component": "FeesView",
        "backend_table": "fees",
        "backend_tool": "fees_tool",
        "keywords": [
            "fee", "fees", "dues", "outstanding", "tuition fee", "hostel fee", "transport fee",
            "payment", "receipt", "fine", "penalty", "due date", "pay online", "installments"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.PAY,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_fees": {
                "operation": OperationType.VIEW,
                "description": "View total demand, paid amount, outstanding balance, and installment due dates.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/student/dashboard"
            },
            "pay_fee": {
                "operation": OperationType.PAY,
                "description": "Redirect to authorized university fee payment gateway.",
                "required_params": ["amount"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": False,
                "endpoint": "GET /?tab=fees&action=pay"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Check Fee Ledger",
        "guidance_text": "Check your outstanding fee balance, payment receipts, and upcoming due dates in the **Fee Status** tab."
    },

    "curriculum": {
        "feature_id": "curriculum",
        "name": "Curriculum & Degree Audit",
        "category": "CURRICULUM",
        "description": "B.Tech academic regulation curriculum roadmap, credit requirements, earned credits, and course electives.",
        "frontend_tab": "curriculum",
        "frontend_route": "/?tab=curriculum",
        "component": "CurriculumView",
        "backend_table": "curriculum",
        "backend_tool": "curriculum_tool",
        "keywords": [
            "curriculum", "syllabus", "credits", "credit requirement", "degree audit",
            "regulation", "r23", "electives", "open elective", "professional elective", "course structure"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_curriculum": {
                "operation": OperationType.VIEW,
                "description": "View total credits required, earned credits, remaining credits, and next semester courses.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "curriculum_tool.get_curriculum_summary(session)"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Open Curriculum & Syllabus",
        "guidance_text": "Degree credit requirements, academic regulation roadmap, and course electives are located in the **Curriculum** tab."
    },

    "hostel": {
        "feature_id": "hostel",
        "name": "Hostel & Mess Services",
        "category": "HOSTEL",
        "description": "Hostel room allocation, daily mess dining menu, warden contacts, outpass requests, and room maintenance.",
        "frontend_tab": "hostel",
        "frontend_route": "/?tab=hostel",
        "component": "HostelManagementView",
        "backend_table": "hostel_requests",
        "backend_tool": "hostel_tool",
        "keywords": [
            "hostel", "mess", "mess food", "room", "warden", "outpass", "curfew", "outing",
            "hostel complaint", "hostel leave", "laundry", "hot water"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SUBMIT,
            OperationType.TRACK,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_hostel": {
                "operation": OperationType.VIEW,
                "description": "View hostel room allocation, mess menu, and active requests.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getHostelRequests(studentId)"
            },
            "submit_outpass_or_complaint": {
                "operation": OperationType.SUBMIT,
                "description": "Submit a new outpass request or hostel room maintenance complaint.",
                "required_params": ["type", "details"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "createHostelRequest(studentId, type, details)"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Hostel Management",
        "guidance_text": "Hostel outpass requests, room maintenance complaints, and mess dining menus are handled in the **Hostel & Mess** section."
    },

    "transport": {
        "feature_id": "transport",
        "name": "Campus Transport & Bus Tracking",
        "category": "TRANSPORT",
        "description": "University bus fleet routes, pickup timings across Guntur/Vijayawada/Tenali, driver contacts, and live GPS tracking.",
        "frontend_tab": "transport",
        "frontend_route": "/?tab=transport",
        "component": "TransportView",
        "backend_table": "transportation_routes",
        "backend_tool": "transport_tool",
        "keywords": [
            "bus", "transport", "bus route", "bus timings", "bus stops", "bus fee", "transportation",
            "live bus tracking", "driver contact", "bus pass"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.TRACK,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_routes": {
                "operation": OperationType.VIEW,
                "description": "List all university bus routes, drivers, and ETA minutes.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getTransportRoutes()"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Transport Routes",
        "guidance_text": "Bus schedules, stop locations, route details, and live GPS coordinates are available in the **Transport (Live)** tab."
    },

    "library": {
        "feature_id": "library",
        "name": "Central Library",
        "category": "LIBRARY",
        "description": "Book catalog search, borrowed textbook records, due dates, overdue fines, and IEEE/ACM digital repository access.",
        "frontend_tab": "library",
        "frontend_route": "/?tab=library",
        "component": "LibraryView",
        "backend_table": "library_resources",
        "backend_tool": "library_tool",
        "keywords": [
            "library", "book", "books", "borrow", "due date", "return book", "renew book",
            "overdue", "journal", "ieee", "digital library", "textbook"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_borrowed_books": {
                "operation": OperationType.VIEW,
                "description": "View currently issued books and due dates.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "DataRepository.get_library_lended_books(session)"
            },
            "search_catalog": {
                "operation": OperationType.SEARCH,
                "description": "Search library resources catalog for course textbooks and papers.",
                "required_params": ["query"],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getLibraryResources()"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Access Central Library",
        "guidance_text": "Search textbook holdings, check borrowed book return deadlines, and access digital journals in the **Library** section."
    },

    "bookings": {
        "feature_id": "bookings",
        "name": "Facility Bookings",
        "category": "BOOKINGS",
        "description": "Campus facility reservations: Seminar Halls, Sports Grounds, Central Auditorium, and Project Labs.",
        "frontend_tab": "bookings",
        "frontend_route": "/?tab=bookings",
        "component": "BookingsView",
        "backend_table": "bookings",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "booking", "book facility", "seminar hall", "auditorium", "ground", "cricket ground",
            "lab booking", "reserve room", "conference hall", "slot booking", "cancel booking"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.BOOK,
            OperationType.CANCEL,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_facilities": {
                "operation": OperationType.VIEW,
                "description": "View all campus facilities, descriptions, and seating capacities.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getFacilities()"
            },
            "create_booking": {
                "operation": OperationType.BOOK,
                "description": "Reserve a facility for a specified date, start time, end time, and academic purpose.",
                "required_params": ["facility_id", "date", "start_time", "end_time", "purpose"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "createBooking(data)"
            },
            "cancel_booking": {
                "operation": OperationType.CANCEL,
                "description": "Cancel an existing facility booking reservation.",
                "required_params": ["booking_id"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "cancelBooking(bookingId, studentId)"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Facility Bookings",
        "guidance_text": "Reserve campus seminar halls, auditorium, or sports grounds for approved student events in the **Facility Booking** section."
    },

    "clubs": {
        "feature_id": "clubs",
        "name": "Clubs & Extracurriculars",
        "category": "CLUBS",
        "description": "Student clubs and societies directory (AI, Coding, Music, Drama, Dance, Photography) and recruitment forms.",
        "frontend_tab": "clubs",
        "frontend_route": "/?tab=clubs",
        "component": "ClubsView",
        "backend_table": "studentlife_club",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "club", "clubs", "extracurricular", "society", "ai club", "music club", "drama club",
            "dance club", "photography club", "join club", "audition"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.APPLY,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "browse_clubs": {
                "operation": OperationType.VIEW,
                "description": "List all active university student clubs, categories, and descriptions.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "DataRepository.get_clubs()"
            },
            "apply_club": {
                "operation": OperationType.APPLY,
                "description": "Submit application to join a specific student club.",
                "required_params": ["club_id"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "DataRepository.create_club_application(session, club_id, student_name)"
            }
        },
        "requires_auth": False,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Explore Student Clubs",
        "guidance_text": "Discover extracurricular activities, tech chapters, and submit club joining requests in the **Clubs & Communities** section."
    },

    "events": {
        "feature_id": "events",
        "name": "Event Registration",
        "category": "EVENTS",
        "description": "Campus cultural festivals, technical symposiums, hackathons, guest lectures, and student event passes.",
        "frontend_tab": "events",
        "frontend_route": "/?tab=events",
        "component": "EventRegistrationView",
        "backend_table": "calendar_events",
        "backend_tool": "events_tool",
        "keywords": [
            "event", "events", "hackathon", "fest", "symposium", "workshop", "webinar",
            "cultural fest", "technical fest", "register for event", "event pass"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SUBMIT,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_events": {
                "operation": OperationType.VIEW,
                "description": "List upcoming campus hackathons, workshops, and fests.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "DataRepository.get_upcoming_events()"
            },
            "register_event": {
                "operation": OperationType.SUBMIT,
                "description": "Register for a campus event to receive an entry pass.",
                "required_params": ["event_name"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "registerForEvent(studentId, eventName)"
            }
        },
        "requires_auth": False,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "View Upcoming Events",
        "guidance_text": "Browse upcoming workshops, hackathons, and cultural fests in the **Event Registration** tab."
    },

    "marketplace": {
        "feature_id": "marketplace",
        "name": "Student Marketplace",
        "category": "MARKETPLACE",
        "description": "Peer-to-peer campus marketplace for buying and selling textbooks, engineering drafters, lab coats, and cycles.",
        "frontend_tab": "marketplace",
        "frontend_route": "/?tab=marketplace",
        "component": "MarketplaceView",
        "backend_table": "marketplace_listings",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "marketplace", "buy", "sell", "second hand", "used book", "used drafter", "used cycle",
            "lab coat", "calculator sell", "student market"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.SUBMIT,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_listings": {
                "operation": OperationType.VIEW,
                "description": "Browse all peer-to-peer campus listings.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getMarketplaceListings()"
            },
            "create_listing": {
                "operation": OperationType.SUBMIT,
                "description": "Post a second-hand item for sale to campus peers.",
                "required_params": ["title", "category", "price"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "createMarketplaceListing(studentId, title, category, price)"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Marketplace",
        "guidance_text": "Buy and sell used books, lab coats, and campus essentials safely in the **Marketplace** tab."
    },

    "map": {
        "feature_id": "map",
        "name": "Campus Map & Navigation",
        "category": "MAP",
        "description": "Interactive university campus map, academic blocks (A-Block, U-Block, H-Block), departments, labs, and ATMs.",
        "frontend_tab": "map",
        "frontend_route": "/?tab=map",
        "component": "CampusMapView",
        "backend_table": "campus_locations",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "map", "campus map", "directions", "where is room", "where is block",
            "u block", "u-block", "ublock", "a block", "a-block", "ablock",
            "h block", "h-block", "hblock", "n block", "n-block", "nblock",
            "e block", "e-block", "eblock", "vignan vihar", "convocation hall",
            "convocation", "mhp canteen", "zest", "zest supermarket", "zest store", "chest supermarket", "ntr library",
            "library location", "canteen", "atm", "seminar hall location",
            "where is", "where is n-block", "where is n block", "where is a-block",
            "where is u-block", "where is h-block", "where is e-block",
            "navigation", "how to reach", "how do i get to", "way to", "directions to"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_locations": {
                "operation": OperationType.VIEW,
                "description": "View all campus buildings, blocks, coordinates, and features.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getCampusLocations()"
            }
        },
        "requires_auth": False,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Open Campus Map",
        "guidance_text": "Find classroom locations, faculty cabins, auditoriums, and canteen directions on the **Campus Map**."
    },

    "wellness": {
        "feature_id": "wellness",
        "name": "Student Wellness & Counseling",
        "category": "WELLNESS",
        "description": "Mental health support, confidential counseling appointments, wellness centers, and 24x7 crisis helplines.",
        "frontend_tab": "wellness",
        "frontend_route": "/?tab=wellness",
        "component": "WellnessView",
        "backend_table": "wellness_resources",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "wellness", "counseling", "counsellor", "mental health", "stress", "anxiety",
            "tele-manas", "wellness center", "confidential helpline", "psychologist"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_resources": {
                "operation": OperationType.VIEW,
                "description": "View confidential counseling center hours and national support lines.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getWellnessResources()"
            }
        },
        "requires_auth": False,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Access Wellness Support",
        "guidance_text": (
            "Access confidential student wellbeing and counseling assistance in the **Wellness** tab.\n"
            "• **Student Wellness Center:** Room 102, Student Activity Building\n"
            "• **National Tele-MANAS Helpline:** 14416 (24x7 Toll-Free)"
        )
    },

    "policies": {
        "feature_id": "policies",
        "name": "Policies & Academic Regulations",
        "category": "POLICIES",
        "description": "Official Academic Regulations R23, attendance rules, detention criteria, condonation, and grading scales.",
        "frontend_tab": "policies",
        "frontend_route": "/?tab=policies",
        "component": "PoliciesView",
        "backend_table": "policies",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "policy", "policies", "rules", "regulations", "academic ordinance", "bylaw",
            "condonation rule", "attendance rule", "malpractice", "detention policy"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "search_policies": {
                "operation": OperationType.SEARCH,
                "description": "Search academic regulations and statutory bylaws by keyword.",
                "required_params": ["query"],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "DataRepository.search_policies(query)"
            }
        },
        "requires_auth": False,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View University Policies",
        "guidance_text": "Read official academic regulations, condonation criteria, and university bylaws in the **Policies & Regulations** tab."
    },

    "circulars": {
        "feature_id": "circulars",
        "name": "Circulars & Notices",
        "category": "CIRCULARS",
        "description": "Official notices issued by the Registrar, Controller of Examinations, Dean Academics, and Vice-Chancellor.",
        "frontend_tab": "circulars",
        "frontend_route": "/?tab=circulars",
        "component": "CircularsView",
        "backend_table": "circulars",
        "backend_tool": "circulars_tool",
        "keywords": [
            "circular", "circulars", "notice", "notices", "notification", "announcement",
            "registrar notice", "official notice", "cie circular"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.FILTER,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_circulars": {
                "operation": OperationType.VIEW,
                "description": "View official administrative notices and university announcements.",
                "required_params": [],
                "requires_auth": False,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "circulars_tool.get_circulars_summary(session)"
            }
        },
        "requires_auth": False,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Circulars & Notices",
        "guidance_text": "Read official administrative notices and university announcements in the **Circulars & Notices** section."
    },

    "calendar": {
        "feature_id": "calendar",
        "name": "Academic Calendar",
        "category": "CALENDAR",
        "description": "Institutional calendar with semester start/end dates, CIE examination windows, national holidays, and fests.",
        "frontend_tab": "calendar",
        "frontend_route": "/?tab=calendar",
        "component": "CalendarView",
        "backend_table": "calendar_events",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "calendar", "academic calendar", "semester schedule", "holidays", "diwali holiday",
            "pongal vacation", "cie dates", "working days", "semester end"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_calendar": {
                "operation": OperationType.VIEW,
                "description": "View institutional schedule of academic milestones and holidays.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "fetchStudentSchedule(studentId)"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Open Academic Calendar",
        "guidance_text": "Check semester milestones, holiday schedules, and examination windows in the **Academic Calendar** tab."
    },

    "gamification": {
        "feature_id": "gamification",
        "name": "Achievements & Streaks",
        "category": "GAMIFICATION",
        "description": "Student karma points, attendance badges (75%+ Streak), learning rewards, and campus leaderboard.",
        "frontend_tab": "gamification",
        "frontend_route": "/?tab=gamification",
        "component": "GamificationView",
        "backend_table": "gamification",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "gamification", "points", "karma", "badges", "streak", "attendance streak",
            "rewards", "achievements", "leaderboard"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_badges": {
                "operation": OperationType.VIEW,
                "description": "View earned achievement badges, points, and consistency streaks.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getGamificationData(studentId)"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Achievements",
        "guidance_text": "Track your learning points, attendance streak badges, and campus rankings in the **Gamification** tab."
    },

    "career": {
        "feature_id": "career",
        "name": "Career Hub & Placements",
        "category": "CAREER",
        "description": "Placement statistics, company recruitment drives, aptitude training, and AI resume review tools.",
        "frontend_tab": "career",
        "frontend_route": "/?tab=career",
        "component": "CareerView",
        "backend_table": "resumes",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "placement", "placements", "job", "career", "recruiter", "package", "salary",
            "highest package", "amazon package", "t&p", "training and placement", "resume", "resume review"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SUBMIT,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_placements": {
                "operation": OperationType.VIEW,
                "description": "View placement statistics, visiting recruiters, and resume status.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getResumeData(studentId)"
            },
            "save_resume": {
                "operation": OperationType.SUBMIT,
                "description": "Save student skills and projects for AI placement review.",
                "required_params": ["skills", "projects"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "saveResumeData(studentId, skills, projects)"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Career Hub",
        "guidance_text": "Placement eligibility, visiting recruiters, and career preparation tools are available in the **Career Hub**."
    },

    "grievance": {
        "feature_id": "grievance",
        "name": "Student Grievance Redressal",
        "category": "GRIEVANCE",
        "description": "Statutory Student Grievance Redressal Committee (SGRC) portal under UGC 2023 regulations with 15-day SLA.",
        "frontend_tab": "services",
        "frontend_route": "/?tab=services",
        "component": "StudentServicesView",
        "backend_table": "studentlife_grievance",
        "backend_tool": "services_tool",
        "keywords": [
            "grievance", "complaint", "file complaint", "sgrc", "ombudsperson", "harassment",
            "unfair marking", "faculty complaint", "official grievance", "ragging", "anti-ragging",
            "antiragging", "bullying"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE,
            OperationType.SUBMIT,
            OperationType.TRACK
        ],
        "operations_matrix": {
            "view_grievance_portal": {
                "operation": OperationType.VIEW,
                "description": "View UGC SGRC statutory regulations and grievance procedure.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /?tab=services&view=grievance"
            },
            "lodge_grievance": {
                "operation": OperationType.SUBMIT,
                "description": "Lodge formal confidential complaint with UGC Ombudsman & SGRC.",
                "required_params": ["description"],
                "requires_auth": True,
                "requires_confirmation": True,
                "is_write": True,
                "endpoint": "submitAncComplaint(complaintText, studentId)"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Lodge Grievance",
        "guidance_text": (
            "To file an official student grievance under UGC Regulations (Clause 2.1), use the Grievance option in **Student Services**.\n"
            "• Statutory Ombudsman & SGRC reviews and resolves registered grievances within 15 working days.\n"
            "• For anti-ragging: Zero-tolerance policy is strictly enforced. National Anti-Ragging Helpline: 1800-180-5522 (Toll-Free, 24x7) | Email: helpline@antiragging.in"
        )
    },

    "polling": {
        "feature_id": "polling",
        "name": "Campus Polls & Voting",
        "category": "POLLING",
        "description": "Student voice platform for active campus surveys, feedback polls, and student council referendums.",
        "frontend_tab": "polling",
        "frontend_route": "/?tab=polling",
        "component": "PollingView",
        "backend_table": "campus_polls",
        "backend_tool": "knowledge_tool",
        "keywords": ["poll", "polls", "voting", "vote", "survey", "surveys", "referendum", "feedback poll"],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.VOTE,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_polls": {
                "operation": OperationType.VIEW,
                "description": "View active campus student body polls and referendums.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getCampusPolls()"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Open Campus Polls",
        "guidance_text": "Participate in active campus polls and institutional surveys in the **Campus Polls** section."
    },

    "alumni": {
        "feature_id": "alumni",
        "name": "Alumni Mentorship Network",
        "category": "ALUMNI",
        "description": "Directory of university alumni mentors offering career guidance, referrals, and industry insights.",
        "frontend_tab": "alumni",
        "frontend_route": "/?tab=alumni",
        "component": "AlumniView",
        "backend_table": "alumni_mentors",
        "backend_tool": "knowledge_tool",
        "keywords": ["alumni", "alumnus", "alumna", "alumni network", "alumni mentor", "graduates", "senior passout"],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.SEARCH,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_alumni": {
                "operation": OperationType.VIEW,
                "description": "Search directory of alumni mentors by company and domain.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "getAlumniMentors()"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "Explore Alumni Network",
        "guidance_text": "Connect with graduates working in top companies through the **Alumni Mentorship Network**."
    },

    "student-profile": {
        "feature_id": "student-profile",
        "name": "Student Profile & Advisors",
        "category": "PROFILE",
        "description": "Verified student identity record, academic enrollment info, parent contact, class teacher, and faculty mentor.",
        "frontend_tab": "student-profile",
        "frontend_route": "/?tab=student-profile",
        "component": "StudentProfileDrawer",
        "backend_table": "students",
        "backend_tool": "knowledge_tool",
        "keywords": [
            "profile", "my profile", "student profile", "roll number", "registration number",
            "id card details", "parent contact", "advisor", "class teacher", "mentor", "counsellor", "hod"
        ],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "view_profile": {
                "operation": OperationType.VIEW,
                "description": "View verified enrollment profile and assigned faculty advisors.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /api/v1/me"
            }
        },
        "requires_auth": True,
        "modifies_data": False,
        "requires_confirmation_for_write": False,
        "default_navigation_label": "View Student Profile",
        "guidance_text": "Your official student profile, enrollment details, and faculty advisors are listed in the **Student Profile** section."
    },

    "admin": {
        "feature_id": "admin",
        "name": "Administrative Control Panel",
        "category": "ADMIN",
        "description": "Administrative management console for faculty, department coordinators, and helpdesk officers.",
        "frontend_tab": "admin",
        "frontend_route": "/admin",
        "component": "AdminDashboardView",
        "backend_table": "admins",
        "backend_tool": "knowledge_tool",
        "keywords": ["admin", "admin panel", "administrator", "staff portal", "control panel", "management console", "officer portal"],
        "supported_operations": [
            OperationType.VIEW,
            OperationType.NAVIGATE
        ],
        "operations_matrix": {
            "admin_console": {
                "operation": OperationType.VIEW,
                "description": "Administrative dashboard for institutional management.",
                "required_params": [],
                "requires_auth": True,
                "requires_confirmation": False,
                "is_write": False,
                "endpoint": "GET /admin"
            }
        },
        "requires_auth": True,
        "modifies_data": True,
        "requires_confirmation_for_write": True,
        "default_navigation_label": "Open Admin Panel",
        "guidance_text": "The administrative control center is restricted to authorized faculty and staff officers."
    }
}


# ---------------------------------------------------------------------------
# SEMANTIC RESOLUTION LOGIC & PRECOMPILED MATCHERS
# ---------------------------------------------------------------------------

TYPO_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\battendence\b", re.IGNORECASE), "attendance"),
    (re.compile(r"\bfess\b", re.IGNORECASE), "fees"),
    (re.compile(r"\bhostle\b", re.IGNORECASE), "hostel"),
    (re.compile(r"\bbonafied\b", re.IGNORECASE), "bonafide"),
    (re.compile(r"\bcerificate\b", re.IGNORECASE), "certificate"),
    (re.compile(r"\bsyllubas\b", re.IGNORECASE), "syllabus"),
    (re.compile(r"\bfacalty\b", re.IGNORECASE), "faculty"),
]

# High-priority domain overrides compiled with word boundaries (exhaustive 27 capabilities)
DOMAIN_OVERRIDES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(?:ragging|anti-ragging|antiragging|sgrc|ombudsman|harassment|bullying|faculty complaint|unfair marking)\b", re.IGNORECASE), "grievance"),
    (re.compile(r"\b(?:counselor|counsellor|counseling|counselling|mental health|stress|stressed|depress(?:ed|ion)|overwhelmed|anxious|anxiety|suicid(?:e|al)|hopeless|tele-manas|telemanas|wellbeing|therapist|psychologist|talk to someone)\b", re.IGNORECASE), "wellness"),
    (re.compile(r"\b(?:condonation(?: fee)?|75% rule|detention|detained|attendance policy|attendance rule|attendance criteria|shortage of attendance|below 65%?|below 75%?|clause 4\.2|academic regulation|university regulation|ordinance|bylaws|dress code|refund policy)\b", re.IGNORECASE), "policies"),
    (re.compile(r"\b(?:bonafide|study certificate|id card replacement|duplicate id card|bus concession|railway concession|transcript|migration certificate|services desk)\b", re.IGNORECASE), "services"),
    (re.compile(r"\b(?:facility booking|seminar hall|cricket ground|book ground|auditorium booking|auditorium|lab booking|reserve slot|book room|booking|bookings|book the auditorium|reserve auditorium|book a slot|reserve ground)\b", re.IGNORECASE), "bookings"),
    (re.compile(r"\b(?:timetable|time table|schedule today|classes today|today'?s classes|next class|next period|which classroom|which room do i have|period schedule)\b", re.IGNORECASE), "timetable"),
    (re.compile(r"\b(?:cgpa|sgpa|gpa|mid marks|internal marks|lab marks|marks obtained|my marks|how many marks|scorecard|marksheet|grades?)\b", re.IGNORECASE), "marks"),
    (re.compile(r"\b(?:exam schedule|examination schedule|exam date|exam dates|next exam|seating arrangement|hall ticket|admit card|cie-?1|cie-?2|mid exam schedule|semester exam schedule|end sem exam)\b", re.IGNORECASE), "exams"),
    (re.compile(r"\b(?:marketplace|buy used|sell(?:ing)?|second\s*hand|used book|used books|used drafter|peer to peer|for sale|resell|buy cycle)\b", re.IGNORECASE), "marketplace"),
    (re.compile(r"\b(?:lost and found|lost & found|found item|lost item|lost my|found a|found something|report something if i found|report found|if i found|misplaced|someone found my)\b", re.IGNORECASE), "lost-and-found"),
    (re.compile(r"\b(?:campus placement|placements?|recruitment drive|package|highest package|average package|internship|t&p cell|training and placement|placement cell|companies visiting)\b", re.IGNORECASE), "career"),
    (re.compile(r"\b(?:hackathon|hackathons|vignan mahotsav|mahotsav|cultural fest|tech(?:nical)? fest|annual fest|freshers party|campus event|campus events|upcoming events|event registration)\b", re.IGNORECASE), "events"),
    (re.compile(r"\b(?:(?:student\s+)?clubs?|coding club|music club|dance club|robotics club|drama club|photography club|symphony club|nss|ncc|join club|club recruitment|extracurricular)\b", re.IGNORECASE), "clubs"),
    (re.compile(r"\b(?:[nauhe][- ]?block|[nauhe]block|vignan\s+vihar|convocation(?:\s+hall)?|ntr(?:\s+library)?|mhp(?:\s+canteen)?|zest(?:\s+supermarket)?|chest(?:\s+supermarket)?|second\s+gate|vlits|lara|campus\s+map|map\s+of\s+campus)\b|\b(?:where\s+is|where\s+are|directions?\s+to|how\s+to\s+reach|how\s+do\s+i\s+(?:reach|get\s+to|go\s+to)|how\s+can\s+i\s+(?:reach|get\s+to|go\s+to)|way\s+to|route\s+to|path\s+to|location\s+of)\b.*?\b(?:block|building|room|lab|gate|canteen|library|hall|mess|hostel|supermarket|ground|entrance|exit|ece|cse|aiml|law|bba|pharmacy|biotech)\b", re.IGNORECASE), "map"),
    (re.compile(r"\b(?:central library|library timings|library open|library close|reading room|issue book|renew book|library fine|library hours|sunday library|ntr library)\b", re.IGNORECASE), "library"),
    (re.compile(r"\b(?:hostel|mess food|hostel mess|curfew|outpass|outing|mess timings|boys hostel|girls hostel|hostel warden|hostel room)\b", re.IGNORECASE), "hostel"),
    (re.compile(r"\b(?:bus route|bus timings|college bus|bus pass|bus stop|evening bus|morning bus|transport)\b", re.IGNORECASE), "transport"),
    (re.compile(r"\b(?:academic calendar|semester start|semester end|diwali holiday|pongal vacation|holidays list|vacation dates|calendar)\b", re.IGNORECASE), "calendar"),
    (re.compile(r"\b(?:official circular|circulars|circular|university circular|latest circular|announcements?|notices?)\b", re.IGNORECASE), "circulars"),
    (re.compile(r"\b(?:voting|student vote|survey|surveys|polls|poll|vote|referendum)\b", re.IGNORECASE), "polling"),
    (re.compile(r"\b(?:alumnus|alumna|alumni|alumni network|senior passout|alumni mentors?)\b", re.IGNORECASE), "alumni"),
    (re.compile(r"\b(?:attendance|classes attended|classes held|bunk|attendance percentage|short attendance)\b", re.IGNORECASE), "attendance"),
    (re.compile(r"\b(?:fee balance|tuition fee|tuition|fees|fee due|fee payment|challan|fee receipt)\b", re.IGNORECASE), "fees"),
    (re.compile(r"\b(?:curriculum|degree audit|credits? required|credit requirement|credits? (?:do i )?need|r23 regulation|total credits|graduate credits|graduation requirement|credits? to graduate|syllabus)\b", re.IGNORECASE), "curriculum"),
    (re.compile(r"\b(?:gamification|karma points|attendance streak|leaderboard|my badges)\b", re.IGNORECASE), "gamification"),
    (re.compile(r"\b(?:student profile|my profile|profile details|roll number|parent contact|class teacher|faculty advisor|my mentor)\b", re.IGNORECASE), "student-profile"),
    (re.compile(r"\b(?:admin console|admin portal|admin panel|staff portal|management console)\b", re.IGNORECASE), "admin"),
]

# Precompiled per-capability keyword patterns for sub-millisecond scoring
CAPABILITY_KEYWORD_PATTERNS: List[Tuple[Dict[str, Any], List[Tuple[re.Pattern, int]]]] = []

def _init_capability_keyword_patterns() -> None:
    global CAPABILITY_KEYWORD_PATTERNS
    if not CAPABILITY_KEYWORD_PATTERNS:
        for cap in APPLICATION_CAPABILITIES.values():
            kw_patterns = []
            for kw in cap.get("keywords", []):
                pat = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
                weight = len(kw.split()) * 2
                kw_patterns.append((pat, weight))
            CAPABILITY_KEYWORD_PATTERNS.append((cap, kw_patterns))

_init_capability_keyword_patterns()


def find_matching_capability(query: str) -> Optional[Dict[str, Any]]:
    """
    Resolves the most relevant application capability based on word-boundary matching,
    common misspelling normalization, and domain intention.
    """
    q_norm = query.lower()

    # Normalization of common misspellings
    for pattern, replacement in TYPO_PATTERNS:
        q_norm = pattern.sub(replacement, q_norm)

    # Exact domain overrides for safety-critical and high-confusion capabilities
    for pattern, cap_key in DOMAIN_OVERRIDES:
        if pattern.search(q_norm):
            return APPLICATION_CAPABILITIES.get(cap_key)

    # Semantic keyword scoring using precompiled word-boundary matchers
    best_cap = None
    best_score = 0

    for cap, kw_patterns in CAPABILITY_KEYWORD_PATTERNS:
        score = 0
        for pat, weight in kw_patterns:
            if pat.search(q_norm):
                score += weight
        if score > best_score:
            best_score = score
            best_cap = cap

    return best_cap if best_score > 0 else None
