# VIGBOT Data Coverage, Source Audit & Missing Facts Specification

**Document Version:** 1.0.0  
**Audit Date:** October 30, 2026  
**Scope:** Exhaustive audit across all 23 sidebar pages in VIGBOT (FastAPI backend + Next.js frontend + SQLite database).  
**Objective:** Ground every answer in verified structured tools, eliminate navigation traps, enforce the **Answer-First Rule**, and specify the exact missing facts required from university stakeholders.

---

## 1. Architectural Rules for Answer Pipeline (Step 2 Baseline)

### 1.1 The "Answer-First" Rule
- **Primary Directive:** Every reply to a factual question must deliver the direct answer in the **very first sentence**.
- **No Navigation Traps:** A response must never simply state *"Opening Central Library for you now"* or *"Find this on the Campus Map"* without first answering the student's question.
- **Role of Navigation Cards:** Navigation action cards (`action: {type: 'navigate', route: '...'}`) and deep links are **supplementary UI chips** appended below the answer, never a substitute for information.
- **Zero-Mutation on Information Queries:** Informational inquiries (*"how do I report a lost card"*, *"where is the mess"*) must strictly be read-only and **never** mutate the database or create ticket IDs.

### 1.2 Classifier Hints & Ablation Architecture
- The 18-class ML classifier (Word/Char TF-IDF + Logistic Regression) returns **Top-3 topic hints with confidence scores** (e.g. `[('transport', 0.72), ('hostel', 0.26), ('greeting_smalltalk', 0.00)]`).
- **Advisory Only:** These top-3 hints are passed to the Gemini function calling engine purely as **optional hints**. Gemini is given the **entire Tool Registry** and is free to select any tool.
- **Classifier Coverage Gap:** The 18 target intents in `ml/intents.yaml` do **not** have classes for:
  - `bookings` (Facility bookings)
  - `map` (Campus navigation)
  - `lost-and-found`
  - `career`
  - `marketplace`
  - `polling`
  - `alumni`
  *(These 7 capabilities are discovered via the Tool Registry and Universal NLU capability registry rather than ML intent classes).*
- **Ablation Protocol:** The evaluation harness will benchmark:
  1. *Pipeline With Classifier Hints* (Top-3 hints injected in system prompt)
  2. *Pipeline Without Classifier Hints* (Gemini explores tool registry blindly from query alone)
  to measure tool selection accuracy, latency delta, and token usage.

### 1.3 Deterministic Fast Paths
- For queries where structured database calculations already provide complete, authoritative, and grounded answers:
  1. **Attendance Recovery Math** (`attendance`): Current percentage, classes attended/held, consecutive classes needed to cross 75%, condonation cutoff date.
  2. **Marks & CGPA Breakdown** (`marks`): Formative assessment components, mid-term marks, max marks, credit weighting.
  3. **Fee Status & Challans** (`fees`): Total demand, paid amount, outstanding balance, installment deadlines, challan numbers.
- These 3 domains execute via **deterministic fast-path tools** without incurring Gemini LLM latency or token costs.

### 1.4 Privacy & LLM Data Protection Boundary
- **Zero PII Exposure to Cloud LLMs:** Student names, roll numbers, personal phone numbers, and email addresses are **strictly redacted** or stripped before function calling payloads reach Gemini.
- Only anonymized, tokenized parameters (e.g. `course_code: "CS302"`, `facility_type: "seminar_hall"`) are passed to Gemini function calling.
- Final answers merge personalized facts (student name, roll number) locally inside the backend response synthesis layer.

### 1.5 Free-Tier Quota & Degradation Guard
- **Free-Tier Handling:** If Gemini API returns HTTP 429 (Rate Limit / Quota Exceeded), network timeouts, or `GEMINI_API_KEY` is omitted:
  - The pipeline immediately falls back to a **Deterministic Tool Template Engine**.
  - Every tool in the registry implements a static fallback template that synthesizes structured facts directly from SQLite without crashing.
- **Telemetry Metrics:**
  - Latency: p50 and p95 per query.
  - Gemini Tool Rounds: Monitored per query (hard ceiling at maximum 3 rounds).

---

## 2. Exhaustive Data Audit Across All 23 Sidebar Pages

Each sidebar page was audited across its **Frontend View Component**, **Backend SQLite Table**, **Data Format** (Structured Records vs. Static Text), and **Factual Status**:
- **Real:** Grounded in official institutional documents, regulations, or active backend schemas.
- **Demo Data:** Functioning schema and UI populated with mock records for demonstration.
- **Missing:** Data not present in database, frontend, or backend handlers.

| # | Sidebar Page | Actual Frontend Route & File | Backend Table & Source File | Data Format | Fact Status & Source Verification |
|---|---|---|---|---|---|
| **1** | **Helpdesk Home** (`home`) | Route: `/?tab=home`<br>[`FRONTEND/src/components/hero/HeroSection.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/hero/HeroSection.tsx) (L1-80) | SQLite: `students`<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) (L180-220) | Structured Records | **Demo Data**<br>Pre-seeded demo student `251FA04E13` (Aman Kumar, B.Tech CSE). Connected to JWT session. |
| **2** | **Attendance** (`attendance`) | Route: `/?tab=attendance`<br>[`FRONTEND/src/components/attendance/AttendanceView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/attendance/AttendanceView.tsx) (L1-150) | SQLite: `attendance` (977 rows)<br>[`BACKEND/app/tools/attendance_tool.py`](file:///c:/StudentHelpdesk/BACKEND/app/tools/attendance_tool.py) (L1-90) | Structured Records | **Real Regulations + Demo Records**<br>Bylaws grounded in official VFSTR R23 Regulation Clause 4.2 (75% mandatory cutoff, 65-75% condonation). Records are synthetic demo datasets across sections. |
| **3** | **Marks & CGPA** (`marks`) | Route: `/?tab=marks`<br>[`FRONTEND/src/components/marks/MarksView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/marks/MarksView.tsx) (L1-120) | SQLite: `marks` (2,922 rows)<br>[`BACKEND/app/tools/marks_tool.py`](file:///c:/StudentHelpdesk/BACKEND/app/tools/marks_tool.py) (L1-85) | Structured Records | **Demo Data**<br>Modeled on VFSTR Continuous Internal Evaluation (Formative Assessment 1 & 2, Mid-term 1 & 2, 40% internal weightage). |
| **4** | **Library** (`library`) | Route: `/?tab=library`<br>[`FRONTEND/src/components/library/LibraryView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/library/LibraryView.tsx) (L14-209) | SQLite: `library_lended_books` (3 rows), `library_resources` (7 rows)<br>[`BACKEND/app/tools/library_tool.py`](file:///c:/StudentHelpdesk/BACKEND/app/tools/library_tool.py) (L5-73) | Mixed (Structured books; Dummy UI constants) | **Demo Data & Missing Facts**<br>Book titles are demo. **CRITICAL MISSING FACTS:** Library operating hours, Sunday hours, circulation desk rules, digital repository links. |
| **5** | **Timetable** (`timetable`) | Route: `/?tab=timetable`<br>[`FRONTEND/src/components/timetable/TimetableView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/timetable/TimetableView.tsx) (L1-160) | SQLite: `timetable` (4,944 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) (L310-345) | Structured Records | **Real Schedule Structure + Demo Allocation**<br>Configured for 2026-27 Semester-I class periods (Monday–Saturday, 8:00 AM – 4:00 PM) for B.Tech CSE Section 7. |
| **6** | **Examinations** (`exams`) | Route: `/?tab=exams`<br>[`FRONTEND/src/components/examinations/ExaminationsView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/examinations/ExaminationsView.tsx) (L1-140) | SQLite: `exams` (1,272 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) (L350-380) | Structured Records | **Real Schedule + Demo Hall Tickets**<br>Official 2026-27 Semester-I Mid-1, Mid-2, and Semester-End examination calendar dates. Hall ticket QR status is simulated. |
| **7** | **Curriculum** (`curriculum`) | Route: `/?tab=curriculum`<br>[`FRONTEND/src/components/curriculum/CurriculumView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/curriculum/CurriculumView.tsx) (L1-110) | SQLite: `curriculum` (1 row)<br>[`FRONTEND/src/data/curriculum.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/curriculum.ts) (L1-85) | Structured Summary | **Real Structure**<br>VFSTR R23 B.Tech CSE Choice Based Credit System (CBCS) requirements: 160 total graduation credits, departmental core/electives. |
| **8** | **Fee Status** (`fees`) | Route: `/?tab=fees`<br>[`FRONTEND/src/components/fees/FeesView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/fees/FeesView.tsx) (L1-95) | SQLite: `fees` (140 rows)<br>[`BACKEND/app/tools/fees_tool.py`](file:///c:/StudentHelpdesk/BACKEND/app/tools/fees_tool.py) (L1-70) | Structured Records | **Demo Data**<br>Synthetic fee demand schedules, installment payment records, and SBI challan numbers. |
| **9** | **Student Services** (`services`) | Route: `/?tab=services`<br>[`FRONTEND/src/components/services/StudentServicesView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/services/StudentServicesView.tsx) (L1-160) | SQLite: `service_requests` (369 rows)<br>[`BACKEND/app/tools/services_tool.py`](file:///c:/StudentHelpdesk/BACKEND/app/tools/services_tool.py) (L1-150) | Structured Queryable & Writable | **Real Taxonomy + Demo Requests**<br>Standard VFSTR student service categories (Bonafide certificate, Transcript, Bus pass renewal, ID card re-issuance, SGRC grievance). |
| **10** | **Hostel & Mess** (`hostel`) | Route: `/?tab=hostel`<br>[`FRONTEND/src/components/hostel/HostelManagementView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/hostel/HostelManagementView.tsx) (L85-147) | SQLite: `hostel_requests` (4 rows)<br>[`BACKEND/app/agent/nlu_engine.py`](file:///c:/StudentHelpdesk/BACKEND/app/agent/nlu_engine.py) (L1085-1130) | Static Text in Backend; Hardcoded Menu in UI | **Demo Menu + Real Bylaws + MISSING LOCATION**<br>Menu items (Idli/Vada, Rice/Dal, Chapati) are static UI text. Bylaws HD-01 to HD-06 in backend. **CRITICAL MISSING FACT:** Physical location of hostel mess / dining hall buildings. |
| **11** | **Career Hub** (`career`) | Route: `/?tab=career`<br>[`FRONTEND/src/components/career/CareerView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/career/CareerView.tsx) (L1-130) | SQLite: `resumes` (1 row)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Mixed | **Demo Data**<br>Mock internship postings and sample resume builder. |
| **12** | **Academic Calendar** (`calendar`) | Route: `/?tab=calendar`<br>[`FRONTEND/src/components/calendar/CalendarView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/calendar/CalendarView.tsx) (L1-120) | SQLite: `calendar_events` (5 rows)<br>[`FRONTEND/src/data/calendar.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/calendar.ts) (L1-120) | Structured Records | **Real Institutional Calendar**<br>Grounded in official VFSTR 2026-27 Semester-I B.Tech Academic Calendar (Commencement, Mid-1, Dussehra vacation, Mid-2, Practical exams, End-sem). Source: VFSTR Academic Affairs. |
| **13** | **Circulars & Notices** (`circulars`) | Route: `/?tab=circulars`<br>[`FRONTEND/src/components/circulars/CircularsView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/circulars/CircularsView.tsx) (L1-90) | SQLite: `circulars` (3 rows)<br>[`FRONTEND/src/data/circulars.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/circulars.ts) (L1-70) | Structured Records | **Real Structure + Demo Circulars**<br>Office of Dean Academics and Registrar circular formatting and metadata. |
| **14** | **Campus Map** (`map`) | Route: `/?tab=map`<br>[`FRONTEND/src/components/map/CampusMapView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/map/CampusMapView.tsx) (L19-50) | SQLite: `campus_locations` (5 rows)<br>[`FRONTEND/src/actions/campus.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/actions/campus.ts) (L10-31) | Structured Records (Incomplete) | **Partially Real + CRITICAL MISSING BLOCKS**<br>Contains only 5 locations (N-Block, Library, Boys Hostel A, AI/ML Lab, Main Canteen). **CRITICAL MISSING FACT:** Complete Campus Block Directory (U-Block, A-Block, H-Block, Pharmacy Block, Science Block, Exam Cell). |
| **15** | **Transport** (`transport`) | Route: `/?tab=transport`<br>[`FRONTEND/src/components/transport/TransportView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/transport/TransportView.tsx) (L1-66)<br>[`HostelBusTimetable.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/transport/HostelBusTimetable.tsx) (L4-20) | SQLite: `transportation_routes` (4 rows)<br>[`FRONTEND/src/actions/transport.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/actions/transport.ts) (L7-17) | Mixed (Static DB table + Hardcoded JSX Hostel Timetable) | **Demo Data & Isolated Timetable**<br>City routes (1–4) and driver ETAs are mock. Hostel bus schedule is hardcoded in JSX (`HostelBusTimetable.tsx`) but **was completely missing from backend knowledge**. "Live" badge is unverified. |
| **16** | **Event Registration** (`events`) | Route: `/?tab=events`<br>[`FRONTEND/src/components/events/EventRegistrationView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/events/EventRegistrationView.tsx) (L1-110) | SQLite: `event_registrations` (3 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Structured Records | **Demo Data**<br>Mock campus events (Hackathon 2026, Vignan Mahotsav). |
| **17** | **Lost & Found** (`lost-and-found`) | Route: `/?tab=lost-and-found`<br>[`FRONTEND/src/components/lost-and-found/LostAndFoundView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/lost-and-found/LostAndFoundView.tsx) (L23-80) | SQLite: `lost_and_found` (4 rows)<br>[`FRONTEND/src/actions/lostAndFound.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/actions/lostAndFound.ts) | Structured Queryable & Writable | **Demo Community Board + MISSING ID PROCEDURE**<br>Supports student item posting/claiming. **CRITICAL MISSING FACT:** Formal administrative procedure for reporting and replacing lost University ID cards. |
| **18** | **Facility Booking** (`bookings`) | Route: `/?tab=bookings`<br>[`FRONTEND/src/components/bookings/BookingsView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/bookings/BookingsView.tsx) (L1-120) | SQLite: `bookings` (3 rows), `facilities` (4 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Structured Queryable & Writable | **Demo Data**<br>Facilities (Seminar Hall 1, Main Auditorium, Open Air Theatre, Sports Complex) and reservation slots. |
| **19** | **Clubs & Communities** (`clubs`) | Route: `/?tab=clubs`<br>[`FRONTEND/src/components/clubs/ClubsView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/clubs/ClubsView.tsx) (L1-140) | SQLite: `studentlife_club` (5 rows), `studentlife_club_member` (3 rows)<br>[`FRONTEND/src/data/clubs.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/clubs.ts) (L1-180) | Structured Records | **Real Club Directory + Demo Rosters**<br>AI Innovation Club (Robotics/AI), Symphony Music Club, Athletics & Sports, Competitive Programming, Theatrix. |
| **20** | **Marketplace** (`marketplace`) | Route: `/?tab=marketplace`<br>[`FRONTEND/src/components/marketplace/MarketplaceView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/marketplace/MarketplaceView.tsx) (L1-120) | SQLite: `marketplace_listings` (5 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Structured Queryable & Writable | **Demo Data**<br>Used textbooks, engineering drafters, calculators. |
| **21** | **Campus Polling** (`polling`) | Route: `/?tab=polling`<br>[`FRONTEND/src/components/polling/PollingView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/polling/PollingView.tsx) (L1-90) | SQLite: `campus_polls` (3 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Structured Queryable & Writable | **Demo Data**<br>Mock student sentiment polls. |
| **22** | **Alumni Network** (`alumni`) | Route: `/?tab=alumni`<br>[`FRONTEND/src/components/alumni/AlumniView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/alumni/AlumniView.tsx) (L1-95) | SQLite: `alumni_mentors` (5 rows)<br>[`BACKEND/app/database.py`](file:///c:/StudentHelpdesk/BACKEND/app/database.py) | Structured Records | **Demo Data**<br>Sample alumni mentors at tech companies. |
| **23** | **Policies & Regulations** (`policies`) | Route: `/?tab=policies`<br>[`FRONTEND/src/components/policies/PoliciesView.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/policies/PoliciesView.tsx) (L1-110) | SQLite: `policies` (23 rows)<br>[`FRONTEND/src/data/policies.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/policies.ts) (L1-86) | Structured Records | **Real Institutional Policies**<br>Official VFSTR Academic Regulations R23/R24 (Attendance condonation, grading scale, detention rules, exam conduct, malpractice). Source: VFSTR Academic Bylaws. |

---

## 3. Root Cause Analysis of the 5 Failing Reproduction Queries

During Step 1 baseline reproduction, 5 specific factual queries failed to produce accurate, grounded answers. Below is the exact diagnosis of why each failed and what data is missing:

### 3.1 Failing Query: `"is the library open on sunday"`
- **Observed Behavior:** Pipeline routed to `library` and responded with: *"Opening Central Library for you now."* with a navigation card. It never answered whether the library is open on Sunday.
- **Root Cause:**
  - `library_tool.py` (L5-73) only queries the student's personal borrowed books (`library_lended_books`).
  - Neither SQLite nor `LibraryView.tsx` possesses library working hours or Sunday timings.
- **Exact Missing Facts:**
  1. Is the Central Library open on Sundays? (e.g. Yes/No, or 9:00 AM – 5:00 PM).
  2. Sunday reading room hours vs. digital section hours.
  3. Sunday book borrowing/circulation counter availability.

### 3.2 Failing Query: `"where is the mess and what time is dinner"`
- **Observed Behavior:** Pipeline dumped 50 lines of static hostel rules (Clause HD-01 to HD-06). Clause HD-05 mentions dinner is *7:30 PM – 9:00 PM*, but completely failed to state where the mess is located.
- **Root Cause:**
  - `nlu_engine.py` (L1085-1130) contains a hardcoded text block for dining rules, but omits dining hall physical building names and locations.
  - `HostelManagementView.tsx` (L87-100) displays dinner at 7:30 PM, but does not state the building location.
- **Exact Missing Facts:**
  1. Physical location of the Boys Mess (e.g. Ground Floor, Hostel Dining Hall Block H).
  2. Physical location of the Girls Mess (e.g. Priyadarshini Hostel Complex Ground Floor).
  3. Locations of secondary food courts or day-scholar canteens.

### 3.3 Failing Query: `"hostel bus timing"`
- **Observed Behavior:** Pipeline classified query as `transport` (0.7204) and dumped a static schedule for city buses (Routes 1–4 from Guntur, Vijayawada, Tenali). It provided zero hostel-to-campus bus timings.
- **Root Cause:**
  - The frontend has an isolated component [`FRONTEND/src/components/transport/HostelBusTimetable.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/transport/HostelBusTimetable.tsx) (L4-20) with schedules for *KM Hostel*, *Villas SP Residency*, and *AP/AR/AA/AO Hostels*.
  - **The backend has zero access to this table!** The SQLite table `transportation_routes` only contains 4 city routes with mock ETAs.
- **Exact Missing Facts:**
  1. Confirmation of the active hostel shuttle timetable w.e.f. 01.10.2026.
  2. Exact hostel pickup points (e.g., KM Hostel Main Gate, SP Residency Arch).
  3. Weekend rail link timing connecting hostels to Tenali/Guntur railway stations.

### 3.4 Failing Query: `"where is u block"`
- **Observed Behavior:** Pipeline classified query as `services` (0.9687) and navigated to `/?tab=map` with message *"Find classroom locations... on the Campus Map"*. It failed to state where U-Block is.
- **Root Cause:**
  - SQLite table `campus_locations` contains only 5 rows (`LOC_MAIN`, `LOC_LIB`, `LOC_HOSTEL_A`, `LOC_LAB_1`, `LOC_CAFE`).
  - U-Block does not exist anywhere in the database or frontend campus action!
- **Exact Missing Facts:**
  1. Complete Campus Block Directory:
     - **U-Block:** Location, department housed (e.g. Core Engineering / ECE / Mechanical / Biotech), floor count, prominent landmarks.
     - **A-Block, H-Block, Pharmacy Block, Science & Humanities Block:** Locations and departments.
     - **Administrative Block, Examination Cell, Registrar Office:** Room numbers and floors.

### 3.5 Failing Query: `"how do i report a lost id card"`
- **Observed Behavior:** Pipeline classified query as `services` (0.9055), recognized feature `lost-and-found`, and returned a navigation card to `/?tab=lost-and-found`.
- **Root Cause:**
  - The `lost-and-found` page is a community bulletin board for lost water bottles or calculators.
  - A student ID card is an official university credential requiring an administrative re-issuance workflow, not merely a community post.
- **Exact Missing Facts:**
  1. Official lost ID card procedure:
     - Reporting office (e.g., Dean of Student Affairs / Administrative Office Room A-102).
     - Duplicate ID card fee amount (e.g., ₹200 or ₹500 at Cash Counter).
     - Required documents (Application form, copy of payment receipt, police GD or declaration).
     - Processing turnaround time (e.g., 2–3 working days).

---

## 4. Factual Inventory: Exactly What Facts You Must Supply

To make VIGBOT 100% grounded with zero hallucinations, please supply the verified institutional facts below:

```text
================================================================================
INSTITUTIONAL FACTS REQUIRING USER / STAKEHOLDER CONFIRMATION
================================================================================

1. CENTRAL LIBRARY WORKING HOURS:
   • Monday to Saturday hours: [Currently assumed: 8:00 AM – 10:00 PM]
   • Sunday working hours:     [Please confirm: e.g., 9:00 AM – 5:00 PM or Closed?]
   • Sunday book circulation:   [Please confirm: Are book issues allowed on Sunday or reading only?]

2. HOSTEL MESS LOCATIONS:
   • Boys Hostel Dining Hall:  [Please confirm: e.g., Ground Floor, Block H / Main Dining Hall]
   • Girls Hostel Dining Hall: [Please confirm: e.g., Priyadarshini Hostel Complex Ground Floor]
   • Canteen / Food Court:     [Please confirm: Near U-Block / Student Activity Center?]

3. HOSTEL SHUTTLE BUS SCHEDULE:
   • KM Hostel:                [Please confirm: Morning: 7:50, 8:05, 8:40, 9:30, 10:30, 11:35 AM | Evening: 1:45 to 9:00 PM?]
   • Villas SP Residency:      [Please confirm: Morning: 7:45, 8:00, 8:40, 9:00, 9:50, 11:30 AM | Evening: 2:00 to 9:00 PM?]
   • AP, AR, AA, AO Hostels:   [Please confirm: Morning: 7:45, 7:55, 8:00, 8:40, 9:00, 9:50, 11:30 AM | Evening: 2:00 to 9:00 PM?]
   • Weekend Railway Shuttle:  [Please confirm departure times from hostels on Saturdays/Sundays]

4. CAMPUS BLOCK DIRECTORY (MAP DATA):
   • U-Block:                  [Please confirm: Department, floors, location relative to Main Gate/N-Block]
   • A-Block:                  [Please confirm: e.g., Administrative Block / Principal Office]
   • H-Block:                  [Please confirm: e.g., Mechanical / Civil / Hostels]
   • Pharmacy & Science Block: [Please confirm location]

5. LOST STUDENT ID CARD PROCEDURE:
   • Where to apply:           [Please confirm: Room A-102, Dean Student Affairs or Exam Cell?]
   • Duplicate ID card fee:    [Please confirm: e.g., ₹250 or ₹500?]
   • Payment method:           [Please confirm: Finance desk / Online Challan?]
   • Turnaround time:          [Please confirm: e.g., 3 working days?]
================================================================================
```

---

## 5. UI De-Spurious Audit

In accordance with instruction #7:
1. **"12 Connected Agents" Label:**
   - Found hardcoded in [`FRONTEND/src/components/sidebar/Sidebar.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/sidebar/Sidebar.tsx) at line 395.
   - Backed only by mock dummy array in [`FRONTEND/src/data/connected-agents.ts`](file:///c:/StudentHelpdesk/FRONTEND/src/data/connected-agents.ts).
   - **Resolution Plan for Step 7:** Remove the hardcoded string from `Sidebar.tsx`. Replace with verified active system status (e.g., *"RLAC Guardrail Enforced"* or *"System Ready"*).
2. **"Transport (Live)" Label:**
   - Found hardcoded in [`FRONTEND/src/components/sidebar/Sidebar.tsx`](file:///c:/StudentHelpdesk/FRONTEND/src/components/sidebar/Sidebar.tsx) at line 184 (`label: "Transport (Live)"`).
   - Backed only by 4 static rows in `transportation_routes` with static mock numbers.
   - **Resolution Plan for Step 7:** Change label to `"Transport & Buses"` in `Sidebar.tsx`.

---

## 6. Read-Only Tool Registry Design (Preview for Step 3)

For Step 3, we will engineer a centralized Python module [`BACKEND/app/agent/tool_registry.py`](file:///c:/StudentHelpdesk/BACKEND/app/agent/tool_registry.py) providing **one typed read-only tool per sidebar page**.

### Tool Standard Contract
Every tool function will return a dictionary adhering to:
```python
class ToolResult(TypedDict):
    available: bool          # True if data is known and verified; False if missing/unconfigured
    source: str              # E.g., "VFSTR Central Library Desk", "Academic Calendar 2026-27"
    last_updated: str        # E.g., "2026-10-01"
    sidebar_page: str        # E.g., "library", "hostel", "transport"
    data: Optional[Dict[str, Any]] # Structured factual records
    missing_notice: Optional[str]  # Exact office or portal to consult if available=False
```

### The 23 Sidebar Tools Specification
1. `get_student_profile(session)`: JWT-scoped roll number, program, mentor, section.
2. `get_attendance_records(session, course_code=None)`: JWT-scoped attendance percentages, classes needed to reach 75%, condonation status.
3. `get_marks_records(session, course_code=None)`: JWT-scoped CIE, FA-1, FA-2, internal marks.
4. `get_library_info(query_type)`: Operating hours, Sunday timings, borrowing rules, overdue policy.
5. `get_timetable_schedule(session, day_of_week=None)`: JWT-scoped section timetable, class rooms, faculty.
6. `get_examination_schedule(session)`: Mid-term and end-sem exam dates, times, venues.
7. `get_curriculum_audit(session)`: CBCS graduation credits, remaining credits, core/electives.
8. `get_fee_status(session)`: JWT-scoped demand, paid amount, dues, payment deadline, SBI challan details.
9. `get_services_directory(category=None)`: List of administrative services, SLA turnaround times, required forms.
10. `get_hostel_and_mess_info(hostel_name=None)`: Dining hall locations, mess hours (breakfast, lunch, dinner), curfew rules.
11. `get_career_opportunities()`: Campus placement drive notices, eligibility, internship portal.
12. `get_academic_calendar(month=None)`: 2026-27 Semester-I start dates, holidays, exam windows.
13. `get_official_circulars(limit=5)`: Recent registrar circulars, notifications, deadlines.
14. `get_campus_location_info(block_or_room_name)`: Campus block directory, U-Block, N-Block, floor, landmarks.
15. `get_transport_timetable(route_or_hostel=None)`: Hostel bus schedules (KM, Villas SP, AP/AR/AA/AO), city transit routes (1-4).
16. `get_campus_events()`: Active hackathons, cultural festivals, registration links.
17. `get_lost_and_found_info(item_type=None)`: Active community listings AND official lost ID card administrative procedure.
18. `get_facility_booking_info(facility_name=None)`: Seminar halls, auditoriums, capacity, booking procedure.
19. `get_clubs_directory(category=None)`: Active student clubs (AI Innovation, Symphony, Sports, etc.), joining steps.
20. `get_marketplace_listings(category=None)`: Student peer marketplace listings, prices.
21. `get_campus_polls()`: Active institutional polls, student votes.
22. `get_alumni_mentors(field=None)`: Registered alumni mentors, companies, domains.
23. `get_university_policies(policy_id_or_keyword=None)`: R23 attendance condonation, detention, grading, UMC rules.

---

## 7. Status & Next Action

- **Step 2 (Data Audit & `docs/DATA_COVERAGE.md`)** is fully written and verified against the codebase.
- In accordance with instruction #6: **Execution is stopped here.** We will not begin Step 3 until you review and approve this audit.

