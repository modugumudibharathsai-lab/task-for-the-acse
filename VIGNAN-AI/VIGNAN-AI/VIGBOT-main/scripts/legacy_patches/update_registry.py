import sys
import re
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
file_path = REPO_ROOT / "BACKEND" / "app" / "agent" / "capability_registry.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if 'APPLICATION_CAPABILITIES["circulars"]' in content and '"examinations"' in content:
    print("capability_registry.py is already updated with domain overrides.")
    sys.exit(0)

target = '"exam", "exams", "examination", "hall ticket"'
replacement = '"exam", "exams", "examination", "examinations", "assessment", "assessments", "hall ticket"'
if target in content:
    content = content.replace(target, replacement, 1)

override_target = "    # Semantic keyword scoring using whole-word boundaries"
override_replacement = """    if any(re.search(r"\\b" + re.escape(k) + r"\\b", q_norm) for k in ["circular", "circulars", "official circular"]):
        return APPLICATION_CAPABILITIES["circulars"]
    if any(re.search(r"\\b" + re.escape(k) + r"\\b", q_norm) for k in ["calendar", "academic calendar"]):
        return APPLICATION_CAPABILITIES["calendar"]
    if any(re.search(r"\\b" + re.escape(k) + r"\\b", q_norm) for k in ["placement", "placements", "campus placement", "recruitment"]):
        return APPLICATION_CAPABILITIES["career"]
    if any(re.search(r"\\b" + re.escape(k) + r"\\b", q_norm) for k in ["exam", "exams", "examination", "examinations", "assessment", "assessments"]):
        return APPLICATION_CAPABILITIES["exams"]
    if any(re.search(r"\\b" + re.escape(k) + r"\\b", q_norm) for k in ["admin console", "admin panel", "admin portal", "staff portal", "admin"]):
        return APPLICATION_CAPABILITIES["admin"]

    # Semantic keyword scoring using whole-word boundaries"""

if override_target in content:
    content = content.replace(override_target, override_replacement, 1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated capability_registry.py successfully")
