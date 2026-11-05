# VIGBOT — Final Project Directory & Architecture Reference

This document provides the authoritative structural and architectural overview of the cleaned, optimized, production-grade **VIGBOT** intelligent academic helpdesk repository.

---

## 1. Top-Level Repository Overview

```
C:\StudentHelpdesk\
├── archive/                      # Preserved ad-hoc inspection and debugging scripts
│   ├── legacy_launchers/         # Preserved historical launchers (start_live_agent65)
│   └── scratch/                  # Isolated scratch files (separated from production)
├── bin/                          # Standalone tunnel binaries (cloudflared, ngrok)
├── BACKEND/                      # FastAPI, Universal NLU, RAG & Database Services
│   ├── app/                      # Application core (Agent, API, Tools, Database)
│   ├── artifacts/                # Benchmark suites, intent model, evaluation outputs
│   ├── data/vigbot_research/     # Persistent Progress Manager & Checkpoints
│   ├── tests/                    # Pytest test suite (89 passing tests)
│   ├── .env.example              # Documented environment template
│   ├── Dockerfile                # Production container deployment
│   ├── main.py                   # FastAPI application entrypoint
│   └── requirements.txt          # Production Python dependencies
├── data/                         # Datasets & Skill Indexes
│   ├── authors/                  # Author-partitioned training data
│   ├── maps/                     # Google Maps Platform skills index
│   └── intents.csv               # Production intent training corpus
├── database/                     # Production SQLite Database
│   ├── vigbot.db                 # Canonical active SQLite database (5.21 MB)
│   └── student_helpdesk.db       # Original schema reference baseline (4.39 MB)
├── docs/                         # Architecture, deployment, and guide documentation
│   ├── API_DOCUMENTATION.md      # Backend REST API contract
│   ├── ARCHITECTURE.md           # Systems design and data flows
│   ├── DATA_SOURCES.md           # Institutional knowledge sources
│   ├── DEPLOYMENT_AND_OPERATIONS_GUIDE.md # Production deployment guide
│   ├── FALSE_ACTION_AUDIT.md     # Audit report on zero false writes
│   ├── FRONTEND_INTEGRATION.md   # Next.js frontend integration specification
│   ├── IMPLEMENTATION_REPORT.md  # Comprehensive Phase 13/14 report
│   ├── INTENT_MODEL_EXPLAINED.md # ML intent model architecture & math
│   └── UNIVERSAL_INTENT_ROUTING.md # NLU routing matrix & specifications
├── FRONTEND/                     # Next.js 16.3.4 (Turbopack) Full-Stack Web App
│   ├── src/app/                  # App Router pages and API routes
│   ├── src/components/           # 28 capability UI views & interactive components
│   ├── src/context/              # Global chat and authentication React context
│   ├── src/lib/                  # Client-side DB provider, AI engine, and API client
│   ├── src/types/                # TypeScript type definitions
│   ├── .env.example              # Documented frontend environment template
│   ├── package.json              # NPM dependencies and scripts
│   └── vigbot.db                 # Synchronized SQLite bundle for standalone deployments
├── ml/                           # Offline Machine Learning & Dataset Pipelines
│   ├── colab/                    # Google Colab training notebooks & zip packs
│   ├── train_intent.py           # Scikit-learn TF-IDF + LogisticRegression trainer
│   ├── evaluate_capability_suite.py # Capability matrix benchmark runner
│   └── generate_intent_dataset.py# Synthetic dataset generator
├── models/                       # Local offline LLM weights
│   ├── vigbot-academic-8b.gguf   # Primary 8B academic reasoning GGUF
│   └── vigbot-tutor-1b.gguf      # Low-latency 1B fallback GGUF
├── scripts/                      # Verified standing utilities & verification harnesses
│   ├── legacy_patches/           # Relocated historical idempotent patches
│   ├── build_full_operation_suite.py # Generates 252-case independent benchmark
│   ├── evaluate_independent_suite.py # Executes independent real-world benchmark
│   ├── run_adversarial_safety_suite.py # Adversarial safety & injection test suite
│   ├── verify_frontend_e2e.py    # Validates all 28 capabilities against UI tabs
│   ├── verify_scripts_integrity.py # End-to-end multi-stage script verification harness
│   └── resume_vigbot_research.py # Progress manager recovery CLI
├── tests/                        # Repository-level test suites
│   └── test_data_guardrails.py   # Row-level security & database isolation tests
├── .gitignore                    # Consolidated, clean Git ignore definitions
├── CLEANUP_FILE_MANIFEST.json    # Complete inventory of cleaned and archived files
├── CLEANUP_TEST_RESULTS.json     # Verification test results across all suites
├── FINAL_PROJECT_STRUCTURE.md    # This directory and architecture specification
├── PROJECT_CLEANUP_REPORT.md     # Comprehensive 18-section audit and refactoring report
└── README.md                     # Central project overview and quickstart guide
```

---

## 2. Backend Architecture (`BACKEND/`)

```
BACKEND/app/
├── agent/
│   ├── capability_registry.py    # 28 capabilities, 48 operations, precompiled regex matchers
│   ├── universal_nlu.py          # Communication intent parser & safe execution planner
│   ├── nlu_engine.py             # Layered cognitive dispatcher & multi-turn reasoning engine
│   ├── orchestrator.py           # 10-step student lifecycle orchestrator & RLS boundary
│   ├── intent_classifier.py      # TF-IDF + LogisticRegression intent inference service
│   ├── llm_client.py             # Multi-provider local/Gemini/Groq client with backoff
│   ├── prompts.py                # Academic persona, pedagogical, and safety system prompts
│   └── grounding_guard.py        # Hallucination prevention and citation validator
├── api/
│   ├── chat.py                   # /api/chat streaming and synchronous message endpoints
│   ├── conversations.py          # Conversation history and context management
│   ├── health.py                 # Service health check and model availability
│   ├── feedback.py               # Student response feedback collection
│   ├── admin.py                  # Administrative console APIs and analytics
│   └── voice.py                  # Multilingual voice transcription & synthesis
├── database.py                   # DataRepository with Row-Level Security (RLS) enforcement
└── tools/
    ├── academic_tool.py          # Attendance math, exam eligibility, GPA calculator
    ├── distress_tool.py          # Mandatory crisis intervention & counselor routing
    ├── services_tool.py          # Service requests, tracking, and document applications
    ├── vector_search_tool.py     # SQLite RAG search over university handbooks and circulars
    └── calendar_tool.py          # Academic calendar, holidays, and examination schedules
```

---

## 3. Frontend Architecture (`FRONTEND/`)

```
FRONTEND/src/
├── app/
│   ├── page.tsx                  # Main Helpdesk dashboard with 27 interactive capability tabs
│   ├── layout.tsx                # Root layout with providers, theme, and toast notifications
│   ├── admin/                    # Administrative dashboard and officer management
│   │   ├── page.tsx              # Admin overview & system metrics
│   │   └── login/page.tsx        # Staff authentication portal
│   └── api/                      # Edge and serverless route handlers
├── components/
│   ├── ChatInterface.tsx         # Conversational assistant UI with markdown and LaTeX
│   ├── NavigationBar.tsx         # Primary navigation drawer and tab switcher
│   ├── StructuredActionCard.tsx  # Dynamic action cards with one-click navigation pills
│   ├── AcademicAuditView.tsx     # Attendance calculator and exam eligibility dashboard
│   ├── LostAndFoundView.tsx      # Misplaced items listing, search, and claim modal
│   ├── FacilityBookingView.tsx   # Seminar hall and grounds reservation workspace
│   ├── GrievancePortalView.tsx   # SGRC complaints and Anti-Ragging emergency contacts
│   ├── StudentServicesView.tsx   # Certificates, ID card requests, and SLA tracking
│   ├── HostelManagementView.tsx  # Hostel rooms, mess menu, outpass, and curfew rules
│   ├── TransportScheduleView.tsx # Bus routes, stoppage timings, and pass renewal
│   ├── CareerPlacementView.tsx   # Campus recruitment drives, eligibility, and drives
│   ├── ExaminationsView.tsx      # Timetables, hall tickets, and results
│   ├── FeesManagementView.tsx    # Tuition fee dues, challans, and payment receipts
│   └── ... (28 capability views total)
├── context/
│   ├── AgentChatContext.tsx      # Real-time message streaming, active action listener
│   └── AuthContext.tsx           # Authenticated student session and RLS token store
└── lib/
    ├── api-client.ts             # Typed HTTP client communicating with FastAPI backend
    ├── db-provider.ts            # Client-side SQLite fallback provider
    └── ai-engine.ts              # Local hybrid inference engine for offline mode
```

---

## 4. Script Suite Architecture (`scripts/`)

```
scripts/
├── build_full_operation_suite.py     # Constructs the 252-case independent test benchmark
├── build_independent_dataset.py      # Generates synthetic edge cases across 8 dimensions
├── checkpoint_phase13.py             # Phase 13 progress and artifact checkpoint utility
├── checkpoint_phase14.py             # Phase 14 progress and artifact checkpoint utility
├── evaluate_independent_suite.py     # Evaluates 252 independent cases with zero false writes
├── resume_vigbot_research.py         # Autonomous resume manager for interrupted phases
├── run_adversarial_safety_suite.py   # Runs 15 adversarial attack and prompt injection tests
├── test_cancel.py                    # Tests cancellation and withdrawal intent routing
├── test_general_ai_quality.py        # Measures reasoning clarity, LaTeX math, and citations
├── test_multiturn_dialogue.py        # Validates 5-turn conversational state preservation
├── trace_query.py                    # Deep-trace debugger for single query execution flows
├── verify_frontend_e2e.py            # Verifies all 28 capabilities against UI components
├── verify_scripts_integrity.py       # Multi-stage execution harness for all standing scripts
└── legacy_patches/                   # Archived historical idempotent patches
    ├── enrich_navigation.py
    ├── fix_auditorium_and_test.py
    ├── fix_nlu_engine.py
    ├── fix_page_useeffect.py
    ├── fix_tests.py
    ├── fix_universal_nlu.py
    ├── update_page_profile_route.py
    └── update_registry.py
```

---

## 5. Persistent Research & Progress Storage (`BACKEND/data/vigbot_research/`)

```
BACKEND/data/vigbot_research/
├── progress.json             # Authoritative machine-readable execution state
├── PROGRESS.md               # Human-readable progress log with completed subtasks
├── phase_status.json         # High-level tracking across all 15 project phases
├── manifest.json             # Comprehensive inventory of research datasets and artifacts
├── errors.jsonl              # Append-only log of recoverable and fatal failures
├── checkpoints/              # Immutable state snapshots of completed phases
└── locks/                    # Process concurrency and duplicate-execution guards
```
