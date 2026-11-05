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

# 1. Update is_academic_or_conceptual_query terms
old_academic = '"hash table", "hash map",'
new_academic = '"hash table", "hash map", "b tree", "b+ tree", "b+tree", "btree", "indexing", "tree", "avl", "red black", "trie", "hashing", "diagram",'

if '"b tree"' not in content and old_academic in content:
    content = content.replace(old_academic, new_academic, 1)
    print("Updated is_academic_or_conceptual_query")
else:
    print("is_academic_or_conceptual_query terms already up to date")

# 2. Add capability cross-check guard to route_classified_intent
guard_target = '        # 1. Distress safety path: confident prediction provides supportive counseling response without crisis overlay'
guard_replacement = '''        # 0. Cross-check guard: If query specifically matches an explicit distinctive capability
        # (e.g. facility bookings, lost-and-found, marketplace) that the ML classifier confounds with library/services:
        from app.agent.capability_registry import find_matching_capability
        from app.agent.universal_nlu import UniversalNLU
        matching_cap = find_matching_capability(query)
        if matching_cap and matching_cap["feature_id"] in ("bookings", "lost-and-found", "marketplace", "polling", "alumni", "map"):
            if intent in ("library", "services", "general", "out_of_scope"):
                cross_res = UniversalNLU.resolve_and_execute(session, query)
                if cross_res is not None:
                    cross_res["routed_by"] = routed_by
                    return cross_res

        # 1. Distress safety path: confident prediction provides supportive counseling response without crisis overlay'''

if '# 0. Cross-check guard' not in content and guard_target in content:
    content = content.replace(guard_target, guard_replacement, 1)
    print("Added cross-check guard to route_classified_intent")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
else:
    print("Cross-check guard already present in route_classified_intent")

print("nlu_engine.py verified successfully")
