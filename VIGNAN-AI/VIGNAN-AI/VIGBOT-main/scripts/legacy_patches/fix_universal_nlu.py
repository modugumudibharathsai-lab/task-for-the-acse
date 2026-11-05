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
file_path = REPO_ROOT / "BACKEND" / "app" / "agent" / "universal_nlu.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add Hinglish pronouns to HINGLISH_TRANSLATIONS
old_translations = '''        "meri": "my",
        "mera": "my",
        "apna": "my"
    }'''

new_translations = '''        "meri": "my",
        "mera": "my",
        "apna": "my",
        "isko": "it",
        "use": "it",
        "ise": "it",
        "usko": "that",
        "ye": "this",
        "yeh": "this",
        "wo": "that",
        "woh": "that"
    }'''

if old_translations in content:
    content = content.replace(old_translations, new_translations, 1)

# Add anaphora triggers
old_anaphora = '''        anaphora_triggers = [
            "open it", "take me there", "go there", "show it", "navigate there",
            "open that", "open the tab", "kholo", "yes", "yes please", "sure",
            "open page", "take me", "view it", "show that", "let's go"
        ]'''

new_anaphora = '''        anaphora_triggers = [
            "open it", "take me there", "go there", "show it", "navigate there",
            "open that", "open the tab", "kholo", "yes", "yes please", "sure",
            "open page", "take me", "view it", "show that", "let's go",
            "open this", "show this", "kholo isko", "isko kholo", "open", "kholo"
        ]'''

if old_anaphora in content:
    content = content.replace(old_anaphora, new_anaphora, 1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated universal_nlu.py successfully")
