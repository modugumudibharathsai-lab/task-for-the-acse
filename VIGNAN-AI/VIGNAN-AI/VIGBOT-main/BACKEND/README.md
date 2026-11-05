# VIGBOT Backend & AI Service

This backend service powers **VIGBOT** (Group 13 Student Support Agents). It provides authenticated students with a single, secure conversational interface to query their academic records, attendance, timetable, continuous internal marks, examination schedules, fee demands, and approved institutional policies.

---

## Key Features & Problem Statement Compliance

- **Strict Data-Layer Row-Level Security (RLS):** Student session context (`SET LOCAL app.student_id = '<uuid>'`) is enforced at the database layer. A student is technically incapable of viewing another student's records under any prompt phrasing or injection.
- **Hybrid 3-Tier Execution:** Tier 1: Deterministic security guardrails & fast database rules; Tier 2: Sub-millisecond CPU TF-IDF + Logistic Regression Intent Classifier; Tier 3: Cloud LLM fallback (Google Gemini gemini-3.5-flash / Groq) with automatic student PII redaction. Local mock mode (`LLM_PROVIDER=mock`) is fully supported for offline development and CI testing without external API keys.
- **Mandatory Step 9 Distress Guardrail (Crisis Intervention):** Every message is evaluated for distress, self-harm, or safety concerns before any routine processing. Any detected crisis immediately halts academic queries, writes an urgent alert to `confidential.crisis_escalation` (feeding **Agent 66**), and provides 24/7 counseling contacts.
- **Actionable Attendance Guidance:** Answers report the exact attendance percentage, classes attended/held, classes needed to reach 75%, condonation cut-off deadlines, and recovery feasibility.
- **Official Policy Citations:** Answers on academic rules cite the exact Regulation title, Clause number, and Effective Date (Agents 53 & 55).
- **Service Request Ticketing :** Generates formal service requests for Bonafide Certificates, Transcripts, Transit Bus Passes, Mentor Meetings, and Student Grievances with tracking IDs (e.g. `SR-2026-0001`).
- **Privacy-Safe Daily Analytics (Step 10):** Daily query analytics aggregate query counts, topics, and escalation rates **without storing student identities or raw chat text**.

---

## Quick Start (Running Locally)

### 1. Run Automated Acceptance Tests
All 12 acceptance tests validate the entire Problem Statement without needing any external database or API key:

```powershell
cd BACKEND
.\.venv\Scripts\python -m pytest -v
```

### 2. Start the Backend API Server
```powershell
cd BACKEND
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

Once running:
- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Schema:** [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Pre-Configured Test Student Accounts

| Student Name | Roll Number | Username | Password | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Asha Reddy** | `24CSE001` | `24cse001` | `student123` | B.Tech CSE, 2nd Year, Digital Electronics Attendance: 68.0% (At Risk, 14 classes needed) |
| **Rahul Verma** | `24CSE002` | `24cse002` | `student123` | B.Tech CSE, 2nd Year, Data Structures Attendance: 70.0%, 2 Backlogs |

---

## Database Architecture

The backend utilizes the platform schema files from `database/source/`:
- `01_foundation.sql` (Institutions, academic year, calendar)
- `02_people_identity.sql` (Student profile, users, roles)
- `03_curriculum.sql` (Programmes, regulations, course versions)
- `04_academics_attendance.sql` (Timetable, class sessions, attendance)
- `05_assessment_exams_outcomes.sql` (CIE marks, exam schedules, backlogs)
- `07_admissions_finance.sql` (Fee demand, installments, payments)
- `08_studentlife_placement_hr.sql` (Mentorship, grievances, crisis escalation)
- `09_governance_quality_knowledge.sql` (Policies, circulars, knowledge docs)
- `10_agentops.sql` (Agent catalogue, tools, run logs, alerts)
- `11_security_rls.sql` (PostgreSQL Row-Level Security policies)
- `12_views.sql` (Read-layer views)
- `13_helpdesk_extension.sql` (Conversations, messages, service requests, handovers, daily analytics)

*(Note: `06_research_engagement.sql` is strictly excluded as it is out of scope).*

---

## Docker Deployment (Optional)

To start PostgreSQL and the backend with Docker Compose:
```bash
docker compose up -d
```
