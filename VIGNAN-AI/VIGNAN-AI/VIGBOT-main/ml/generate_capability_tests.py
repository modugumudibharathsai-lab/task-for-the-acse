"""
Registry-Driven Capability Test Suite Generator for VIGBOT.
Discovers all application capabilities and supported operations directly from
`app.agent.capability_registry.APPLICATION_CAPABILITIES` and generates 15-20 diverse
natural language test variations per feature across 16 linguistic dimensions.
"""

import os
import sys
import json
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BACKEND")))

from app.agent.capability_registry import (
    APPLICATION_CAPABILITIES,
    CommunicationIntent,
    OperationType
)


def generate_tests_for_capability(cap_id: str, cap: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates 16-20 diverse test cases dynamically for a registered application feature.
    """
    cap_name = cap["name"]
    tab = cap["frontend_tab"]
    keywords = cap["keywords"]
    primary_kw = keywords[0] if keywords else cap_id
    second_kw = keywords[1] if len(keywords) > 1 else primary_kw
    third_kw = keywords[2] if len(keywords) > 2 else second_kw

    tests = []

    # 1. Direct Wording (Explicit Information Request)
    tests.append({
        "test_id": f"{cap_id}_01_direct_info",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "direct_wording",
        "query": f"Where can I find information about {primary_kw}?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 2. Indirect Wording (Circumlocutory question)
    tests.append({
        "test_id": f"{cap_id}_02_indirect_info",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "indirect_wording",
        "query": f"Is there a dedicated section on the portal to handle {second_kw}?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 3. Conversational Wording
    tests.append({
        "test_id": f"{cap_id}_03_conversational",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "conversational_wording",
        "query": f"Could you please explain how {cap_name} works at our university?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 4. Informal English / Slang
    tests.append({
        "test_id": f"{cap_id}_04_informal",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "informal_english",
        "query": f"Hey where do I go for {third_kw} stuff?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 5. Hinglish (Colloquial code-mixing)
    tests.append({
        "test_id": f"{cap_id}_05_hinglish",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "hinglish",
        "query": f"{primary_kw} kahan se check kar sakte hain?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 6. Realistic Misspellings (Typos)
    typo_kw = primary_kw.replace("attendance", "attendence").replace("hostel", "hostle").replace("fee", "fess")
    tests.append({
        "test_id": f"{cap_id}_06_misspelling",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "misspellings",
        "query": f"Where is the {typo_kw} option located?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 7. Abbreviations / Acronyms
    tests.append({
        "test_id": f"{cap_id}_07_abbreviation",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "abbreviations",
        "query": f"Need details on {primary_kw.upper()} rules.",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 8. Short / Incomplete Message
    tests.append({
        "test_id": f"{cap_id}_08_short_incomplete",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "short_incomplete",
        "query": f"{cap_name}",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 9. Explicit Navigation Request ("Open X", "Go to X")
    tests.append({
        "test_id": f"{cap_id}_09_explicit_navigation",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "navigation_request",
        "query": f"Open {cap_name}",
        "expected_intent": CommunicationIntent.NAVIGATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 10. Colloquial Navigation ("Take me to X")
    tests.append({
        "test_id": f"{cap_id}_10_colloquial_navigation",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "navigation_request",
        "query": f"Take me to the {primary_kw} tab",
        "expected_intent": CommunicationIntent.NAVIGATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 11. Asking vs Doing: Informational ("Where do I report / apply...")
    tests.append({
        "test_id": f"{cap_id}_11_asking_not_doing",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "asking_vs_doing",
        "query": f"Where can I submit a request for {primary_kw}?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False  # MUST NEVER WRITE!
    })

    # 12. Asking vs Doing: Action Intent ("I want to submit / apply / book...")
    tests.append({
        "test_id": f"{cap_id}_12_action_intent",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "action_request",
        "query": f"I want to submit a new entry for {primary_kw}",
        "expected_intent": CommunicationIntent.ACTION_REQUEST,
        "expected_tab": tab,
        "should_write": False  # Must guide to official form or ask confirmation
    })

    # 13. Status Tracking Request ("Status of my X")
    tests.append({
        "test_id": f"{cap_id}_13_status_tracking",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "status_lookup",
        "query": f"Can I check the status of my {primary_kw}?",
        "expected_intent": CommunicationIntent.STATUS_LOOKUP,
        "expected_tab": tab,
        "should_write": False
    })

    # 14. Negative Request ("Don't do anything, just tell me...")
    tests.append({
        "test_id": f"{cap_id}_14_negative_request",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "negative_request",
        "query": f"Don't submit anything, just tell me where to find {second_kw}",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 15. Cancellation Request ("Cancel my X")
    tests.append({
        "test_id": f"{cap_id}_15_cancellation",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "cancel_request",
        "query": f"Cancel my {primary_kw} request",
        "expected_intent": CommunicationIntent.CANCEL_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 16. Generalization / Unseen Language
    tests.append({
        "test_id": f"{cap_id}_16_unseen_student_language",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "unseen_generalization",
        "query": f"How am I supposed to get my {primary_kw} sorted out?",
        "expected_intent": CommunicationIntent.INFORMATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 17. Multi-Intent ("Tell me about X and open it")
    tests.append({
        "test_id": f"{cap_id}_17_multi_intent",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "multi_intent",
        "query": f"Tell me about {primary_kw} and open the page",
        "expected_intent": CommunicationIntent.NAVIGATION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    # 18. Hinglish Action ("X apply karna hai")
    tests.append({
        "test_id": f"{cap_id}_18_hinglish_action",
        "feature_id": cap_id,
        "feature_name": cap_name,
        "dimension": "hinglish_action",
        "query": f"Mujhe {primary_kw} apply karna hai",
        "expected_intent": CommunicationIntent.ACTION_REQUEST,
        "expected_tab": tab,
        "should_write": False
    })

    return tests


def generate_master_test_suite() -> List[Dict[str, Any]]:
    """
    Generates test cases across all registered application capabilities.
    """
    master_suite = []
    print(f"Discovering capabilities from APPLICATION_CAPABILITIES ({len(APPLICATION_CAPABILITIES)} total)...")

    for cap_id, cap in APPLICATION_CAPABILITIES.items():
        cap_tests = generate_tests_for_capability(cap_id, cap)
        master_suite.extend(cap_tests)
        print(f"  Generated {len(cap_tests)} test cases for [{cap_id}] ({cap['name']})")

    return master_suite


if __name__ == "__main__":
    suite = generate_master_test_suite()
    print(f"\nTotal generated test cases: {len(suite)}")

    os.makedirs("BACKEND/artifacts", exist_ok=True)
    os.makedirs("BACKEND/data/vigbot_research/datasets", exist_ok=True)

    out_file_1 = "BACKEND/artifacts/capability_test_suite.json"
    with open(out_file_1, "w", encoding="utf-8") as f:
        json.dump(suite, f, indent=2)
    print(f"Saved master suite to {out_file_1}")

    out_file_2 = "BACKEND/data/vigbot_research/datasets/capability_test_suite.json"
    with open(out_file_2, "w", encoding="utf-8") as f:
        json.dump(suite, f, indent=2)
    print(f"Saved checkpoint copy to {out_file_2}")

