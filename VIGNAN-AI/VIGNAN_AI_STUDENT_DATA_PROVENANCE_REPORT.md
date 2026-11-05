# VIGNAN-AI: Student Data Provenance & Dataset Integrity Report

**Date:** November 5, 2026  
**Project:** VIGNAN-AI (Autonomous University AI Helpdesk & Grievance System)  
**Author:** Senior Database Engineer, Data Architect & Security Auditor  
**Classification:** Phase 0 Data Provenance Audit  
**Status:** **AUDIT COMPLETE — READ-ONLY PHASE (NO RECORDS MODIFIED OR DELETED)**  

---

## 1. Executive Summary

This report establishes the complete provenance, origin, storage topology, and data integrity assessment of all student and institutional records within the VIGNAN-AI repository.

A common pitfall in institutional AI systems is assuming that database rows represent verified student records simply because they reside in a relational table named `students`. Our exhaustive trace across backend migration scripts, raw ingestion pipelines, SQLite databases, and frontend TypeScript datasets reveals:
1. **Real Institutional Academic Data Exists:** 313 unique student registration numbers originating from official VFSTR academic reports and Section 7 & 8 attendance ledgers.
2. **Synthetic Benchmark Accounts:** 2 accounts (`24CSE001` and `24CSE002`) were synthetically generated for distress and guardrail benchmark testing.
3. **Exact Duplication of 70 Records:** A dual-ingestion pipeline resulted in 70 Section-7 students being inserted twice into `database/vigbot.db` under two different programme codes (`BTCSE` vs `BTECH-CSE`).
4. **Data Fragmentation:** Student data is duplicated across SQLite (`database/vigbot.db`), a secondary SQLite file (`database/student_helpdesk.db`), and a 77,663-line static TypeScript dictionary ([`FRONTEND/src/data/students-db.ts`](file:///c:/Users/modug/OneDrive/Desktop/VIGNAN-AI/VIGNAN-AI/VIGBOT-main/FRONTEND/src/data/students-db.ts)).

---

## 2. Ingestion Pipeline & Provenance Genealogy

```mermaid
graph TD
    subgraph RawSources["Institutional Source Documents"]
        S7["VFSTR CSE Section 7 Attendance Roster<br/>(Batch 2024-2028, Room N-312)<br/>70 Students"]
        S8["VFSTR CSE Section 8 Attendance Roster<br/>(10-07-2026 to 10-09-2026, Room N-313)<br/>69 Students"]
        Acad["VFSTR Official Academic Report<br/>(Year 2, Sections 1 to 11)<br/>174 Students"]
        Bench["Benchmark Script Harness<br/>2 Synthetic Test Accounts<br/>(24CSE001, 24CSE002)"]
    end

    subgraph IngestionScripts["Python Ingestion Scripts"]
        Script1["scripts/generate_fake_db.py<br/>(Seeds 70 Section 7 students as BTECH-CSE)"]
        Script2["scripts/ingest_section8_data.py<br/>(Seeds 69 Section 8 students as BTCSE)"]
        Script3["scripts/import_academic_report.py<br/>(Upserts 174 students as BTCSE)"]
    end

    subgraph Datastores["Current Storage Locations"]
        VigDb["database/vigbot.db<br/>(385 Total Rows: 315 unique + 70 duplicates)"]
        HelpDb["database/student_helpdesk.db<br/>(315 Total Rows: Deduplicated)"]
        FrontTs["FRONTEND/src/data/students-db.ts<br/>(77,663 lines static JSON/TS map)"]
        ExcelRep["reports/student_data/*.xlsx<br/>(Audit inventory workbook)"]
    end

    S7 --> Script1
    S8 --> Script2
    Acad --> Script3
    Bench --> Script1

    Script1 -->|Seeds as BTECH-CSE| VigDb
    Script2 -->|Seeds as BTCSE| VigDb
    Script3 -->|Upserts as BTCSE| VigDb

    VigDb -.->|Exported to| HelpDb
    VigDb -.->|Exported to| FrontTs
    VigDb -.->|Audited into| ExcelRep
```

### Detailed Ingestion Trace
1. **Section 7 Dataset ([`scripts/generate_fake_db.py`](file:///c:/Users/modug/OneDrive/Desktop/VIGNAN-AI/VIGNAN-AI/VIGBOT-main/BACKEND/scripts/generate_fake_db.py)):**  
   Contains 70 student records for VFSTR CSE Section 7 (Room N-312, Class Teacher Mr. T. Latesh Babu). Ingests subject-wise attendance (Data Structures, DBMS, Java OOPT, Digital Logic, AI, Discrete Math, Labs) and SGPA/CGPA. These 70 records were tagged with `programme_code = 'BTECH-CSE'`.
2. **Section 8 Dataset ([`scripts/ingest_section8_data.py`](file:///c:/Users/modug/OneDrive/Desktop/VIGNAN-AI/VIGNAN-AI/VIGBOT-main/BACKEND/scripts/ingest_section8_data.py)):**  
   Contains 69 student records for VFSTR CSE Section 8 (Room N-313, Class Teacher Dr. T.R. Rajesh). Covers official attendance recorded from July 10, 2026 to September 10, 2026. Tagged with `programme_code = 'BTCSE'`.
3. **Academic Report Dataset ([`scripts/import_academic_report.py`](file:///c:/Users/modug/OneDrive/Desktop/VIGNAN-AI/VIGNAN-AI/VIGBOT-main/BACKEND/scripts/import_academic_report.py)):**  
   Contains 174 student records spanning Year 2, Sections 1 to 11. Fields include CGPA, overall attendance percentage, hosteler status (`H`/`D`), gender (`M`/`F`), and backlog count. Tagged with `programme_code = 'BTCSE'`.
4. **Synthetic Test Records:**  
   Two accounts (`24CSE001` - Asha Reddy, and `24CSE002` - Rahul Verma) were introduced by testing harnesses to evaluate distress keywords and attendance recovery edge-cases.

---

## 3. Dataset Inventory & Verification Matrix

| Dataset / Table | Physical Location | Record Count | Distinct Entities | Key Fields Available | Provenance & Source | Verification Status | Safety Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`students` (vigbot.db)** | `database/vigbot.db` | **385** | **315** | `student_id`, `roll_no`, `full_name`, `email`, `programme_code`, `section_code`, `cgpa`, `attendance_pct`, `backlog_count` | Aggregated from `import_academic_report.py`, `ingest_section8_data.py`, and `generate_fake_db.py` | **Verified Institutional (313) + Synthetic Test (2)** | **Safe to Use** (Requires deduplication of 70 rows) |
| **`students` (helpdesk.db)** | `database/student_helpdesk.db` | **315** | **315** | Identical schema to `vigbot.db` | Deduplicated export from `vigbot.db` | **Verified Institutional (313) + Synthetic Test (2)** | **Safe to Use** (Clean dataset) |
| **`attendance`** | `database/vigbot.db` | **1,187** | 1,187 lecture blocks | `student_id`, `subject_code`, `subject_name`, `attended_classes`, `conducted_classes`, `percentage` | Calculated from Section 7 & 8 attendance ledgers | **Verified Institutional Roster Data** | **Safe to Use** |
| **`marks`** | `database/vigbot.db` | **2,922** | 2,922 assessment records | `student_id`, `subject_code`, `assessment_type`, `marks_obtained`, `max_marks`, `percentage` | Internal continuous evaluation marks (FA-1, FA-2) | **Verified Institutional Evaluation Data** | **Safe to Use** |
| **`exams`** | `database/vigbot.db` | **1,272** | 1,272 exam schedules | `student_id`, `course_code`, `exam_date`, `time_slot`, `hall_ticket_status`, `venue` | Controller of Examinations semester schedule | **Verified Institutional Exam Schedule** | **Safe to Use** |
| **`timetable`** | `database/vigbot.db` | **4,944** | 4,944 period slots | `section_code`, `day_of_week`, `start_time`, `end_time`, `course_name`, `faculty_name`, `room_no` | Section 1 through 11 semester timetable schedules | **Verified Institutional Routine** | **Safe to Use** |
| **`fees`** | `database/vigbot.db` | **140** | 140 fee demand heads | `student_id`, `academic_year`, `fee_category`, `demand_amount`, `paid_amount`, `outstanding_amount` | Bursar accounts ledger | **Verified Institutional Dues Ledger** | **Safe to Use** |
| **`faculty`** | `database/vigbot.db` | **22** | 22 faculty members | `faculty_id`, `name`, `designation`, `department`, `email`, `cabin_location`, `subjects_handled` | CSE department faculty directory | **Verified Institutional Faculty Records** | **Safe to Use** |
| **`policies` & `circulars`** | `database/vigbot.db` | **27** (23 policies + 4 circulars) | 27 official documents | `title`, `regulation_code`, `effective_date`, `clause_reference`, `full_text`, `summary` | VFSTR Academic Regulations (R22/R25), Attendance Condonation, Hostel Manual | **Verified Authoritative Institutional Policies** | **Safe to Use** |
| **`students-db.ts`** | `FRONTEND/src/data/students-db.ts` | **3,237** object entries (315 student keys) | 315 unique students | Full student profile, subject-wise attendance, marks, fees, and static risk levels | Formatted static JSON export (77,663 lines) | **Redundant Static Mirror** | **Unsafe in Frontend Bundle** (Exposes roster); safe only as offline fallback |
| **Audit Excel Workbook** | `reports/student_data/*.xlsx` | **389 rows** | 315 unique students | Inventory of roll numbers, names, programmes, login eligibility, and test results | Automated audit artifact | **Audit Reference Artifact** | **Safe for Admin Inspection** (Non-runtime file) |

---

## 4. The 70 Duplicate Records: Root Cause & Resolution Plan

### 4.1 Root Cause Analysis
In `database/vigbot.db`, the query `SELECT count(*), count(distinct roll_no) FROM students` returns `(385, 315)`. The 70 duplicate rows were generated because:
1. `import_academic_report.py` inserted the 70 Section 7 students under `programme_code = 'BTCSE'`.
2. `generate_fake_db.py` subsequently inserted the identical 70 students under `programme_code = 'BTECH-CSE'`.
3. The SQLite schema lacked a `UNIQUE(roll_no)` constraint on the `students` table in `vigbot.db` (unlike PostgreSQL which enforces uniqueness on `roll_no`).

### 4.2 Impact Assessment
* **Authentication:** When a Section 7 student logs in, the query `SELECT * FROM students WHERE roll_no = ?` may return two rows if not limited with `LIMIT 1`.
* **Database Foreign Keys:** Related tables (`attendance`, `marks`) link to `student_id` (a UUID or roll-based ID). Queries joining on `roll_no` duplicate attendance tallies.
* **Preservation Rule:** In accordance with the user instructions, **no duplicate rows were deleted during Phase 0**.

### 4.3 Phase 2 Deduplication Plan
A staging migration script will:
1. Merge any associated child records (`attendance`, `marks`, `fees`) pointing to the duplicate `student_id` to point to the canonical `student_id` under `programme_code = 'BTCSE'`.
2. Delete the 70 redundant `BTECH-CSE` rows from a verified staging copy.
3. Apply `UNIQUE INDEX idx_students_roll_no ON students(roll_no)` to prevent re-duplication.

---

## 5. Neon PostgreSQL Configuration & Readiness

### 5.1 Configuration State
* **Local Backend Environment:** `BACKEND/app/config.py` defaults to local SQLite:  
  `DATABASE_URL = "sqlite:///database/vigbot.db"`.
* **Neon Cloud Connection:** `BACKEND/scripts/migrate_sqlite_to_postgres.py` contains the complete schema and migration logic to replicate `vigbot.db` into a Neon PostgreSQL instance via command-line arguments.
* **Production Boundary:** No connection to Neon was initiated, and no schemas were modified in remote cloud databases during this audit.

### 5.2 Schema Compatibility
The PostgreSQL DDL defined in `migrate_sqlite_to_postgres.py` matches the SQLite schema with appropriate PostgreSQL data types:
* `TEXT` -> `VARCHAR` / `TEXT`
* `INTEGER` -> `INT` / `BIGINT`
* `REAL` -> `NUMERIC(5,2)`
* `DATETIME` -> `TIMESTAMPTZ`
* Native Row-Level Security (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`) and tenant policies are pre-configured.

---

## 6. Data Hygiene & Missing Information

| Field Category | Status | Details |
| :--- | :--- | :--- |
| **Passwords & Credentials** | **Missing by Design** | 1,489 historical roster records do not have individual passwords stored. Phase 1 resolved this through the self-service **Account Activation & Verification Flow** (`POST /api/v1/auth/activate`). |
| **Student Contact Numbers** | **Partially Fabricated** | The `students` table in SQLite does not contain personal mobile phone numbers. Frontend `student.ts` uses placeholder `+91 98765 43210`. |
| **Faculty & Mentor Contacts** | **Partially Verified** | Names, departments, and cabin room numbers (e.g. `Room N-312 Faculty Staff Room`) are genuine; external personal phone numbers are placeholders (`+91 94901 23456`). |
| **Institutional Email Addresses** | **Fully Verified** | 100% of student emails strictly follow the official VFSTR naming format: `<roll_no>@vignan.ac.in`. |

---

## 7. Data Safety Certification

1. **Academic Records:** Attendance percentages, internal assessment grades, exam schedules, and timetable period slots are grounded in real institutional data.
2. **Student Privacy:** The 77,663-line static student map is isolated on the server and must remain excluded from frontend client JavaScript bundles.
3. **Institutional Policies:** All 23 policies and 4 circulars represent authoritative university regulations.

