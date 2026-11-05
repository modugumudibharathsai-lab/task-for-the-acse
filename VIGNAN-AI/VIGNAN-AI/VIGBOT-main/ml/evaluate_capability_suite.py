"""
Comprehensive Capability & Action Intelligence Evaluator for VIGBOT.
Executes the 504 generated test cases across all 28 application capabilities,
measures intent accuracy, feature identification, false-action rates,
and verifies zero unauthorized writes and zero fabricated tickets.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BACKEND")))

from app.agent.universal_nlu import UniversalNLU
from app.agent.capability_registry import (
    APPLICATION_CAPABILITIES,
    CommunicationIntent,
    OperationType
)
from app.agent.nlu_engine import NLUEngine
from app.database import DatabaseSession, DataRepository


def run_capability_evaluation() -> Dict[str, Any]:
    suite_path = "BACKEND/artifacts/capability_test_suite.json"
    if not os.path.exists(suite_path):
        from ml.generate_capability_tests import generate_master_test_suite
        test_suite = generate_master_test_suite()
    else:
        with open(suite_path, "r", encoding="utf-8") as f:
            test_suite = json.load(f)

    session = DatabaseSession(student_id="24CSE001", user_id="user_24CSE001")
    total_cases = len(test_suite)
    print(f"\n=================================================================")
    print(f"RUNNING VIGBOT UNIVERSAL INTELLIGENCE BENCHMARK ({total_cases} CASES)")
    print(f"=================================================================\n")

    correct_features = 0
    correct_intents = 0
    false_writes = 0
    false_confirmations = 0
    navigation_successes = 0
    total_nav_requests = 0
    total_info_requests = 0
    total_action_requests = 0

    dimension_metrics = {}
    feature_metrics = {}
    failures = []

    start_eval_time = time.time()

    for idx, item in enumerate(test_suite, start=1):
        q = item["query"]
        expected_feat = item["feature_id"]
        expected_intent = item["expected_intent"]
        expected_tab = item["expected_tab"]
        dimension = item["dimension"]

        dim_entry = dimension_metrics.setdefault(dimension, {"total": 0, "correct_feature": 0, "correct_intent": 0})
        dim_entry["total"] += 1

        feat_entry = feature_metrics.setdefault(expected_feat, {"total": 0, "correct_feature": 0, "correct_intent": 0})
        feat_entry["total"] += 1

        # Count intents
        if expected_intent == CommunicationIntent.NAVIGATION_REQUEST:
            total_nav_requests += 1
        elif expected_intent == CommunicationIntent.INFORMATION_REQUEST:
            total_info_requests += 1
        elif expected_intent == CommunicationIntent.ACTION_REQUEST:
            total_action_requests += 1

        # Execute resolution
        t0 = time.time()
        detected_intent = UniversalNLU.parse_communication_intent(q)
        detected_cap = UniversalNLU.resolve_contextual_capability(q)
        detected_tab = detected_cap["frontend_tab"] if detected_cap else None

        # Execute full NLUEngine pipeline
        res = NLUEngine.classify_and_reason(
            session=session,
            query=q,
            conversation_history=[],
            context_data={},
            language="en"
        )
        elapsed = (time.time() - t0) * 1000.0

        res_content = res.get("content", "")
        res_redirect = res.get("redirect_path")
        res_action = res.get("action")

        # Check Feature Match
        feat_match = (detected_cap and detected_cap["feature_id"] == expected_feat) or (res_redirect == expected_tab)
        if feat_match:
            correct_features += 1
            dim_entry["correct_feature"] += 1
            feat_entry["correct_feature"] += 1

        # Check Intent Match
        intent_match = (detected_intent == expected_intent) or (
            expected_intent == CommunicationIntent.NAVIGATION_REQUEST and res_action is not None and res_action.get("type") == "navigate"
        )
        if intent_match:
            correct_intents += 1
            dim_entry["correct_intent"] += 1
            feat_entry["correct_intent"] += 1

        # Check Navigation
        if expected_intent == CommunicationIntent.NAVIGATION_REQUEST:
            if res_redirect == expected_tab or (res_action and res_action.get("target") == expected_tab):
                navigation_successes += 1

        # CRITICAL SAFETY CHECK: False writes & Fabricated Confirmations
        # If inquiry is informational or navigational, it MUST NOT create a service ticket or claim success!
        if expected_intent in (CommunicationIntent.INFORMATION_REQUEST, CommunicationIntent.NAVIGATION_REQUEST):
            if "SR-2026-" in res_content or "Service Request Created" in res_content:
                false_writes += 1
                false_confirmations += 1
                failures.append({
                    "test_id": item["test_id"],
                    "query": q,
                    "reason": "FALSE_WRITE: Created ticket for informational/navigational query",
                    "content_snippet": res_content[:150]
                })

        if not feat_match and len(failures) < 15:
            failures.append({
                "test_id": item["test_id"],
                "query": q,
                "dimension": dimension,
                "expected_feature": expected_feat,
                "detected_feature": detected_cap["feature_id"] if detected_cap else None,
                "detected_tab": detected_tab
            })

    total_time = time.time() - start_eval_time
    avg_latency = (total_time / total_cases) * 1000.0

    feat_acc = (correct_features / total_cases) * 100.0
    intent_acc = (correct_intents / total_cases) * 100.0
    nav_acc = (navigation_successes / max(1, total_nav_requests)) * 100.0
    false_write_rate = (false_writes / total_cases) * 100.0

    report = {
        "benchmark_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_test_cases": total_cases,
        "total_capabilities": len(APPLICATION_CAPABILITIES),
        "overall_feature_accuracy_pct": round(feat_acc, 2),
        "overall_intent_accuracy_pct": round(intent_acc, 2),
        "navigation_accuracy_pct": round(nav_acc, 2),
        "false_write_operations": false_writes,
        "false_success_confirmations": false_confirmations,
        "false_write_rate_pct": round(false_write_rate, 4),
        "average_latency_ms": round(avg_latency, 2),
        "dimension_breakdown": {
            dim: {
                "total": data["total"],
                "feature_accuracy_pct": round((data["correct_feature"] / data["total"]) * 100.0, 2),
                "intent_accuracy_pct": round((data["correct_intent"] / data["total"]) * 100.0, 2)
            }
            for dim, data in dimension_metrics.items()
        },
        "sample_failures": failures[:10]
    }

    # Print clean Markdown summary
    print(f"\n================ BENCHMARK RESULTS SUMMARY ================")
    print(f"Total Test Cases Evaluated:       {total_cases}")
    print(f"Overall Feature Accuracy:         {feat_acc:.2f}% ({correct_features}/{total_cases})")
    print(f"Overall Intent Accuracy:          {intent_acc:.2f}% ({correct_intents}/{total_cases})")
    print(f"Navigation Accuracy:              {nav_acc:.2f}% ({navigation_successes}/{total_nav_requests})")
    print(f"False Write Operations:           {false_writes} (Target: 0)")
    print(f"False Success Confirmations:      {false_confirmations} (Target: 0)")
    print(f"Average Execution Latency:        {avg_latency:.2f} ms/query")
    print(f"===========================================================\n")

    print(f"| Dimension | Total | Feature Acc (%) | Intent Acc (%) |")
    print(f"|---|---|---|---|")
    for dim, d in report["dimension_breakdown"].items():
        print(f"| `{dim}` | {d['total']} | {d['feature_accuracy_pct']}% | {d['intent_accuracy_pct']}% |")

    # Save artifact
    artifact_path = "BACKEND/artifacts/universal_intelligence_benchmark_results.json"
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved structured evaluation report to {artifact_path}")

    return report


if __name__ == "__main__":
    run_capability_evaluation()

