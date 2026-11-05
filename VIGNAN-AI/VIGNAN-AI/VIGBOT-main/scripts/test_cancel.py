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
from app.agent.universal_nlu import UniversalNLU
from app.agent.nlu_engine import NLUEngine

session = DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")
history = [
    {"role": "user", "content": "I want to apply for a bonafide certificate"},
    {"role": "assistant", "content": "Please provide the purpose for your certificate."}
]

res = UniversalNLU.resolve_and_execute(session, "actually cancel that, don't submit", conversation_history=history)
print("resolve_and_execute cancel:", res.get("content")[:100] if res else "None")

res_nlu = NLUEngine.classify_and_reason(session, "actually cancel that, don't submit", history, {}, "en")
print("nlu_engine cancel:", res_nlu.get("content")[:100] if res_nlu else "None")
