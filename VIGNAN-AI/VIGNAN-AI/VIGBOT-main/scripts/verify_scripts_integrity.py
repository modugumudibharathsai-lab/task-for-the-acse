import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
LEGACY_DIR = SCRIPTS_DIR / "legacy_patches"
PYTHON_BIN = sys.executable

standing_scripts = sorted([
    f.name for f in SCRIPTS_DIR.glob("*.py")
    if f.name != "verify_scripts_integrity.py"
])

legacy_scripts = sorted([
    f.name for f in LEGACY_DIR.glob("*.py")
]) if LEGACY_DIR.exists() else []

print(f"Discovered {len(standing_scripts)} standing scripts and {len(legacy_scripts)} archived patches:")
print("Standing scripts:")
for s in standing_scripts:
    print(f"  - {s}")
if legacy_scripts:
    print("Archived patch scripts:")
    for s in legacy_scripts:
        print(f"  - legacy_patches/{s}")

print("\n" + "=" * 60)
print("PHASE 1: RUNNING STANDING SCRIPTS FROM REPOSITORY ROOT")
print("=" * 60)

root_failures = []
for s in standing_scripts:
    script_path = str(SCRIPTS_DIR / s)
    print(f"Running '{s}' from repo root... ", end="", flush=True)
    res = subprocess.run(
        [PYTHON_BIN, script_path],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode == 0:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (exit {res.returncode})")
        print("--- STDERR ---")
        print(res.stderr[:500])
        print("--- STDOUT ---")
        print(res.stdout[:500])
        root_failures.append(s)

print("\n" + "=" * 60)
print("PHASE 2: RUNNING STANDING SCRIPTS FROM INSIDE SCRIPTS/ DIRECTORY")
print("=" * 60)

sub_failures = []
for s in standing_scripts:
    print(f"Running '{s}' inside scripts/... ", end="", flush=True)
    res = subprocess.run(
        [PYTHON_BIN, s],
        cwd=str(SCRIPTS_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode == 0:
        print("✅ PASS")
    else:
        print(f"❌ FAIL (exit {res.returncode})")
        print("--- STDERR ---")
        print(res.stderr[:500])
        print("--- STDOUT ---")
        print(res.stdout[:500])
        sub_failures.append(s)

print("\n" + "=" * 60)
print("PHASE 3: VERIFYING ARCHIVED PATCHES IDEMPOTENCY")
print("=" * 60)

patch_failures = []
for s in legacy_scripts:
    script_path = str(LEGACY_DIR / s)
    print(f"Running 'legacy_patches/{s}'... ", end="", flush=True)
    res = subprocess.run(
        [PYTHON_BIN, script_path],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if res.returncode == 0:
        print("✅ PASS (Idempotent)")
    else:
        print(f"❌ FAIL (exit {res.returncode})")
        print("--- STDERR ---")
        print(res.stderr[:500])
        patch_failures.append(s)

print("\n" + "=" * 60)
print("BATCH SCRIPTS INTEGRITY AUDIT SUMMARY")
print("=" * 60)
print(f"Standing Scripts Tested:    {len(standing_scripts)}")
print(f"Archived Patches Tested:    {len(legacy_scripts)}")
print(f"Repo Root Failures:         {len(root_failures)}")
print(f"Scripts Subdir Failures:    {len(sub_failures)}")
print(f"Patch Idempotency Failures: {len(patch_failures)}")

if root_failures or sub_failures or patch_failures:
    sys.exit(1)
else:
    print("\n🎉 ALL SCRIPTS & PATCHES PASSED WITH ZERO ERRORS!")
    sys.exit(0)
