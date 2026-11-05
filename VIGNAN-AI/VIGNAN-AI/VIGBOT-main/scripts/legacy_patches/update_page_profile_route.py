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
    content = f.read()

if "handleNavigateTab" in content and 'activeTab === "student-profile"' in content:
    print("page.tsx is already updated with handleNavigateTab and student-profile support.")
    sys.exit(0)

target = """  const { nextClassSlot, formattedNextExamDate } = useDynamicSchedule();"""

replacement = """  const { nextClassSlot, formattedNextExamDate } = useDynamicSchedule();

  useEffect(() => {
    if (activeTab === "student-profile" || activeTab === "profile") {
      setIsProfileOpen(true);
      setActiveTab("home");
    }
  }, [activeTab]);

  const handleNavigateTab = (tab: string) => {
    if (tab === "student-profile" || tab === "profile") {
      setIsProfileOpen(true);
    } else {
      setActiveTab(tab);
    }
  };"""

if target in content:
    content = content.replace(target, replacement, 1)
    content = content.replace("onNavigateTab={(tab) => setActiveTab(tab)}", "onNavigateTab={handleNavigateTab}")
    with open(page_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated page.tsx with handleNavigateTab and student-profile support")
else:
    print("Notice: target insertion point not found in page.tsx.")
