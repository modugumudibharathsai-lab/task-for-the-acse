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
file_path = REPO_ROOT / "BACKEND" / "app" / "agent" / "nlu_engine.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Check if already enriched
if "is_explicit_nav = any(nv in q_lower" in content and '"redirect_path": "attendance"' in content:
    print("nlu_engine.py is already enriched with navigation actions and parameters.")
    sys.exit(0)

# 1. Update is_fast_record_query to return False for explicit navigation verbs
nav_exclusion = '''        nav_verbs = ["open", "go to", "take me to", "navigate to", "switch to", "view tab", "show tab", "kholo", "take me there", "go there"]
        if any(nv in q_lower for nv in nav_verbs):
            return False
        reasoning_indicators = ['''

if "nav_verbs = " not in content and "        reasoning_indicators = [" in content:
    content = content.replace("        reasoning_indicators = [", nav_exclusion, 1)

# 2. Update line in classify_and_reason to also check is_nav_request
old_line = "        if not cls.is_stress_or_concern(q_lower) and not cls.is_fast_record_query(q_lower):"
new_line = '''        is_explicit_nav = any(nv in q_lower for nv in ["open", "go to", "take me to", "navigate to", "show tab", "switch to", "view tab", "take me there", "go there", "kholo"])
        if not cls.is_stress_or_concern(q_lower) and (is_explicit_nav or not cls.is_fast_record_query(q_lower)):'''

if old_line in content:
    content = content.replace(old_line, new_line, 1)

# 3. Add redirect_path and action to route_classified_intent blocks
nav_mappings = {
    'if intent == "attendance":': (
        '"redirect_path": "attendance",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Attendance",\n'
        '                    "target": "attendance",\n'
        '                    "route": "/?tab=attendance"\n'
        '                },'
    ),
    'elif intent == "exams":': (
        '"redirect_path": "exams",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Examinations",\n'
        '                    "target": "exams",\n'
        '                    "route": "/?tab=exams"\n'
        '                },'
    ),
    'elif intent == "fees":': (
        '"redirect_path": "fees",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Fees & Ledgers",\n'
        '                    "target": "fees",\n'
        '                    "route": "/?tab=fees"\n'
        '                },'
    ),
    'elif intent == "timetable":': (
        '"redirect_path": "timetable",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Timetable",\n'
        '                    "target": "timetable",\n'
        '                    "route": "/?tab=timetable"\n'
        '                },'
    ),
    'elif intent == "marks":': (
        '"redirect_path": "marks",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Academic Marks",\n'
        '                    "target": "marks",\n'
        '                    "route": "/?tab=marks"\n'
        '                },'
    ),
    'elif intent == "curriculum":': (
        '"redirect_path": "curriculum",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Curriculum",\n'
        '                    "target": "curriculum",\n'
        '                    "route": "/?tab=curriculum"\n'
        '                },'
    ),
    'elif intent == "library":': (
        '"redirect_path": "library",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Library Portal",\n'
        '                    "target": "library",\n'
        '                    "route": "/?tab=library"\n'
        '                },'
    ),
    'elif intent == "faculty":': (
        '"redirect_path": "faculty",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Faculty Directory",\n'
        '                    "target": "faculty",\n'
        '                    "route": "/?tab=faculty"\n'
        '                },'
    ),
    'elif intent == "clubs":': (
        '"redirect_path": "clubs",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Student Clubs",\n'
        '                    "target": "clubs",\n'
        '                    "route": "/?tab=clubs"\n'
        '                },'
    ),
    'elif intent == "hostel":': (
        '"redirect_path": "hostel",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Hostel Portal",\n'
        '                    "target": "hostel",\n'
        '                    "route": "/?tab=hostel"\n'
        '                },'
    ),
    'elif intent == "transport":': (
        '"redirect_path": "transport",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Transport & Buses",\n'
        '                    "target": "transport",\n'
        '                    "route": "/?tab=transport"\n'
        '                },'
    ),
    'elif intent == "circulars":': (
        '"redirect_path": "circulars",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Official Circulars",\n'
        '                    "target": "circulars",\n'
        '                    "route": "/?tab=circulars"\n'
        '                },'
    ),
    'elif intent == "events":': (
        '"redirect_path": "events",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Campus Events",\n'
        '                    "target": "events",\n'
        '                    "route": "/?tab=events"\n'
        '                },'
    ),
    'elif intent == "policy_bylaws":': (
        '"redirect_path": "policies",\n'
        '                "action": {\n'
        '                    "type": "navigate",\n'
        '                    "label": "Go to Policies & Regulations",\n'
        '                    "target": "policies",\n'
        '                    "route": "/?tab=policies"\n'
        '                },'
    )
}

# Now for each intent block in route_classified_intent, find its return dict ending with "routed_by": routed_by,
for intent_header, nav_code in nav_mappings.items():
    idx = content.find(intent_header)
    if idx == -1:
        continue
    target_str = '"routed_by": routed_by,'
    sub_idx = content.find(target_str, idx)
    if sub_idx != -1 and sub_idx < idx + 2500:
        if "redirect_path" not in content[sub_idx:sub_idx + 150]:
            replacement_str = f'{target_str}\n                {nav_code}'
            content = content[:sub_idx] + replacement_str + content[sub_idx + len(target_str):]
            print(f"Enriched {intent_header}")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Enriched nlu_engine.py with navigation successfully")
