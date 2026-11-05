"""
General AI Quality & Academic Tutoring Integrity Test for VIGBOT Phase 14 (Phase 7).
Verifies that VIGBOT remains a versatile academic tutor across:
1. Programming (Java, C#, Python)
2. Data Structures & Algorithms
3. Database Management Systems
4. Mathematics & Discrete Math
5. University Exam Answer Preparation (10-mark structured answers with diagrams)
6. General Knowledge & Reasoning
7. Non-forced routing (verifying general academic queries are NOT forced into university routes)
"""

import os
import sys
import json
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


def run_general_ai_quality_evaluation():
    session = DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")

    academic_test_cases = [
        {
            "topic": "Programming (C# & Java)",
            "query": "Explain how garbage collection works in Java vs .NET CLR with generations",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "DSA (Graph Algorithms)",
            "query": "Explain Dijkstra's shortest path algorithm and its time complexity with min-heap vs adjacency matrix",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "DBMS (ACID & Isolation)",
            "query": "Explain the four ACID properties in DBMS and what phantom read anomaly is",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "Mathematics (Calculus)",
            "query": "How do you evaluate the limit of (sin x)/x as x approaches 0 using L'Hopital's rule?",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "Exam Preparation (10-mark standard)",
            "query": "Give me a 10-mark university examination answer on 1NF, 2NF, 3NF and BCNF with table diagrams",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "Pedagogical Simplification",
            "query": "Explain how a hash map handles collisions like I'm a complete beginner",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        },
        {
            "topic": "Multilingual / Hinglish Tutoring",
            "query": "Bhai virtual memory and paging ka concept Hinglish mein practical example ke saath samjhao",
            "expected_category": "ACADEMIC_TUTORING",
            "must_not_route_to_university": True
        }
    ]

    print("\n--- RUNNING GENERAL ACADEMIC AI QUALITY EVALUATION ---")
    results = []

    for c in academic_test_cases:
        q = c["query"]
        res = NLUEngine.classify_and_reason(session, q, [], {}, "en")
        category = res.get("category")
        content = res.get("content", "")
        redirect = res.get("redirect_path")
        source_agent = res.get("source_agent", "")

        is_tutoring = (category == "ACADEMIC_TUTORING" or "Academic" in source_agent)
        is_not_forced = (redirect is None)
        has_substantive_content = len(content) > 100

        passed = is_tutoring and is_not_forced and has_substantive_content
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"[{status}] {c['topic']}: '{q[:45]}...' -> cat={category}, redirect={redirect}, chars={len(content)}")
        results.append({
            "topic": c["topic"],
            "query": q,
            "category": category,
            "redirect_path": redirect,
            "source_agent": source_agent,
            "content_length": len(content),
            "passed": passed
        })

    all_passed = all(r["passed"] for r in results)
    print(f"\nAll general AI academic queries routed to academic tutoring without forced university navigation: {all_passed}")
    return results


if __name__ == "__main__":
    run_general_ai_quality_evaluation()

