# VIGBOT Dataset Guide: Intent Dataset Collection (18 Topics)

## 1. Overview
This dataset powers the **VIGBOT Intent Classifier**, a lightweight, CPU-optimized TF-IDF and Logistic Regression model designed to identify student query intentions and route queries directly to the correct domain handler before calling external APIs.

---

## 2. Directory Structure & Files

To avoid git merge conflicts among teammates, each contributor works in their own dedicated CSV file under `data/authors/`:

```
data/
├── README.md               # This guide
├── intents.csv             # Starter rows only (author=agent)
├── crisis_test.csv         # Optional crisis test suite (text,lang) for crisis recall benchmarking
└── authors/
    ├── aman.csv            # Aman's question contributions (Training Author)
    ├── pragna.csv          # Pragna's question contributions (Training Author)
    ├── sirisha.csv         # Sirisha's question contributions (Training Author)
    └── sridhar.csv         # Sridhar's question contributions (Test Author)
```

All data processing, validation, and training scripts automatically merge `data/intents.csv` with all files in `data/authors/*.csv`.

> [!IMPORTANT]
> **Strict Author Roles & Sequestration**:
> - `author=agent` in `data/intents.csv`: Synthetic seed starter rows. Never counted toward human member quotas and never used as test data.
> - `author=sridhar` in `data/authors/sridhar.csv`: Designated **test author**. These rows are strictly sequestered as unseen test data. They are **never** used during model training, tuning, or cross-validation.
> - `author=aman`, `author=pragna`, `author=sirisha`: Training authors. Counted toward training quotas and evaluated in Leave-One-Author-Out cross-validation.

---

## 3. Schema and Columns

Every CSV file must be read/saved with **UTF-8 encoding** (with BOM or plain UTF-8) and strictly follow this exact header:

```csv
text,intent,lang,author
```

| Column | Description | Allowed Values | Examples |
|---|---|---|---|
| `text` | The student's question or message | Raw text (wrap in quotes if it contains commas) | `"How many classes can I bunk?"` |
| `intent` | The exact intent key | One of the 18 valid keys in [ml/intents.yaml](../ml/intents.yaml) | `attendance`, `fees`, `exams`, `hostel`, `transport` |
| `lang` | The language or code-mixed style | `en`, `hinglish`, `te_roman`, `te`, `hi` | `en` for English, `hinglish` for Hindi-English |
| `author` | Normalized author name (trimmed, lowercase) | `agent`, `aman`, `pragna`, `sirisha`, `sridhar` | `aman`, `pragna`, `sirisha`, `sridhar` |

> [!CAUTION]
> **Strict Encoding & Header Rules**:
> - Files are read with `utf-8-sig` and spaces are trimmed from header names.
> - Non-UTF-8 bytes cause `python ml/validate_data.py` to fail immediately and report the first offending line.
> - Any header column other than `text,intent,lang,author` is strictly rejected.

---

## 4. Team Quotas and Targets

Quotas count **only human authors** (`aman`, `pragna`, `sirisha` for training; `sridhar` for testing):

1. **Human Training Authors (`aman`, `pragna`, `sirisha`)**:
   - **20 rows per topic each** (combined target: **60 rows**) for the 14 standard topics.
   - **14 rows each** (combined target: **42 rows**) for the 4 special topics: `policy_bylaws`, `distress_support`, `greeting_smalltalk`, and `out_of_scope`.
   - Seed starter data (`author=agent`) is excluded from human quota counts.

2. **Test Author Requirements (`sridhar`)**:
   - At least **20 rows per topic** (minimum **15 rows** for `policy_bylaws`, `distress_support`, `greeting_smalltalk`, and `out_of_scope`).
   - At least **20 rows per language** to be officially reported in language-stratified benchmark evaluations.
   - Test rows are **never** trained, tuned, or cross-validated on.

---

## 5. Intent Taxonomy (The 18 Team Topics)

| # | Intent Key | Description | Handler / Data Source in Repo | Status |
|---|---|---|---|---|
| 1 | `attendance` | Attendance %, bunk allowance, consecutive recovery classes | `get_attendance_summary` & `DataRepository.get_attendance` | Handled |
| 2 | `exams` | Midterm, CIE, summative examination dates, venues, timings | `get_exams_summary` & `DataRepository.get_exams` | Handled |
| 3 | `marks` | Internal marks, CGPA/SGPA, grade cards, backlogs | `get_marks_summary` & `DataRepository.get_marks` | Handled |
| 4 | `fees` | Tuition balance, pending dues, late payment fines, fee deadlines | `get_fees_summary` & `DataRepository.get_fees` | Handled |
| 5 | `timetable` | Daily class schedule, lecture time slots, classroom & lab venues | `get_timetable_summary` & `DataRepository.get_timetable` | Handled |
| 6 | `curriculum` | Graduation credit requirements, degree audit, course roadmap | `get_curriculum_summary` & `DataRepository.get_curriculum` | Handled |
| 7 | `faculty` | Mentor, class teacher, counselor contact, phone, cabin | `DataRepository.get_student_advisors` | Handled |
| 8 | `library` | Borrowed book circulation, due dates, renewal, overdue fine rules | `get_library_summary` & `DataRepository.get_library_lended_books` | Handled |
| 9 | `hostel` | Room allotment, mess timings, curfew hours, outpass, warden info | *No dedicated handler in repo* (passes through to general answering) | No handler |
| 10 | `transport` | Bus routes, shuttle timings, bus pass details, driver contacts | `DataRepository.get_transport_routes` (no NLU handler) | No handler |
| 11 | `circulars` | University circulars, official announcements, holiday notices | `DataRepository.search_circulars` (no dedicated NLU handler) | No handler |
| 12 | `events` | Campus fests, symposiums, hackathons, sports tournaments | `DataRepository.get_upcoming_events` (no NLU handler) | No handler |
| 13 | `clubs` | Extracurricular student club directory, joining procedures | `DataRepository.get_clubs` (inline in NLU engine) | Handled |
| 14 | `services` | Bonafide certificate, transit pass endorsement, ID card, grievance | `app.tools.services_tool.handle_service_request` | Handled |
| 15 | `policy_bylaws` | Academic regulations, 75% attendance rule, 65-74.9% condonation | `search_policies_and_circulars` | Handled |
| 16 | `distress_support` | Mental health crisis, despair, study burnout, anxiety | Supportive counseling response (`is_distress=False`) / Crisis check | Handled |
| 17 | `greeting_smalltalk` | Greetings, bot identity, start/menu onboarding | `generate_proactive_briefing` | Handled |
| 18 | `out_of_scope` | Inquiries unrelated to university academics or campus affairs | Polite guide response (or Gemini fallback) | Handled |

> [!NOTE]
> **Human Handover Rule**:
> Human administrative handover is handled via an immediate keyword rule outside the classifier (`is_human_handover`) and routes directly to Dean/HoD escalation with `routed_by="rules"`.

---

## 6. Style and Phrasing Guidelines

When creating questions, please write naturally as real students speak and type:
1. **Natural Typos & Slang**: Include realistic student misspellings: `"atndnc"`, `"attndnce"`, `"proff"`, `"midsem"`, `"bunk"`, `"re-eval"`.
2. **Short Fragments**: Examples: `"room no for cie today"`, `"fee waiver hospital"`, `"bonafide certificate form"`, `"hostel mess timings"`.
3. **Multilingual and Code-Mixed Phrasing**:
   - `en`: Standard student English.
   - `hinglish`: Hindi in Latin script (`"kitna attendance pending hai"`, `"fees bharne ki last date kab hai"`).
   - `te_roman`: Telugu in Latin script (`"attendance entha undi"`, `"repu exam ekkada"`).
   - `te` & `hi`: Native script queries contributed by native speakers.
4. **Data Hygiene & Privacy**:
   - Never include real student names, roll numbers, or passwords.
   - Use synthetic placeholders if needed (e.g., `24CSE001`, `Digital Electronics`, `Room 301`).

---

## 7. How to Validate Your Data

Before committing, run:

```bash
python ml/validate_data.py
```

To run in strict mode (which fails if any human quota or test author quota is unmet):

```bash
python ml/validate_data.py --strict
```
