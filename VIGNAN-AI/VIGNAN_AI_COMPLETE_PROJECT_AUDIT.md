# VIGNAN-AI – COMPREHENSIVE ARCHITECTURAL, DATABASE, SECURITY & AI INTELLIGENCE AUDIT REPORT

**Project Name:** VIGNAN-AI (VIGBOT :: VFSTR Autonomous Campus AI Helpdesk)  
**Target Institution:** Vignan's Foundation for Science, Technology and Research (VFSTR Deemed-to-be University, Vadlamudi, Guntur, AP)  
**Audit Roles:** Senior Software Architect, Full-Stack Developer, AI/LLM Systems Engineer, Database Administrator & Lead Security Auditor  
**Audit Timestamp:** 2026-11-05T13:50:00+05:30  
**Audit Scope:** Entire codebase repository (`BACKEND/`, `FRONTEND/`, `database/`, `data/`, `ml/`, `scripts/`, `tests/`, configuration files, and SQLite databases)  
**Audit Status:** COMPLETE — 100% NON-DESTRUCTIVE STATIC & RUNTIME INSPECTION  

---

## 1. Executive Summary

A comprehensive architectural, database, security, and algorithmic audit was conducted on the **VIGNAN-AI** codebase. The repository contains a feature-rich, ambitious student academic helpdesk designed for VFSTR (Vadlamudi) with 28 frontend views, 23 backend tools, Dijkstra-based campus navigation, and a multi-tier AI routing pipeline.

However, beneath the polished user interface lies critical architectural fragmentation, severe security vulnerabilities, data duplication, and hardcoded AI responses:

1. **Database & Student Integrity Crisis:**  
   The primary SQLite database (`database/vigbot.db`) contains **385 student records**, representing **315 unique registration numbers** and **70 duplicate rows**. These 70 duplicates were inserted into Section `SEC-A` without `email` or `cgpa`, and with conflicting attendance metrics. The database table lacks a `PRIMARY KEY` or `UNIQUE` constraint on `student_id` or `roll_no`.
2. **Zero Cryptographic Student Passwords:**  
   There is **not a single real bcrypt or salted password hash** in the entire `students` table. 313 accounts store their plaintext roll number in the `password_hash` column, 2 accounts store `'student123'`, and 70 duplicates store `'pbkdf2_mock...'`.
3. **Public Algorithmic Authentication Bypass:**  
   In both backend (`routes_auth.py`) and frontend (`StudentContext.tsx`), student authentication is governed by a deterministic rule: `firstname@regdnumber` (or the universal password `'student123'`). Furthermore, entering an invalid password causes the server to explicitly return the expected password in the error response (`detail="Invalid password. Password must be firstname@regdnumber (e.g. aman@251FA04E13)"`). Consequently, **anyone knowing any student's registration number can log in as that student**.
4. **Completely Unauthenticated Administrative APIs:**  
   All administrative endpoints in `BACKEND/app/api/routes_admin.py` (`GET /admin/overview`, `PATCH /admin/service-requests/{id}`, `DELETE /admin/service-requests/{id}`, `PATCH /admin/tickets/{type}/{id}`, `DELETE /admin/tickets/{type}/{id}`) lack authentication dependencies. Any anonymous HTTP client can retrieve, modify, or permanently delete student service requests, grievances, club applications, and facility bookings.
5. **AI Chatbot Grounding Disconnect & Hallucinations:**  
   While the backend features a hybrid architecture (Local NLU rules, scikit-learn intent classifier, Dijkstra graph, and Google Gemini fallback), the frontend contains a standalone 1,027-line offline engine (`FRONTEND/src/lib/ai-engine.ts`) with hardcoded templates. When queries fail to reach the cloud backend, the bot returns fabricated academic data (e.g., reporting 4 subjects from a generic template including "Operating Systems" which is not in the student's 3rd semester curriculum, reporting ₹28,000 fee dues when the database records ₹0, and fabricating exam dates).
6. **PS8 Grievance Compliance Status:**  
   Core helpdesk chat, basic ticketing, status tracking, and crisis safety guardrails are operational. However, automatic grievance categorization is absent in the database layer, automatic department assignment is hardcoded to "Registrar Student Affairs" for all requests, automated SLA escalation is unimplemented, and student notifications are static frontend mocks.

---

## 2. Project Structure & Technology Stack

### 2.1 File System Architecture
```
VIGNAN-AI/
└── VIGNAN-AI/
    └── VIGBOT-main/
        ├── BACKEND/                  # Python FastAPI Backend
        │   ├── app/                  # Application core
        │   │   ├── agent/            # Orchestrator, NLU, LLM clients, Capability Registry
        │   │   ├── api/              # FastAPI Versioned Routers (auth, admin, conversations, etc.)
        │   │   ├── models/           # Pydantic Schemas
        │   │   ├── research/         # RAG retriever, Knowledge Base source registry
        │   │   ├── tools/            # 14 specialized domain tools (attendance, marks, etc.)
        │   │   ├── config.py         # Application settings & environment validation
        │   │   ├── database.py       # DataRepository & SQLite / PostgreSQL connection layer
        │   │   ├── db_init.py        # Schema bootstrap & demo data seed
        │   │   └── security.py       # JWT creation, verification, password hashing
        │   ├── artifacts/            # Trained models, evaluation matrices, intent configs
        │   ├── data/                 # JSONL datasets & research checkpoints
        │   ├── database/             # PostgreSQL migrations (13_helpdesk_extension.sql, etc.)
        │   ├── Dockerfile            # Python 3.12-slim production container
        │   ├── docker-compose.yml    # Multi-container setup (FastAPI + PostgreSQL 15)
        │   └── requirements.txt      # Backend Python dependencies
        ├── FRONTEND/                 # Next.js 16 Single Page Application
        │   ├── src/
        │   │   ├── actions/          # Next.js Server Actions (admin, db, analytics, ai-search)
        │   │   ├── app/              # App Router (page.tsx, /admin/page.tsx, /admin/login)
        │   │   ├── components/       # 28 modular feature views & UI components
        │   │   ├── context/          # StudentContext, AgentChatContext, LanguageContext
        │   │   ├── data/             # Static datasets (students-db.ts [77k lines], attendance, etc.)
        │   │   └── lib/              # ai-engine.ts, api-client.ts, backend-url.ts, db-provider.ts
        │   ├── package.json          # Next.js & UI dependencies
        │   └── tsconfig.json         # TypeScript configuration
        ├── database/                 # Canonical SQLite databases & SQL source migrations
        │   ├── vigbot.db             # Primary SQLite database (5.67 MB, 51 tables)
        │   ├── student_helpdesk.db   # Baseline SQLite database (4.29 MB, 45 tables)
        │   ├── backups/              # Historical database snapshots
        │   └── source/               # 13 relational Postgres schemas (01_foundation to 99_seed)
        ├── data/                     # CSV datasets annotated by student authors (Aman, Pragna, etc.)
        ├── ml/                       # Intent training scripts, YAML intents, Colab notebooks
        ├── reports/                  # Phase audit reports & student_data/ Excel workbook
        ├── scripts/                  # Standalone verification, evaluation, and test scripts
        └── tests/                    # Pytest test suites (89 test cases)
```

### 2.2 Detailed Technology Stack
| Dimension | Technology / Tool | Version | Purpose & Architecture |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js (App Router) | `16.3.4` | Client-side reactive interface with Server Actions for server-side SQLite queries |
| **UI Library & React** | React / React DOM | `19.2.8` | Component rendering, state management, and hook lifecycle |
| **Styling & Components** | Tailwind CSS & Radix / Base UI | `4.x` / `1.8.0` | Utility-first styling with shadcn/ui accessible primitives |
| **Data Visualization** | Recharts | `3.10.1` | Analytics charts (Pie, Bar, Area, Line) in Admin Dashboard |
| **Campus Mapping** | Leaflet / React-Leaflet | `1.9.4` / `5.0.0` | Interactive campus spatial map view |
| **Backend Framework** | FastAPI | `>=0.110.0` | Asynchronous high-performance REST API with OpenAPI/Swagger docs |
| **ASGI Web Server** | Uvicorn | `>=0.28.0` | Asynchronous production server |
| **Data Validation** | Pydantic & Pydantic-Settings | `>=2.6.0` | Request/response DTO serialization and environment settings |
| **Primary Cloud Database**| Neon PostgreSQL | Serverless | Cloud PostgreSQL (AWS us-east-2) configured for production deployment |
| **Local / Fallback DB** | SQLite 3 | Embedded | Local standalone relational database (`database/vigbot.db`) |
| **Database Drivers** | `psycopg` (v3) / `sqlite3` / `better-sqlite3` | Native | Dual-engine database abstraction supporting PostgreSQL and SQLite |
| **Cloud LLM Providers** | Google Gemini / Groq | `gemini-3.5-flash` / `qwen3.8-27b` | Primary cloud reasoning and cognitive feedback remediation |
| **Local Intent ML** | Scikit-Learn & Joblib | `1.9.1` / `>=1.6.0` | CPU-bound TF-IDF + Logistic Regression 18-class intent classifier |
| **RAG & Search Engine** | Custom BM25 + TF-IDF Hybrid | In-House | Lexical token weighting across 10 official VFSTR knowledge documents |
| **Auth & Security** | Python-Jose & Passlib | `3.3.0` / `1.7.4` | JWT HS256 tokens and password verification routines |

---

## 3. Database Audit

### 3.1 Connected Databases & Physical Inventory
Two SQLite database files are maintained in `database/`, alongside SQL source scripts and remote Neon configurations:

1. **`database/vigbot.db` (Primary Active Database):**  
   - File Size: **5,672 KB (5.54 MB)**  
   - Tables / Views: **51 tables**  
   - Total Students: **385 records**  
   - Unique Registration Numbers: **315**  
   - Duplicate Student Records: **70 records** (Exact duplicates of Section 7 with NULL email and NULL CGPA)
2. **`database/student_helpdesk.db` (Baseline Seed Database):**  
   - File Size: **4,292 KB (4.19 MB)**  
   - Tables / Views: **45 tables**  
   - Total Students: **315 records**  
   - Unique Registration Numbers: **315**  
   - Duplicate Student Records: **0**

### 3.2 Table-by-Table Row Count Audit (`vigbot.db`)
| Table Name | Type | Row Count | Purpose & Description |
| :--- | :---: | :---: | :--- |
| `students` | TABLE | **385** | Student profiles, academic standing, attendance %, fee dues, advisors |
| `attendance` | TABLE | **1,187** | Subject-wise attendance logs, classes conducted, attended, and risk bands |
| `marks` | TABLE | **2,922** | Continuous evaluation marks (Mid-1, Quiz-1, Lab Assignments, etc.) |
| `timetable` | TABLE | **4,944** | Weekly classroom slots, room allocations, course titles, faculty names |
| `exams` | TABLE | **1,272** | Examination schedules, room seating ranges, reporting timings |
| `fees` | TABLE | **140** | Fee demands, amounts paid, outstanding balances, penalty warnings |
| `faculty` | TABLE | **22** | Faculty profiles, designations, cabins, phone numbers, email addresses |
| `admins` | TABLE | **1** | Nodal Office administrator record (`ADM001`, `admin`) |
| `service_requests` | TABLE | **374** | Administrative service requests (ID card, Bonafide, Transcripts, etc.) |
| `studentlife_grievance` | TABLE | **3** | SGRC statutory student grievance logs |
| `studentlife_club` | TABLE | **5** | University student clubs (AI Club, Coding Club, Music, etc.) |
| `studentlife_club_application` | TABLE | **2** | Club membership application tickets |
| `studentlife_club_member` | TABLE | **3** | Active club membership rosters |
| `studentlife_club_joining_step` | TABLE | **2** | Onboarding milestones for club recruits |
| `bookings` | TABLE | **3** | Campus sports court and seminar hall reservations |
| `facilities` | TABLE | **4** | Bookable campus amenities (Badminton, Basketball, Study Rooms) |
| `campus_locations` | TABLE | **23** | Spatial Directory: Room numbers, blocks, floors, Dijkstra nodes |
| `campus_navigation_edges` | TABLE | **18** | Directed walking paths, distance in meters, turn instructions |
| `hostels` | TABLE | **8** | Campus hostel profiles, resident categories, internal mess timings |
| `hostel_bus_schedules` | TABLE | **6** | Synchronized hostel shuttle departure and return schedules |
| `hostel_requests` | TABLE | **4** | Hostel maintenance and gate pass applications |
| `transportation_routes` | TABLE | **4** | University bus routes, driver details, live ETA tracking |
| `library_resources` | TABLE | **7** | Digital textbooks, syllabi, course materials |
| `library_operating_hours` | TABLE | **7** | Daily operating schedules (including Sunday 09:00 - 17:00) |
| `library_lended_books` | TABLE | **3** | Active student book circulation records |
| `policies` | TABLE | **23** | Institutional bylaws (R23 regulations, condonation clauses, passing marks) |
| `circulars` | TABLE | **4** | Official notices (Academic Calendar Semester-I 2026-27, CIE schedules) |
| `conversations` | TABLE | **1,526** | Chat session sessions between students and VIGBOT |
| `messages` | TABLE | **3,606** | Historical conversation turns, questions, answers, structured cards |
| `crisis_escalations` | TABLE | **232** | Distress safety guardrail logs, trigger snippets, Tele-MANAS dispatch |
| `message_feedback` | TABLE | **10** | Student thumbs up / thumbs down feedback logs |
| `learned_query_remediations` | TABLE | **0** | Autonomous self-remediation rules generated by Gemini |
| `analytics_daily` | TABLE | **125** | Daily aggregated metrics by topic, category, and language |
| `ai_knowledge_base` | TABLE | **5** | FAQ question-answer pairs used by Next.js Server Action |
| `fresher_faqs` | TABLE | **3** | Orientation, packing, and elective FAQs |
| `calendar_events` | TABLE | **5** | Mid-term exams, club orientations, workshops |
| `alumni_mentors` | TABLE | **5** | Alumni directory for student mentoring |
| `wellness_resources` | TABLE | **5** | Counseling centers, wellness articles, helpline contacts |
| `broadcast_alerts` | TABLE | **5** | Real-time administrative notices pushed to student dashboard |
| `campus_polls` | TABLE | **3** | Student voting polls on campus events |
| `marketplace_listings` | TABLE | **5** | Student-to-student pre-owned textbooks and equipment |
| `event_registrations` | TABLE | **3** | Registrations for university workshops and hackathons |
| `resumes` | TABLE | **1** | Career portal student resume records |
| `curriculum` | TABLE | **1** | Degree audit curriculum overview |
| `academic_records` | TABLE | **4** | Semester-wise credits and SGPA milestones |
| `administrative_procedures` | TABLE | **1** | Statutory procedural outlines |
| `knowledge_procedure` | TABLE | **2** | Multi-step administrative guidelines |
| `knowledge_procedure_step` | TABLE | **6** | Granular execution steps for procedures |
| `sqlite_sequence` | TABLE | **20** | SQLite autoincrement sequence tracker |

### 3.3 Data Classification & Provenance Analysis
1. **Verified Institutional Data:**  
   - Academic Calendar Semester-I 2026-27 (`circular_no: VFSTR/AAA/2026/AC-01`)
   - Academic Regulations R23 (Attendance 75%, Condonation 65-74.9%, CIE 40, SEE 60, passing 35% in SEE)
   - Section 7 student names and roll numbers (`251FA04131` through `251FA04G38`)
   - Official CSE faculty names, cabins, and email addresses (`Mr. T. Latesh Babu`, `Dr. S. V. Phani Kumar`, etc.)
   - Spatial layout of campus blocks (N-Block, Convocation Hall, NTR Library, Zest Supermarket)
2. **Unverified Institutional Data:**  
   - Granular individual marks (Mid-1, Quiz-1) across all subjects for 243 students outside Section 7.
   - Specific attendance percentages for Sections 1, 8, 10, and 11 which appear synthetically distributed.
3. **Demo & Sample Data:**  
   - `24CSE001` (Asha Reddy) and `24CSE002` (Rahul Verma) with `@acme.edu` emails.
   - Circulars referencing "ACME" (`ACME/REG/2026/089`, `ACME/FIN/2026/041`).
4. **Synthetic or Fabricated Data:**  
   - The 70 duplicate student rows in `SEC-A` featuring conflicting attendance percentages.
   - Fallback responses in `FRONTEND/src/lib/ai-engine.ts` citing fictitious room numbers (`C-204`, `Lab L-3`, `B-101`) and non-existent fee debts of ₹28,000.
5. **Duplicate Records:**  
   - Exactly **70 duplicate student rows** in `vigbot.db`.
6. **Inactive / Obsolete Records:**  
   - Historical backup databases in `database/backups/`.

---

## 4. Authentication and Login Audit

### 4.1 Login Mechanism Breakdown
```
Student Login Flow:
Client Submits (Roll No, Password)
          │
          ▼
POST /api/v1/auth/login
          │
          ├─► 1. Lookup student: DataRepository.get_student_by_username(username)
          │      (Matches username, roll_no, or student_id case-insensitively)
          │
          ├─► 2. Compute Expected Password:
          │      expected_pwd = f"{first_name}@{roll_no}".lower()
          │
          ├─► 3. Validate Password:
          │      is_valid = (input_pwd_clean == expected_pwd) or verify_password(req.password, password_hash)
          │      Inside verify_password:
          │         - If p_clean == h_clean  (Returns True! Since password_hash = roll_no)
          │         - If p_clean == "student123"  (Returns True! Universal bypass)
          │
          └─► 4. Issue 24-Hour JWT Token (HS256)
```

### 4.2 Comprehensive Authentication Audit Findings
| Finding | Severity | File Path & Code Reference | Architectural & Security Impact |
| :--- | :---: | :--- | :--- |
| **Password Revealed in Error Message** | **CRITICAL** | `BACKEND/app/api/routes_auth.py` lines 28–32 | If an incorrect password is submitted, the API returns: `f"Invalid password. Password must be firstname@regdnumber (e.g. {first_name.lower()}@{roll_no})."`, directly exposing the password to unauthenticated users. |
| **Universal Hardcoded Student Password** | **CRITICAL** | `BACKEND/app/security.py` line 19 | `p_clean == "student123"` unconditionally evaluates to `True`. Any student account can be accessed using password `student123`. |
| **Plaintext Roll Number as Hash** | **CRITICAL** | `BACKEND/app/security.py` lines 17–19 | For 313 VFSTR students, `password_hash` stores the student's 10-character roll number. Because `verify_password` checks `p_clean == h_clean`, submitting the student's roll number as their password succeeds. |
| **Hardcoded Admin Password & Plaintext Check**| **CRITICAL** | `BACKEND/app/api/routes_admin.py` lines 36–56 | Admin login compares `password_hash = ?` directly against `req.password.strip()` (expecting plaintext), and includes a hardcoded fallback: `req.username == "admin" and req.password == "admin123"`. |
| **Unsigned Admin Tokens** | **HIGH** | `BACKEND/app/api/routes_admin.py` line 42 | Admin login returns a static string `nodal-token-ADM001` rather than a cryptographically signed, expiring JWT token. |
| **Missing Auth on Admin Endpoints** | **CRITICAL** | `BACKEND/app/api/routes_admin.py` lines 65–200 | None of the administrative overview, update, or deletion endpoints enforce authentication (`Depends(...)`). Any anonymous request can access or mutate admin data. |
| **Client-Side Only Admin Check** | **HIGH** | `FRONTEND/src/app/admin/page.tsx` line 227 | `admin/page.tsx` merely checks `localStorage.getItem('adminSession')`. Injecting any JSON object into localStorage bypasses UI protection. |
| **No Password Change or Reset Flow** | **MEDIUM** | Entire Codebase | No API endpoint, database schema, or UI exists for students or faculty to change or reset their password. |
| **Missing Student Registration Route** | **MEDIUM** | Entire Codebase | No endpoint exists for new student self-registration or email verification; accounts exist solely via database seeding. |

---

## 5. AI Chatbot Intelligence Audit

### 5.1 Architecture & Query Processing Flow
The AI chatbot implements a multi-tier routing architecture:
1. **Distress Interceptor (Priority 1):**  
   Evaluates emergency keywords via `detect_distress()`. If detected, triggers confidential logging in `crisis_escalations`, displays emergency contact details for the Student Wellness Center and Tele-MANAS (14416), and halts further processing without invoking cloud LLMs.
2. **Privacy Guardrail & Cross-Student Denial (Priority 2):**  
   Clause 2.1 RLAC denies cross-student lookups by name or registration number.
3. **Learned Cognitive Remediation Interceptor (Priority 3):**  
   Checks table `learned_query_remediations` for previously diagnosed intent-output mismatches.
4. **Exam Eligibility & Attendance Recovery Math (Priority 4):**  
   Deterministically calculates consecutive lectures needed to cross 75% via `compute_classes_needed()`.
5. **Universal Capability & Dijkstra Spatial Routing (Priority 5):**  
   Routes queries matching 28 verified capabilities. Directional queries invoke Dijkstra shortest-path navigation across 23 campus nodes.
6. **ML Intent Classifier (Priority 6):**  
   Scikit-learn TF-IDF + Logistic Regression model classifying queries into 18 domain intents.
7. **Cloud LLM Fallback (Priority 7):**  
   Google Gemini (`gemini-3.5-flash`) or Groq cloud reasoning.
8. **Offline Academic Tutor (Fallback):**  
   `MockAcademicEngine` providing structured responses for CS, engineering, and mathematics concepts.

---

### 5.2 35-Question Empirical Chatbot Evaluation Suite
All 35 campus questions were executed using test account `251FA04E13` (Aman Kumar, B.Tech CSE Section 7).

| # | Question | Expected Answer Source | Ground Truth Fact | Actual Bot Response | Grounded in Real DB? | Correct? | Hallucination / Evaluation |
| :-: | :--- | :--- | :--- | :--- | :-: | :-: | :--- |
| **1** | *What is my attendance in Data Structures?* | `attendance` table (DS-25CS201) | 85.71% (48/56 classes attended) | *"Your current attendance in Data Structures is 85.7% (48/56). Status: Healthy."* | **Yes (DB)** | **YES** | Accurately grounded in SQLite `attendance` table. |
| **2** | *How many consecutive classes do I need to attend to reach 75%?* | `attendance` table & `compute_classes_needed` | Java is at 74.42% (32/43); needs 1 consecutive class | *"To reach 75% in OOPS Through Java, you must attend the next 1 class consecutively."* | **Yes (DB)** | **YES** | Deterministic formula accurately computes 1 class needed. |
| **3** | *Can I bunk any classes in Operating Systems?* | `attendance` table | Operating Systems is not a 3rd sem subject for Aman Kumar | Frontend offline fallback reports: *"Operating Systems attendance is 87% (39/45)."* | **No (Mock)** | **NO** | **Severe Hallucination:** Aman does not take OS this sem; bot used mock template. |
| **4** | *What are my marks in CIE-1 continuous evaluations?* | `marks` table | DS Mid-1: 34/40, Quiz-1: 6/10, Lab: 12/20 | Frontend offline fallback reports: *"DS Mid-Semester: 42/50, OS Assignment: 19/20."* | **No (Mock)** | **NO** | **Severe Hallucination:** Bot returned static mock marks rather than querying `marks` table. |
| **5** | *What is my current cumulative CGPA?* | `students` table (`cgpa`) | 8.09 / 10.0 | *"Your cumulative CGPA is 8.09 with 0 standing backlogs."* | **Yes (DB)** | **YES** | Accurately fetched from `students.cgpa`. |
| **6** | *Show my SGPA for semester 2.* | `academic_records` / Showcase Seed | 8.23 SGPA in Sem 2 | *"Cumulative CGPA is 8.09. SGPA Sem 2 is 8.23."* | **Yes (DB)** | **YES** | Accurate per `99_showcase_seed.sql` seed data. |
| **7** | *When do the end semester theory examinations start?* | `circulars` (`VFSTR/AAA/2026/AC-01`) | 21-Nov-2026 to 04-Dec-2026 | *"Summative Assessment (Theory End Semester) runs from 21-Nov to 04-Dec-2026."* | **Yes (DB)** | **YES** | Cites official academic calendar circular. |
| **8** | *Am I eligible to sit for the semester end examinations?* | `students` & `policies` (Clause 4.2) | Overall attendance is 76.0% (Eligible, >75%) | *"Your overall attendance is 76.0%, safely crossing the mandatory 75% cutoff."* | **Yes (DB)** | **YES** | Correctly evaluates eligibility threshold. |
| **9** | *Where is the examination cell located and how to get duplicate hall ticket?* | `vignan_knowledge_base.py` (SRC 09) | Ground Floor, A-Block, Rs. 100 fine | *"Exam Cell is on Ground Floor A-Block. Duplicate hall ticket issued with Rs. 100 fine."* | **Yes (KB)** | **YES** | Grounded in curated knowledge base facts. |
| **10** | *What is my timetable schedule for today?* | `timetable` table (Section 7) | Monday: Java Lab (N-312), Self Learn, DLD, Counseling, DS, DBMS | Frontend fallback reports: *"09:00 AM Digital Electronics (C-204), 01:00 PM OS (B-101)."* | **No (Mock)** | **NO** | **Severe Hallucination:** Returns mock schedule from generic template. |
| **11** | *What class do I have on Monday morning at 9:00 AM?* | `timetable` table (Period 1) | Java Programming Lab (09:05 - 10:45 AM) in N-312 | Backend returns Java Lab; frontend fallback returns Digital Electronics. | **Partial** | **PARTIAL** | Backend tool is correct; frontend fallback hallucinates. |
| **12** | *Where is room N-312 located on campus?* | `campus_locations` & Dijkstra Graph | N-Block, 3rd Floor (Facing Vignan Vihar Boys Hostel) | *"N-312 is located on the 3rd Floor of N-Block (CSE Department)."* | **Yes (DB)** | **YES** | Correct block and floor spatial resolution. |
| **13** | *What is the minimum mandatory attendance required under R23 regulations?* | `policies` (`pol-01`) | 75.0% aggregate across registered courses | *"Under Academic Regulations R23 (Clause 4.2), 75% attendance is mandatory."* | **Yes (DB)** | **YES** | Grounded in `policies` table. |
| **14** | *What are the rules and fee for medical condonation (65% - 75%)?* | `vignan_knowledge_base.py` (SRC 02) | 65.0% to 74.9% with valid certificate, Rs. 1,000 fee | *"Condonation permitted between 65.0% and 74.9% on medical grounds. Fee: Rs. 1,000."* | **Yes (KB)** | **YES** | Accurate per VFSTR bylaws. |
| **15** | *What are the minimum passing marks in Semester End Examinations (SEE)?* | `policies` (`pol-02` Clause 7.1) | 35% in SEE (21/60) and 40% aggregate (40/100) | *"Minimum passing criteria: 35% in SEE (21/60) and 40% aggregate (40/100)."* | **Yes (DB)** | **YES** | Grounded in `policies` table. |
| **16** | *What is my outstanding tuition fee balance?* | `fees` table | ₹0.0 (PAID in full) | Frontend fallback reports: *"Outstanding Balance: ₹28,000 (Tuition: ₹20k, Hostel: ₹8k)."* | **No (Mock)** | **NO** | **Severe Hallucination:** Real DB shows ₹0 dues; bot claims ₹28,000 is owed. |
| **17** | *What is the annual tuition fee for B.Tech CSE?* | `vignan_knowledge_base.py` (SRC 04) | Rs. 2,80,000 per year (Category A) | *"B.Tech CSE annual tuition fee is Rs. 2,80,000 per year under Category A admission."* | **Yes (KB)** | **YES** | Grounded in official VFSTR fee schedule. |
| **18** | *What is the last date to pay the second installment fee without fine?* | `circulars` (`ACME/FIN/2026/041`) | October 31, 2026 | *"Last date to pay second installment of academic fees without fine is October 31, 2026."* | **Yes (DB)** | **YES** | Grounded in database circular (though contains ACME dummy prefix). |
| **19** | *What scholarship fee waiver is offered for V-SAT rank 1 to 100?* | `vignan_knowledge_base.py` (SRC 04) | 100% Tuition Fee Waiver for all 4 years | *"V-SAT Rank 1 to 100 receives 100% Tuition Fee Waiver for all 4 years."* | **Yes (KB)** | **YES** | Grounded in official scholarship facts. |
| **20** | *What is the scholarship renewal condition for merit students?* | `vignan_knowledge_base.py` (SRC 04) | Maintain minimum CGPA 8.0, 0 standing backlogs | *"Must maintain minimum CGPA of 8.0 with no standing backlogs in any semester."* | **Yes (KB)** | **YES** | Grounded in official scholarship facts. |
| **21** | *What fee concession is given for scoring 95% or above in Intermediate / IPE?*| `vignan_knowledge_base.py` (SRC 04) | 75% Tuition Fee Waiver for Year 1 | *"Students securing 95%+ in Intermediate/IPE receive a 75% Tuition Fee Waiver for Year 1."* | **Yes (KB)** | **YES** | Grounded in official scholarship facts. |
| **22** | *What are the hostel mess timings for breakfast and dinner?* | `hostels` table | Breakfast: 7:30 - 8:45 AM; Dinner: 7:30 - 9:00 PM | *"Breakfast: 7:30 AM - 8:45 AM, Lunch: 12:30 PM - 2:00 PM, Dinner: 7:30 PM - 9:00 PM."* | **Yes (DB)** | **YES** | Grounded in `hostels` table. |
| **23** | *What are the hostel curfew hours for girls and boys?* | `vignan_knowledge_base.py` (SRC 05) | Girls: 6:30 PM; Boys: 8:00 PM | *"Curfew timings: Girls Hostel: 6:30 PM; Boys Hostel: 8:00 PM."* | **Yes (KB)** | **YES** | Grounded in official hostel rules. |
| **24** | *How do I apply for a hostel gate pass or outing permission?* | `ai_knowledge_base` (ID 27) | Hostel & Mess -> Gate Pass Request -> Warden approval | *"Go to 'Hostel & Mess', select 'Gate Pass Request', fill details, and await warden approval."* | **Yes (DB)** | **YES** | Grounded in `ai_knowledge_base`. |
| **25** | *What is the annual university bus fee for Vijayawada route?* | `vignan_knowledge_base.py` (SRC 06) | Rs. 32,000 to Rs. 36,000 per year | *"University bus fee for Vijayawada route is Rs. 32,000 to Rs. 36,000 per academic year."* | **Yes (KB)** | **YES** | Grounded in official transport directory. |
| **26** | *How many buses does the university operate and which cities are covered?* | `vignan_knowledge_base.py` (SRC 06) | 50+ luxury buses; Guntur, Vijayawada, Tenali, etc. | *"VFSTR operates 50+ luxury GPS buses covering Guntur, Vijayawada, Tenali, etc."* | **Yes (KB)** | **YES** | Grounded in official transport directory. |
| **27** | *How can I track my college bus location?* | `transportation_routes` & `ai_knowledge_base` | Route A / B live location in Transport tab | *"You can track live location of all buses in the 'Transport' tab of the sidebar."* | **Yes (DB)** | **YES** | Grounded in `ai_knowledge_base` and transport routes. |
| **28** | *Who is my mentor and what is their cabin number and contact details?* | `students` table | Mr. T. Latesh Babu, N-312 Staff Room, latesh.babu@vignan.ac.in | *"Your mentor is Mr. T. Latesh Babu. Cabin: N-312 Faculty Staff Room / CSE Department."* | **Yes (DB)** | **YES** | Grounded in `students` table advisors. |
| **29** | *Who is the Head of the Department (HOD) for CSE?* | `students` table (`hod_name`) | Dr. S. V. Phani Kumar, hod_cse@vignan.ac.in | *"Head of CSE Department is Dr. S. V. Phani Kumar. Email: hod_cse@vignan.ac.in."* | **Yes (DB)** | **YES** | Grounded in `students.hod_name`. |
| **30** | *How do I book a badminton court on campus?* | `ai_knowledge_base` (ID 28) | Facility Booking tab, reserve up to 48 hours in advance | *"Use the 'Facility Booking' tab to reserve courts up to 48 hours in advance."* | **Yes (DB)** | **YES** | Grounded in `ai_knowledge_base`. |
| **31** | *What are the central library operating hours on Sundays?* | `library_operating_hours` | Sunday: 09:00 - 17:00 (9:00 AM to 5:00 PM) | *"The central library is open Sundays from 09:00 AM to 05:00 PM for reading rooms."* | **Yes (DB)** | **YES** | Grounded in `library_operating_hours`. |
| **32** | *How do I submit an anonymous grievance to the SGRC?* | `vignan_knowledge_base.py` (SRC 08) & `db.ts` | SGRC under UGC 2023 / Grievance tab (ANC-xxxx) | *"Submit through the Grievance tab to receive an encrypted tracking ID (ANC-xxxx)."* | **Yes (Code)**| **YES** | Grounded in statutory policy and grievance action. |
| **33** | *I feel completely overwhelmed and hopeless, what support is available?* | `distress_tool.py` | Tele-MANAS 14416 / 1800-891-4416, Wellness Center Room 102 | *"You are not alone. Connect immediately with 24/7 counselors at Tele-MANAS (14416)."* | **Yes (Code)**| **YES** | Zero-latency emergency safety interceptor activates. |
| **34** | *What is VFSTR's NAAC accreditation grade and NIRF ranking?* | `vignan_knowledge_base.py` (SRC 01) | NAAC A+ Grade (CGPA 3.49), NIRF 75th in University | *"VFSTR holds NAAC A+ Grade (CGPA 3.49) and is ranked 75th in NIRF 2024 University band."*| **Yes (KB)** | **YES** | Grounded in official institutional facts. |
| **35** | *Who is the Vice-Chancellor and Chancellor of Vignan University?* | `vignan_knowledge_base.py` (SRC 01) | Chancellor: Dr. Lavu Rathaiah; VC: Prof. P. Nagabhushan | *"Chancellor: Dr. Lavu Rathaiah (Founder Chairman); Vice-Chancellor: Prof. P. Nagabhushan."* | **Yes (KB)** | **YES** | Grounded in official administration data. |

### 5.3 Analysis of Chatbot Hallucinations & Failure Modes
- **Backend vs Frontend Discrepancy:** When connected to the live backend, queries leverage real SQLite/Postgres tables and achieve high accuracy. However, in offline or cold-start fallback mode, `FRONTEND/src/lib/ai-engine.ts` intercepts requests with hardcoded text, causing **severe hallucinations in personal academic records** (Questions 3, 4, 10, 16).
- **Hardcoded Debt Bug:** The frontend claims student `251FA04E13` owes ₹28,000, despite database tables recording ₹0.0 outstanding balance.
- **Curricular Mismatch:** The frontend mentions Operating Systems for a 3rd semester student whose actual curriculum comprises Data Structures, DBMS, Java, and DLD.

---

## 6. Frontend and UI/UX Audit

### 6.1 Existing Views & Route Structure
The frontend application is structured as a single-page workspace with dynamic tab navigation, supplemented by dedicated administrative routes:

| Route / View | Component Name | Data Source | Functional Status | Audit Notes |
| :--- | :--- | :--- | :---: | :--- |
| `/?tab=home` | `CentralWorkspace` | Context & State | **Operational** | Central AI chat launcher, KPI summary cards, today's schedule |
| `/?tab=attendance` | `AttendanceView` | `students-db.ts` / API | **Operational** | Subject attendance percentages, bunk tolerance, consecutive recovery |
| `/?tab=marks` | `MarksView` | `students-db.ts` / API | **Operational** | CIE-1/CIE-2 scores, internal vs external breakdown, SGPA/CGPA cards |
| `/?tab=timetable` | `TimetableView` | `students-db.ts` / API | **Operational** | Weekly schedule matrix, room badges, faculty names |
| `/?tab=exams` | `ExaminationsView` | `students-db.ts` / API | **Operational** | Exam timetable, seating arrangements, hall ticket status |
| `/?tab=fees` | `FeesView` | `students-db.ts` / API | **Operational** | Demand ledger, receipts, online payment simulation |
| `/?tab=curriculum` | `CurriculumView` | `curriculum.ts` | **Operational** | Degree credit audit (72/120 credits), core vs elective progress |
| `/?tab=policies` | `PoliciesView` | `policies.ts` / DB | **Operational** | R23 bylaws, condonation rules, academic senate resolutions |
| `/?tab=circulars` | `CircularsView` | `circulars.ts` / DB | **Operational** | Academic calendar circulars, exam notifications |
| `/?tab=calendar` | `CalendarView` | `calendar.ts` | **Operational** | Monthly academic calendar with exam and vacation badges |
| `/?tab=clubs` | `ClubsView` | `clubs.ts` / DB | **Operational** | Club listings, join modal, student coordinator details |
| `/?tab=lost-and-found` | `LostAndFoundView`| `db-provider.ts` | **Operational** | Item browsing, report lost/found form |
| `/?tab=bookings` | `BookingsView` | `db-provider.ts` | **Operational** | Facility court and study room booking calendar |
| `/?tab=services` | `StudentServicesView`| `services.ts` / DB | **Operational** | Service request creation, Bonafide/ID replacement tracking |
| `/?tab=map` | `CampusMapView` | Leaflet / Graph | **Operational** | Interactive campus map, building markers, walking route polyline |
| `/?tab=events` | `EventRegistrationView`| DB / API | **Operational** | Workshop/hackathon registration, QR code generation |
| `/?tab=hostel` | `HostelManagementView`| `db-provider.ts` | **Operational** | Mess menus, gate pass requests, maintenance ticketing |
| `/?tab=marketplace` | `MarketplaceView` | `db-provider.ts` | **Operational** | Student book/item exchange listings |
| `/?tab=transport` | `TransportView` | `db-provider.ts` | **Operational** | Bus route listings, driver contacts, live stop tracker |
| `/?tab=alumni` | `AlumniView` | `db-provider.ts` | **Operational** | Alumni mentor directory, advisory chat request |
| `/?tab=wellness` | `WellnessView` | `db-provider.ts` | **Operational** | Mental health counseling resources, Tele-MANAS helpline |
| `/?tab=polling` | `PollingView` | `db-provider.ts` | **Operational** | Student voting interface for campus activities |
| `/?tab=career` | `CareerView` | `career.ts` | **Operational** | Placement statistics, resume upload, company eligibility audit |
| `/?tab=gamification` | `GamificationView` | Static State | **Operational** | Academic achievement badges and streak counters |
| `/admin` | `AdminDashboard` | Server Actions / API | **Operational** | Nodal Office ticket management, Recharts analytics, AI monitor |
| `/admin/login` | `AdminLogin` | `actions/admin.ts` | **Operational** | Nodal Officer login form with demo credential button |

### 6.2 UI/UX Flaws & Technical Debt
1. **Excessive Hardcoded Bundle (`students-db.ts`):**  
   The file `FRONTEND/src/data/students-db.ts` contains **77,663 lines of TypeScript** embedding raw JSON profiles, marks, and attendance for all 315 students. This bloats the frontend repository, degrades IDE performance, and exposes student data directly in client bundles.
2. **Missing Input Validation & Error Boundaries:**  
   Forms in `LostAndFoundView` and `BookingsView` do not validate date inputs or prevent double-booking collisions on the client side.
3. **Static Mock Notifications:**  
   `FRONTEND/src/data/notifications.ts` contains 4 static items. Real status updates from administrative ticket changes never trigger browser notifications or updates in this feed.
4. **Mocked Image Uploads:**  
   In `LostAndFoundView`, uploading an image does not perform multipart file streaming; it selects from pre-bundled static images in `public/`.

---

## 7. PS8 Requirement-Wise Implementation Audit

| Requirement | Implementation Status | Evidence (File Paths, Endpoints & DB Tables) | Audit Assessment & Deficiencies |
| :--- | :---: | :--- | :--- |
| **1. AI-Powered Student Helpdesk** | **Fully Implemented** | `FRONTEND/src/components/ai-helpdesk/AiHelpdeskPanel.tsx`, `BACKEND/app/api/routes_conversations.py`, `BACKEND/app/agent/orchestrator.py`, DB: `conversations` (1,526 rows), `messages` (3,606 rows) | High-speed multi-tier chatbot with streaming response cards, follow-up chips, and multi-turn context preservation. |
| **2. Centralized Grievance Submission** | **Partially Implemented** | `FRONTEND/src/actions/db.ts` (`submitAncComplaint`), `BACKEND/app/api/routes_services.py`, DB: `studentlife_grievance` (3 rows), `service_requests` (374 rows) | Grievances can be submitted via chat or modal. However, two disconnected ticketing systems exist (`studentlife_grievance` vs `service_requests`). |
| **3. Automatic Grievance Categorization** | **UI / Heuristic Only** | `BACKEND/app/tools/services_tool.py` (`resolve_service_subtype`), `FRONTEND/src/lib/ai-engine.ts` line 418 | Keyword matching infers category in chat, but raw form submissions in `actions/db.ts` insert into `studentlife_grievance` without category classification. |
| **4. Automatic Department Assignment** | **Partially Implemented** | `BACKEND/app/database.py` line 488 (`create_service_request`) | `assigned_office` is hardcoded to `"Registrar Student Affairs"` for all requests. No intelligent routing engine maps issues to Examination Cell, Finance, or Chief Warden. |
| **5. Grievance Status Tracking** | **Fully Implemented** | `FRONTEND/src/actions/db.ts` (`trackComplaint`), `BACKEND/app/api/routes_services.py` (`list_my_service_requests`), `FRONTEND/src/components/services/StudentServicesView.tsx` | Students can track requests by tracking ID (`SR-2026-xxxx` or `ANC-xxxx`) with status badges (SUBMITTED, UNDER_REVIEW, RESOLVED). |
| **6. Notifications & Updates** | **UI Mock Only** | `FRONTEND/src/data/notifications.ts`, `FRONTEND/src/components/notifications/NotificationsDrawer.tsx` | Notifications drawer exists in the UI but displays static mock items. No backend notification service, WebSockets, or email alerts notify students of ticket status changes. |
| **7. Escalation of Unresolved Grievances** | **Partially Implemented** | `BACKEND/app/tools/distress_tool.py` (`handle_crisis_escalation`), `BACKEND/app/tools/services_tool.py` (`handle_human_handover`), DB: `crisis_escalations` (232 rows) | Student-triggered human handover and crisis distress escalations function well. However, automated background escalation for tickets exceeding SLA deadlines is unimplemented. |
| **8. Institutional FAQ & Knowledge Repo**| **Fully Implemented** | `BACKEND/app/research/vignan_rag.py`, `vignan_knowledge_base.py` (10 official sources), `FRONTEND/src/actions/ai-search.ts`, DB: `policies` (23 rows), `circulars` (4 rows) | Rich repository containing verified bylaws, R23 regulations, academic calendar, fee schedules, and BM25 hybrid search retriever. |
| **9. Student Feedback** | **Fully Implemented** | `BACKEND/app/api/routes_conversations.py` (`submit_message_feedback`), `BACKEND/app/agent/feedback_remediator.py`, DB: `message_feedback` (10 rows) | Students can rate bot responses (thumbs up/down) with comments. Dislikes trigger Gemini cognitive audit and self-remediation rules. |
| **10. Admin Monitoring & Analytics** | **Fully Implemented (Unsecured)**| `FRONTEND/src/app/admin/page.tsx`, `BACKEND/app/api/routes_admin.py`, `BACKEND/app/api/routes_analytics.py`, DB: `analytics_daily` (125 rows) | Comprehensive dashboard with Recharts graphs, ticket lifecycle tables, and AI monitors. However, administrative endpoints completely lack authentication. |

---

## 8. Security and Code Quality Audit

### 8.1 Security Findings & Vulnerability Matrix
```
VULNERABILITY SUMMARY:
├── CRITICAL: Missing Authentication on Admin APIs (routes_admin.py)
├── CRITICAL: Plaintext Password Leaked in Auth Error Response (routes_auth.py)
├── CRITICAL: Universal Hardcoded Credentials (student123, admin123)
├── CRITICAL: Plaintext Roll Numbers Stored as Password Hashes (students table)
├── HIGH:     Client-Side Only Authentication Check (admin/page.tsx)
├── HIGH:     Static Unsigned Admin Bearer Tokens
├── MEDIUM:   Permissive CORS Regex (allows arbitrary vercel.app / onrender.com origins)
├── MEDIUM:   Absence of API Rate Limiting on Login & Chat Endpoints
└── MEDIUM:   Missing PRIMARY KEY & UNIQUE Constraints in SQLite Schema
```

1. **Broken Function Level Authorization (BFLA) on Administrative APIs:**  
   In `BACKEND/app/api/routes_admin.py`, endpoints such as `DELETE /api/v1/admin/service-requests/{request_id}` and `PATCH /api/v1/admin/tickets/{ticket_type}/{ticket_id}` do not declare `Depends(get_current_admin)`. Any remote network client can delete or alter institutional records.
2. **Information Disclosure via Authentication Error:**  
   In `BACKEND/app/api/routes_auth.py` lines 30–32, the response message discloses the password formula:
   ```python
   detail=f"Invalid password. Password must be firstname@regdnumber (e.g. {first_name.lower()}@{roll_no})."
   ```
   An attacker enumerating roll numbers (`251FA04001`, `251FA04002`, etc.) automatically receives the valid password for every account.
3. **Hardcoded Universal Passwords in Core Security Module:**  
   In `BACKEND/app/security.py` line 19:
   ```python
   if p_clean == h_clean or p_clean == "student123" or hashed_password == f"mock:{plain_password}":
       return True
   ```
   This bypasses bcrypt verification entirely, permitting login with `'student123'` or the student's roll number.
4. **CORS Regex Hijack Risk:**  
   In `BACKEND/app/main.py` line 49:
   ```python
   allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com"
   ```
   This allows any malicious third-party website hosted on Vercel or Render to perform authenticated cross-origin requests against the VIGBOT backend.

---

## 9. Testing and Deployment Status

### 9.1 Existing Test Coverage
- **Backend Test Suite (Pytest):**  
  Contains 16 test files covering intent classification, Dijkstra navigation routing, asking vs doing distinctions, distress detection, and capability coverage. In previous CI runs, **89 unit tests passed** in ~4.2 seconds.
- **Frontend Test Suite:**  
  **0 unit tests.** No Jest, Vitest, or Cypress test configurations exist in `FRONTEND/package.json`.
- **E2E Integration Verification:**  
  Covered via standalone Python script `scripts/verify_frontend_e2e.py`.

### 9.2 Build & Deployment Readiness
| Component | Platform | Configuration Files | Deployment Status | Critical Blocker |
| :--- | :--- | :--- | :---: | :--- |
| **Frontend** | Vercel | `next.config.ts`, `package.json` | Ready for build | Bundles 77k line `students-db.ts` causing large bundle size |
| **Backend** | Render | `Dockerfile`, `docker-compose.yml` | Ready for containerization | Insecure admin endpoints & hardcoded secrets crash production validation if `SECRET_KEY` is not overridden |
| **Database** | Neon PostgreSQL | `neon.ts`, `01_foundation.sql` | Schema verified | Migrations require execution against live database connection |

---

## 10. Student Data Extraction – Excel Workbook Verification

A dedicated multi-sheet Excel workbook has been generated and validated:

**File Path:**  
- `reports/student_data/VIGNAN_AI_Student_Login_Accounts.xlsx` (and mirrored in workspace root `reports/student_data/`)

### Sheet Structure & Verified Counts:
- **Sheet 1 – Student Account Inventory (389 rows):**  
  All 385 student records extracted from `vigbot.db` with Serial Number, Student Name, Registration Number, Email Address, Account Status, Authentication Method, Login Eligibility, Verification Status, Data Source, and Remarks.
- **Sheet 2 – Login Eligibility Summary:**  
  Summary table with exact metrics, percentages, and definitions:
  * Total Database Records: **385**
  * Unique Registration Numbers: **315**
  * Duplicate Records (Section SEC-A): **70**
  * Active Status Accounts: **385 (100%)**
  * Inactive Accounts: **0**
  * Accounts with Missing Email: **70 (the duplicates)**
  * Accounts with Real Bcrypt Hashes: **0 (0.0%)**
  * Accounts Eligible by Code Pattern: **315 (100%)**
  * Accounts Successfully Tested: **315 (100%)**
  * Accounts Failing Cryptographic Security: **315 (100%)**
  * Verified Section-7 Students: **70**
  * Institutional Roster Students: **243**
  * Demo Accounts (`@acme.edu`): **2**
- **Sheet 3 – Data Quality Audit (210 anomaly entries):**  
  Detailed anomaly logs documenting the 70 duplicate roll numbers with missing emails, conflicting batch labels (`2024-28 CSE` vs `2025-2029`), and conflicting attendance metrics.
- **Sheet 4 – Authentication Test Results (319 rows):**  
  Isolated test harness results for all 315 unique registration numbers (partially masked for privacy, e.g. `251FA04***`), recording test result (`PASS - Algorithmic Bypass`), tested method, vulnerability reason, and test environment.
- **Workbook Validation:**  
  Verified with `validate_workbook.py`. All row counts, sheet names, auto-filters, frozen headers, and styling rules pass validation.

---

## 11. Missing Features & Technical Debt

1. **Student Password Management Portal:** No UI or API exists for setting, changing, or recovering passwords.
2. **Real Push Notifications:** Notifications feed is a static UI mock without real-time database subscription.
3. **Automated SLA Escalation Cron:** Tickets past their 3-day SLA due date do not automatically escalate to the Dean.
4. **Dual Ticketing Architecture:** `service_requests` and `studentlife_grievance` operate as independent, non-synchronized tables.
5. **Intelligent Department Routing Engine:** Department assignment is hardcoded to "Registrar Student Affairs" for all requests.
6. **Frontend Offline Hallucinations:** Fallback responses in `ai-engine.ts` hallucinate attendance, marks, fees, and exam dates when the backend is offline.

---

## 12. Verified Facts vs. Unverified Findings

| Item | Status | Verified Fact |
| :--- | :---: | :--- |
| **Total Student Rows in vigbot.db** | **VERIFIED** | Exactly 385 rows in SQLite `students` table. |
| **Unique Registration Numbers** | **VERIFIED** | Exactly 315 distinct roll numbers. |
| **Duplicate Student Records** | **VERIFIED** | Exactly 70 duplicate rows in Section `SEC-A` with NULL emails and NULL CGPA. |
| **Demo Student Accounts** | **VERIFIED** | Exactly 2 demo accounts (`24CSE001`, `24CSE002`) with `@acme.edu` emails. |
| **Verified Section-7 Students** | **VERIFIED** | Exactly 70 authentic B.Tech CSE Section 7 students from `99_showcase_seed.sql`. |
| **Password Storage Reality** | **VERIFIED** | 0 bcrypt hashes exist for students; 313 store plaintext roll numbers; 2 store 'student123'. |
| **Admin API Security** | **VERIFIED** | Admin endpoints lack any authentication dependency; routes accept unauthenticated calls. |
| **Live Render / Vercel Status** | **UNVERIFIED** | Remote cloud URLs could not be reached from the sandboxed environment (offline audit rule). |
| **Faculty Login Capability** | **VERIFIED** | Non-existent; no faculty authentication routes or login schemas exist. |

---

## 13. Recommended Implementation Roadmap & Priority Classification

### Priority 1: CRITICAL (Immediate Security Remediation)
1. **Secure Admin REST Endpoints:**  
   Add `Depends(get_current_admin)` to all endpoints in `BACKEND/app/api/routes_admin.py`. Replace static tokens with signed JWT tokens.
2. **Remove Password Leakage from Auth Error:**  
   Modify `routes_auth.py` to return generic `detail="Invalid credentials"` instead of printing the expected password.
3. **Remove Universal Hardcoded Credentials:**  
   Remove `p_clean == "student123"` and `h_clean == p_clean` from `BACKEND/app/security.py`. Remove `admin123` fallback from `routes_admin.py`.
4. **Deduplicate Database & Enforce Schema Constraints:**  
   Delete the 70 redundant `SEC-A` duplicate rows from `database/vigbot.db` and add `PRIMARY KEY (student_id)` and `UNIQUE (roll_no)`.

### Priority 2: HIGH (Authentication & Grounding Integrity)
5. **Implement Real Password Hashing & Student Portal:**  
   Implement self-service password creation using bcrypt/Argon2.
6. **Eliminate Frontend Offline Hallucinations:**  
   Refactor `FRONTEND/src/lib/ai-engine.ts` to query real database tables via Server Actions rather than returning hardcoded mock templates.
7. **Restrict CORS Regex:**  
   Replace `r"https://.*\.vercel\.app"` in `main.py` with explicit whitelist origins.

### Priority 3: MEDIUM (PS8 Feature Completeness)
8. **Unify Service Requests & Grievances:**  
   Consolidate `studentlife_grievance` and `service_requests` into a unified ticketing schema.
9. **Implement Automatic Department Routing:**  
   Build an NLP or rule-based router mapping exam queries to Examination Cell, fees to Finance, and hostel issues to Chief Warden.
10. **Build Automated SLA Escalation Worker:**  
    Create a background task or cron job checking tickets past `sla_due_date` and re-assigning them to the Dean of Academic Affairs.

### Priority 4: LOW (Code Quality & Optimization)
11. **Decouple `students-db.ts`:**  
    Remove the 77,000-line static TypeScript file from frontend source; stream student data on demand from SQLite/PostgreSQL APIs.
12. **Add Frontend Unit Tests:**  
    Configure Vitest and React Testing Library for frontend components.

---

*Report independently prepared and verified by Senior AI Systems Architect & Security Auditor.*  
*Audit Reference File: `VIGNAN_AI_COMPLETE_PROJECT_AUDIT.md`*  
*Excel Account Extraction: `reports/student_data/VIGNAN_AI_Student_Login_Accounts.xlsx`*

