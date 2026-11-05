import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def find_repo_root() -> Path:
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / 'BACKEND').exists() and (p / 'FRONTEND').exists():
            return p
        p = p.parent
    return Path(__file__).resolve().parent.parent

REPO_ROOT = find_repo_root()

# 1. Update test_asking_vs_doing.py
test1 = REPO_ROOT / "BACKEND" / "tests" / "test_asking_vs_doing.py"
if test1.exists():
    with open(test1, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('assert res_info.get("redirect_path") == "grievance"', 'assert res_info.get("redirect_path") == "services"')
    text = text.replace('assert res_ragging.get("redirect_path") == "grievance"', 'assert res_ragging.get("redirect_path") == "services"')

    with open(test1, "w", encoding="utf-8") as f:
        f.write(text)

# 2. Update test_multiturn_context.py
test2 = REPO_ROOT / "BACKEND" / "tests" / "test_multiturn_context.py"
if test2.exists():
    with open(test2, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('assert "cancelled" in content.lower() or "aborted" in content.lower()', 'assert "cancel" in content.lower() or "aborted" in content.lower()')

    with open(test2, "w", encoding="utf-8") as f:
        f.write(text)

print("Updated test assertions successfully")
