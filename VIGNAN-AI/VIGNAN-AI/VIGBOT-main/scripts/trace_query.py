import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "BACKEND"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.database import DatabaseSession
from app.agent.nlu_engine import NLUEngine

session = DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")

queries = [
    "Where can I book the seminar hall?",
    "How do I reserve the cricket ground for Saturday?",
    "What is the process to book the auditorium?",
    "Where do I lodge a grievance regarding faculty evaluation?",
    "kholo isko",
    "actually cancel that, don't submit",
    "Explain B+ Tree indexing with a simple diagram"
]

for q in queries:
    res = NLUEngine.classify_and_reason(session, q, [], {}, "en")
    print("Q:", q)
    print("  redirect_path:", res.get("redirect_path"))
    print("  category:", res.get("category"))
    print("  routed_by:", res.get("routed_by"))
    print("  action:", res.get("action"))
    print("---")
