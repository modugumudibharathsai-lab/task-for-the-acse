# VIGBOT: Deployment and Operations Guide

> **Production Deployment | Hybrid 3-Tier Architecture | Privacy-Preserving Cloud Fallback**

This guide provides operational and deployment procedures for the **VIGBOT** platform:

1. **System Architecture:** Hybrid 3-tier routing (Rules -> Local Classifier -> Gemini 2.5 Flash).
2. **Production Deployment:** Hosting the Next.js frontend on Vercel, the FastAPI backend on Render / Docker, and PostgreSQL on Neon.
3. **Database Migration:** Migrating the seeded SQLite database (70 student records) to PostgreSQL.
4. **Operations & Monitoring:** Checking system health, privacy logs, and routing tiers.

---

## 1. System Architecture

VIGBOT operates on a **3-Tier Hybrid Intelligence Stack** designed for low latency, deterministic accuracy on university policies, and robust fallback for open-ended queries:

```
                  ┌─────────────────────────────────────┐
                  │   Student Submits Query to API      │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │  Tier 1: Deterministic Guardrails   │
                  │  - Distress Safety Interceptor      │
                  │  - Domain Rule Handlers (Academic)  │
                  └──────────────────┬──────────────────┘
                                     │ (unmatched / dynamic)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │  Tier 2: Local ML Intent Classifier │
                  │  - CPU TF-IDF + Logistic Regression │
                  │  - 18 Intent Categories             │
                  │  - High Confidence Threshold Match  │
                  └──────────────────┬──────────────────┘
                                     │ (below threshold / unclassified)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │  Tier 3: Cloud LLM Fallback         │
                  │  - Google Gemini 2.5 Flash          │
                  │  - PII-Redacted Context Anonymizer  │
                  │  - Grounded Academic Guidelines     │
                  └─────────────────────────────────────┘
```

### Core Components
* **Tier 1 (Deterministic Guardrails):**
  - **Distress Interceptor:** Immediate keyword detection for self-harm or distress; triggers Emergency Counseling emergency counseling protocol without invoking cloud LLMs.
  - **Academic Domain Rules:** Deterministic calculations for attendance deficit (mandatory 75% threshold, medical condonation 65%–75%), fee balances, credit audits, and timetable lookup.
  - **Row-Level Security (RLS):** Student data access strictly isolated by authenticated user session.
* **Tier 2 (Local ML Intent Classifier):**
  - Fast, zero-GPU-overhead TF-IDF vectorizer + Logistic Regression classifier.
  - Classifies student intent into one of 18 domain intents and triggers domain specific data fetching.
* **Tier 3 (Cloud LLM Fallback):**
  - Uses `gemini-2.5-flash` via Google GenAI SDK.
  - **Privacy Enforcement:** Student PII (name, roll number, student ID) is automatically redacted and replaced with `[Authenticated Student]` prior to transmitting prompts to cloud endpoints.

---

## 2. Production Deployment Guide

### Step 1: Database Setup (Neon PostgreSQL)
For persistent production storage, provision a managed PostgreSQL database on Neon:
1. Register at [neon.tech](https://neon.tech) and create a project (e.g. `vigbot-db`).
2. Copy the connection string:
   ```text
   postgresql://user:password@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Seed / Migrate Student Records
The local SQLite database (`database/vigbot.db`) contains 70 seeded student records (Section 7 and test accounts), faculty, course schedules, attendance logs, and academic policies.
To migrate to Neon PostgreSQL, run:
```powershell
.\BACKEND\.venv\Scripts\python BACKEND/scripts/migrate_sqlite_to_postgres.py "postgresql://user:password@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"
```
The migration script will verify table structures and insert the 70 student records along with associated timetable, marks, and attendance data.

### Step 3: Deploy Backend on Render (FastAPI Docker)
1. In [Render](https://render.com), create a **New Web Service** connected to your GitHub repository.
2. Configure settings:
   - **Root Directory:** `BACKEND`
   - **Runtime:** `Docker`
   - **Instance Type:** `Free` or `Starter`
3. Set Environment Variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string (or SQLite path) | `postgresql://...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model ID for fallback | `gemini-2.5-flash` |
| `LLM_PROVIDER` | Default LLM provider | `gemini` (or `local` / `mock`) |
| `FRONTEND_ORIGINS` | Permitted frontend CORS origins | `["https://your-frontend.vercel.app"]` |
| `ALLOW_PIPELINE_TEST_MODEL` | Flag for test model usage | `false` |

4. Verify backend health once deployed:
   ```bash
   curl https://your-backend.onrender.com/api/v1/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "agent": "VIGBOT (Academic Concierge & Executive Interface)",
     "rls_guardrail_enforced": true,
     "llm_provider": "gemini"
   }
   ```

### Step 4: Deploy Frontend on Vercel (Next.js)
1. In [Vercel](https://vercel.com), import the repository.
2. Set **Root Directory** to `FRONTEND`.
3. Set Environment Variables:
   - `NEXT_PUBLIC_BACKEND_URL`: `https://your-backend.onrender.com/api/v1`
4. Deploy. Ensure CORS is enabled on the backend for the generated Vercel domain.

---

## 3. Operational Verification & Diagnostics

### Routing Tier Verification
Each assistant message response returned by `POST /api/v1/conversations/{id}/messages` includes routing metadata:
* `routed_by`:
  - `"rules"`: Handled by Tier 1 deterministic rules, calculations, or distress interceptor.
  - `"classifier"`: Handled by Tier 2 ML intent classification.
  - `"gemini"`: Handled by Tier 3 Google Gemini cloud fallback.
  - `"classifier_pipeline_test"`: Handled by dry-run testing pipeline model.
* `used_fallback`: Boolean indicating whether Tier 3 cloud fallback was engaged.

### Privacy Compliance
* Student query texts are **never** logged to stdout or persistent log stores.
* Inbound and outbound intent logging records only:
  ```
  Intent classification: intent=<intent_name> confidence=<score> is_confident=<bool> routed_by=<tier>
  ```
* System prompts sent to cloud LLMs undergo automated PII redaction: `roll_no`, `student_id`, and `full_name` are stripped and replaced with `[Authenticated Student]`.

### Running Tests
To verify all backend services and classifiers:
```powershell
cd BACKEND
.\.venv\Scripts\python -m pytest tests/ -v
```
To verify data guardrails across team author CSVs:
```powershell
.\BACKEND\.venv\Scripts\python -m pytest tests/test_data_guardrails.py -v
```
