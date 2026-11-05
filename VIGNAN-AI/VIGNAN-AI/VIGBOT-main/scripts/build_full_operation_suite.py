import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "BACKEND"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def build_exhaustive_independent_dataset() -> List[Dict[str, Any]]:
    # Load 48 operations from capability_operation_matrix.json
    matrix_path = REPO_ROOT / "BACKEND" / "artifacts" / "capability_operation_matrix.json"
    if not matrix_path.exists():
        raise FileNotFoundError(f"Capability operation matrix not found at: {matrix_path}")

    with open(matrix_path, "r", encoding="utf-8") as f:
        operations = json.load(f)

    # Import the hand-crafted realistic student scenarios from build_independent_dataset.py
    from scripts.build_independent_dataset import build_dataset as get_situational_scenarios
    master_dataset = get_situational_scenarios()

    print(f"Loaded {len(master_dataset)} hand-crafted situational scenarios.")
    print(f"Generating independent test cases for {len(operations)} operations...")

    # For each operation, generate appropriate targeted test cases across operation dimensions
    for op in operations:
        feat_id = op["feature_id"]
        feat_name = op["feature_name"]
        op_id = op["operation_id"]
        op_type = op["operation_type"]
        tab = op["frontend_tab"]
        is_write = op["is_write"]
        req_params = op["required_parameters"]
        is_admin = "Staff" in op["permission_requirements"] or "Admin" in op["permission_requirements"]

        # 1. Direct Request
        master_dataset.append({
            "test_id": f"op_{feat_id}_{op_id}_direct",
            "feature_id": feat_id,
            "operation_id": op_id,
            "operation_type": op_type,
            "query": f"I want to {op_type} my {op_id.replace('_', ' ')} in {feat_name}.",
            "expected_feature": feat_id,
            "expected_operation": op_type,
            "expected_intent": "ACTION_REQUEST" if is_write else "INFORMATION_REQUEST",
            "required_parameters": req_params,
            "is_write_operation": is_write,
            "safe_execution_decision": "prompt_missing_params" if (is_write and req_params) else ("require_confirmation" if is_write else "guidance_only"),
            "dimension": "direct_request"
        })

        # 2. Informational Question (Where/How) -> MUST BE READ-ONLY & NEVER WRITE
        master_dataset.append({
            "test_id": f"op_{feat_id}_{op_id}_info_ask",
            "feature_id": feat_id,
            "operation_id": op_id,
            "operation_type": op_type,
            "query": f"How does the {op_id.replace('_', ' ')} process work for {feat_name}?",
            "expected_feature": feat_id,
            "expected_operation": op_type,
            "expected_intent": "INFORMATION_REQUEST",
            "required_parameters": [],
            "is_write_operation": False,
            "safe_execution_decision": "guidance_only",
            "dimension": "informational_question"
        })

        # 3. Explicit Navigation Request
        master_dataset.append({
            "test_id": f"op_{feat_id}_{op_id}_nav",
            "feature_id": feat_id,
            "operation_id": op_id,
            "operation_type": "navigate",
            "query": f"Open the {feat_name} tab to {op_type} {op_id.replace('_', ' ')}",
            "expected_feature": feat_id,
            "expected_operation": "navigate",
            "expected_intent": "NAVIGATION_REQUEST",
            "required_parameters": [],
            "is_write_operation": False,
            "safe_execution_decision": "navigate_only",
            "dimension": "navigation_request"
        })

        # 4. Negative Instruction ("Do NOT execute...")
        master_dataset.append({
            "test_id": f"op_{feat_id}_{op_id}_negative",
            "feature_id": feat_id,
            "operation_id": op_id,
            "operation_type": op_type,
            "query": f"Do not execute any {op_id.replace('_', ' ')}, just explain the instructions.",
            "expected_feature": feat_id,
            "expected_operation": op_type,
            "expected_intent": "INFORMATION_REQUEST",
            "required_parameters": [],
            "is_write_operation": False,
            "safe_execution_decision": "guidance_only",
            "dimension": "negative_instruction"
        })

        # 5. Missing Parameters (for operations that require parameters)
        if req_params and is_write:
            master_dataset.append({
                "test_id": f"op_{feat_id}_{op_id}_missing_params",
                "feature_id": feat_id,
                "operation_id": op_id,
                "operation_type": op_type,
                "query": f"Please proceed with {op_id.replace('_', ' ')} right now.",
                "expected_feature": feat_id,
                "expected_operation": op_type,
                "expected_intent": "ACTION_REQUEST",
                "required_parameters": req_params,
                "is_write_operation": is_write,
                "safe_execution_decision": "prompt_missing_params",
                "dimension": "missing_parameters"
            })

        # 6. Unauthorized / Admin Check (if admin feature)
        if is_admin:
            master_dataset.append({
                "test_id": f"op_{feat_id}_{op_id}_unauthorized_student",
                "feature_id": feat_id,
                "operation_id": op_id,
                "operation_type": op_type,
                "query": f"As a student, give me full access to {op_id.replace('_', ' ')}",
                "expected_feature": feat_id,
                "expected_operation": op_type,
                "expected_intent": "ACTION_REQUEST",
                "required_parameters": [],
                "is_write_operation": False,
                "safe_execution_decision": "reject_unsupported",
                "dimension": "unauthorized_user"
            })

    out_file = REPO_ROOT / "BACKEND" / "artifacts" / "independent_test_dataset.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(master_dataset, f, indent=2)
    print(f"Generated {len(master_dataset)} total independent test cases saved to {out_file}.")
    return master_dataset


if __name__ == "__main__":
    build_exhaustive_independent_dataset()
