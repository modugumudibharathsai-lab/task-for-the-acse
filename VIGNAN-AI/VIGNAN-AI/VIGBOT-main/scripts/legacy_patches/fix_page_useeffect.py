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
page_file = REPO_ROOT / "FRONTEND" / "src" / "app" / "page.tsx"

with open(page_file, "r", encoding="utf-8") as f:
    text = f.read()

target = 'import React, { useState } from "react";'
replacement = 'import React, { useState, useEffect } from "react";'

if "useEffect" in text:
    print("useEffect already imported in page.tsx")
elif target in text:
    text = text.replace(target, replacement, 1)
    with open(page_file, "w", encoding="utf-8") as f:
        f.write(text)
    print("Added useEffect to page.tsx")
else:
    print("Notice: target import statement not found in page.tsx")
