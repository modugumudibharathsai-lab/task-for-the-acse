#!/usr/bin/env python3
"""
VIGBOT: Comprehensive Intent Model Evaluation Pipeline (ml/evaluate_intent.py)
Evaluates on the sequestered test author (sridhar) only.
Compares:
  (1) Trained TF-IDF + Logistic Regression Intent Classifier (full test set & 200 benchmark subset)
  (2) Rule-Based NLU baseline (rules only, with LLMClient.classify_intent disabled)
  (3) Gemini Zero-Shot baseline (fixed prompt, temp=0, on identical 200 subset)
Profiles measured latency (mean, p50, p95), ECE calibration, bootstrap 95% CIs,
paired comparisons, distress_support recall, and per-language metrics (>= 20 rows).
"""

import os
import sys
import re
import argparse
import json
import csv
import time
import math
import random
from collections import defaultdict, Counter
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add parent and backend directories to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(parent_dir, "BACKEND")
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.dataset_loader import (
    ALLOWED_AUTHORS,
    HUMAN_AUTHORS,
    TRAINING_AUTHORS,
    TEST_AUTHOR,
    ALLOWED_LANGS,
    SPECIAL_QUOTA_INTENTS,
    load_intents_schema,
    load_all_intent_data,
    load_crisis_test_data,
    check_dataset_quotas,
)


def run_rule_only_nlu(query: str) -> Optional[str]:
    """
    Simulates the repo's existing rule-based NLU heuristics from nlu_engine.py
    with LLMClient.classify_intent and ALL Gemini calls DISABLED.
    Maps to the team's 18 topics. Returns matched intent key or None if unmatched.
    """
    q_lower = query.strip().lower()

    # 1. Distress safety check
    distress_keywords = [
        "can't handle this", "cant handle this", "cannot handle this",
        "handle this anymore", "want to give up", "giving up", "feel hopeless",
        "break down", "breakdown", "suicide", "suicidal", "end my life",
        "kill myself", "hate my life", "panic attack", "no reason to live", "ending it all",
        "stress", "stressed", "burnout", "anxiety", "overwhelmed", "exhausted", "headache", "depressed"
    ]
    if any(k in q_lower for k in distress_keywords):
        return "distress_support"

    # 2. Greeting / Menu / Start
    if q_lower in ["start", "menu"] or any(k in q_lower for k in ["hi", "hello", "hey", "good morning", "good afternoon", "who are you", "helpdesk"]):
        return "greeting_smalltalk"

    # 3. Attendance
    if any(k in q_lower for k in ["attendance", "bunk", "classes held", "75%"]):
        return "attendance"

    # 4. Exams
    if any(k in q_lower for k in ["exam", "exams", "assessment", "cie", "formative", "summative", "mid"]):
        return "exams"

    # 5. Fees
    if any(k in q_lower for k in ["fee", "fees", "balance", "due", "tuition", "fine", "waive"]):
        return "fees"

    # 6. Timetable
    if any(k in q_lower for k in ["schedule", "timetable", "class today", "lecture slot", "room no"]):
        return "timetable"

    # 7. Marks
    if any(k in q_lower for k in ["marks", "cgpa", "sgpa", "grade", "score", "backlog", "backlogs"]):
        return "marks"

    # 8. Curriculum
    if any(k in q_lower for k in ["curriculum", "credit", "credits", "graduate", "graduation", "degree", "next semester"]):
        return "curriculum"

    # 9. Faculty
    if any(k in q_lower for k in ["class teacher", "counsellor", "counselor", "mentor", "advisor", "faculty", "professor"]):
        return "faculty"

    # 10. Library
    if any(k in q_lower for k in ["library", "book", "borrowed", "overdue", "issue"]):
        return "library"

    # 11. Hostel
    if any(k in q_lower for k in ["hostel", "room allotment", "warden", "curfew", "outpass", "mess food"]):
        return "hostel"

    # 12. Transport
    if any(k in q_lower for k in ["bus route", "bus timing", "shuttle", "bus pass", "commute", "transit", "transport"]):
        return "transport"

    # 13. Circulars
    if any(k in q_lower for k in ["circular", "circulars", "notification", "holiday", "holidays", "vacation", "announcement", "calendar"]):
        return "circulars"

    # 14. Events
    if any(k in q_lower for k in ["fest", "symposium", "hackathon", "sports meet", "annual day", "event", "events"]):
        return "events"

    # 15. Clubs
    if any(k in q_lower for k in ["club", "clubs", "extracurricular", "society", "societies"]):
        return "clubs"

    # 16. Services
    if any(k in q_lower for k in ["apply for", "certificate", "bonafide", "railway concession", "transit pass", "id card", "lost card", "lodge grievance", "file complaint", "grievance", "service", "services"]):
        return "services"

    # 17. Policy / Bylaws
    if any(k in q_lower for k in ["policy", "condonation", "regulation", "rule", "bylaw", "r23"]):
        return "policy_bylaws"

    # Rule-only fallback: Unmatched
    return None


def run_gemini_with_retry(
    query: str,
    valid_intents: List[str],
    api_key: str,
    model_id: str = "gemini-2.5-flash",
    max_retries: int = 3,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Calls Google Gemini zero-shot on query with temperature 0 and fixed prompt using exact model_id.
    Retries on API errors, rate limits, and timeouts with exponential backoff.
    Returns (predicted_intent, error_message).
    If all retries fail, returns (None, error_str). Never counts API errors as wrong answers!
    """
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        intent_list_str = ", ".join(valid_intents)
        prompt = (
            f"Classify the query into exactly ONE of the following 18 intents:\n"
            f"{intent_list_str}\n\n"
            f"Query: \"{query}\"\n\n"
            f"Respond with ONLY the exact intent key in lowercase, with no punctuation or additional words."
        )

        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=200,
                    ),
                )
                raw_text = ""
                if response and response.text:
                    raw_text = response.text.strip().lower()
                elif response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        p_text = getattr(part, 'text', None)
                        if p_text:
                            raw_text = p_text.strip().lower()
                            break
                clean_intent = re.sub(r"[^a-z_]", "", raw_text)
                if clean_intent in valid_intents:
                    return clean_intent, None
                for vi in valid_intents:
                    if vi in clean_intent:
                        return vi, None
                return None, f"Unrecognized intent from Gemini: '{raw_text}'"
            except Exception as ex:
                err_s = str(ex)
                if "404" in err_s or "NOT_FOUND" in err_s:
                    return None, f"Model unavailable (404 NOT_FOUND): {ex}"
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                else:
                    return None, f"Gemini API error after {max_retries} attempts: {ex}"
    except Exception as e:
        return None, f"Client setup error: {e}"

    return None, "Unknown failure"


def bootstrap_ci(
    targets: List[str],
    preds: List[str],
    n_resamples: int = 1000,
    random_state: int = 42,
) -> Dict[str, Tuple[float, float]]:
    """
    Computes 95% bootstrap confidence intervals for accuracy and macro-F1.
    """
    from sklearn.metrics import accuracy_score, f1_score
    import numpy as np

    rng = np.random.RandomState(random_state)
    n = len(targets)
    if n == 0:
        return {"accuracy": (0.0, 0.0), "macro_f1": (0.0, 0.0)}

    boot_accs = []
    boot_f1s = []

    for _ in range(n_resamples):
        indices = rng.choice(n, size=n, replace=True)
        sub_t = [targets[i] for i in indices]
        sub_p = [preds[i] for i in indices]
        boot_accs.append(accuracy_score(sub_t, sub_p))
        boot_f1s.append(f1_score(sub_t, sub_p, average="macro", zero_division=0))

    boot_accs.sort()
    boot_f1s.sort()

    low_idx = int(n_resamples * 0.025)
    high_idx = int(n_resamples * 0.975)

    return {
        "accuracy": (round(float(boot_accs[low_idx]), 4), round(float(boot_accs[high_idx]), 4)),
        "macro_f1": (round(float(boot_f1s[low_idx]), 4), round(float(boot_f1s[high_idx]), 4)),
    }


def compute_paired_comparison(
    targets: List[str],
    preds_a: List[str],
    preds_b: List[str],
    n_resamples: int = 1000,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Computes paired difference and 95% bootstrap CI between method A (classifier) and method B.
    Positive difference means method A outperforms method B.
    """
    from sklearn.metrics import accuracy_score, f1_score
    import numpy as np

    rng = np.random.RandomState(random_state)
    n = len(targets)
    if n == 0:
        return {"diff_acc": 0.0, "ci_acc": (0.0, 0.0), "diff_f1": 0.0, "ci_f1": (0.0, 0.0)}

    base_diff_acc = accuracy_score(targets, preds_a) - accuracy_score(targets, preds_b)
    base_diff_f1 = f1_score(targets, preds_a, average="macro", zero_division=0) - f1_score(targets, preds_b, average="macro", zero_division=0)

    diffs_acc = []
    diffs_f1 = []

    for _ in range(n_resamples):
        indices = rng.choice(n, size=n, replace=True)
        sub_t = [targets[i] for i in indices]
        sub_a = [preds_a[i] for i in indices]
        sub_b = [preds_b[i] for i in indices]
        d_acc = accuracy_score(sub_t, sub_a) - accuracy_score(sub_t, sub_b)
        d_f1 = f1_score(sub_t, sub_a, average="macro", zero_division=0) - f1_score(sub_t, sub_b, average="macro", zero_division=0)
        diffs_acc.append(d_acc)
        diffs_f1.append(d_f1)

    diffs_acc.sort()
    diffs_f1.sort()

    low_idx = int(n_resamples * 0.025)
    high_idx = int(n_resamples * 0.975)

    return {
        "diff_acc": round(float(base_diff_acc), 4),
        "ci_acc": (round(float(diffs_acc[low_idx]), 4), round(float(diffs_acc[high_idx]), 4)),
        "diff_f1": round(float(base_diff_f1), 4),
        "ci_f1": (round(float(diffs_f1[low_idx]), 4), round(float(diffs_f1[high_idx]), 4)),
    }


def compute_calibration_ece(
    confidences: List[float],
    predictions: List[str],
    ground_truth: List[str],
    n_bins: int = 10,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Computes Expected Calibration Error (ECE) and bin breakdown table.
    Outputs confidence scores with explicit small-test-set reliability notice.
    """
    bins = []
    bin_size = 1.0 / n_bins
    total_samples = len(confidences)
    if total_samples == 0:
        return 0.0, []

    ece = 0.0
    for i in range(n_bins):
        low = i * bin_size
        high = (i + 1) * bin_size
        indices = [
            idx for idx, c in enumerate(confidences)
            if (low <= c < high) or (i == n_bins - 1 and low <= c <= high)
        ]
        count = len(indices)
        if count == 0:
            bins.append({
                "bin": f"[{low:.1f}, {high:.1f}]",
                "count": 0,
                "avg_confidence": 0.0,
                "accuracy": 0.0,
                "gap": 0.0,
            })
            continue

        avg_conf = sum(confidences[idx] for idx in indices) / count
        correct = sum(1 for idx in indices if predictions[idx] == ground_truth[idx])
        acc = correct / count
        gap = abs(acc - avg_conf)
        ece += (count / total_samples) * gap

        bins.append({
            "bin": f"[{low:.1f}, {high:.1f}]",
            "count": count,
            "avg_confidence": round(avg_conf, 4),
            "accuracy": round(acc, 4),
            "gap": round(gap, 4),
        })

    return round(ece, 4), bins


def evaluate_intent_pipeline(
    data_dir: str = "data",
    yaml_path: str = "ml/intents.yaml",
    test_author: str = TEST_AUTHOR,
    artifacts_dir: str = "BACKEND/artifacts",
    model_path: Optional[str] = None,
    gemini_sample_size: int = 200,
    allow_partial: bool = False,
    crisis_test_path: Optional[str] = None,
) -> int:
    """
    Main evaluation pipeline.
    """
    import sklearn
    from sklearn.metrics import classification_report, f1_score, accuracy_score, recall_score
    import joblib

    test_author = test_author.strip().lower()

    # 1. Load intent schema
    intents_schema = load_intents_schema(yaml_path)
    valid_intents = sorted(list(intents_schema.keys()))

    # 2. Load dataset
    rows, load_errors = load_all_intent_data(data_dir, yaml_path)
    if load_errors:
        print("[FATAL ERROR] Dataset loading failed:")
        for err in load_errors:
            print(f"  ❌ {err}")
        return 1

    # 3. Quota Audit and Pipeline Mode Flagging
    quotas = check_dataset_quotas(rows, valid_intents=set(valid_intents), test_author=test_author)
    is_ready = quotas["is_ready"]

    if is_ready:
        mode = "PRODUCTION"
        file_prefix = ""
        print("\n" + "=" * 80)
        print("          FULL PRODUCTION EVALUATION (ALL HUMAN QUOTAS MET)")
        print("=" * 80 + "\n")
    elif allow_partial:
        mode = "PRELIMINARY"
        file_prefix = "preliminary_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PRELIMINARY EVALUATION (--allow-partial enabled)                      *")
        print("*         PRELIMINARY: incomplete data                                         *")
        print("*" + " " * 78 + "*")
        print("*" * 80)
        print("  ℹ️ Evaluating available data in preliminary mode.")
        print(f"  ℹ️ Output artifacts will be prefixed with '{file_prefix}'.")
        print("  ℹ️ Results will NEVER be written to results_intent.json / results_intent.csv.\n")
    else:
        mode = "PIPELINE_TEST"
        file_prefix = "pipeline_test_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PIPELINE TEST ONLY (human data incomplete)                           *")
        print("*" + " " * 78 + "*")
        print("*" * 80)
        print("  ℹ️ Human dataset is incomplete. Output files will be prefixed with 'pipeline_test_'.")
        print("  ℹ️ Results will NEVER be written to results_intent.json / results_intent.csv.\n")

    # 4. Filter test author rows strictly
    test_rows = [r for r in rows if r["author"] == test_author]

    # Handle pipeline test mode when sridhar rows are not yet populated
    dry_run_notice = None
    if not test_rows:
        if mode in ("PIPELINE_TEST", "PRELIMINARY"):
            print(f"[{mode} NOTICE] Test author '{test_author}' has 0 rows.")
            print("\n" + "!" * 80)
            print("!       EVALUATED ON TRAINING DATA (code dry run, not a performance measure)   !")
            print("!  Subset drawn from 68 stratified questions from 'agent' starter rows.        !")
            print("!  Since the model was trained on these rows, these metrics represent dry-run  !")
            print("!  execution verification, NOT true held-out test generalization.              !")
            print("!" * 80 + "\n")
            all_agent_rows = [r for r in rows if r["author"] == "agent"]
            from sklearn.model_selection import train_test_split
            _, test_rows = train_test_split(
                all_agent_rows,
                test_size=0.25,
                stratify=[r["intent"] for r in all_agent_rows],
                random_state=42
            )
            dry_run_notice = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure). Subset drawn from agent starter rows (data/intents.csv)."
        else:
            print(f"[FATAL ERROR] Test author '{test_author}' has 0 rows in production mode.")
            return 1

    print(f"Evaluating on Test Rows: {len(test_rows)} questions (Test Author: {test_author.upper() if not dry_run_notice else 'agent (starter holdout)'})")

    # Count rows per author and intent for preliminary metadata
    author_counts: Dict[str, int] = defaultdict(int)
    intent_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        author_counts[r["author"]] += 1
        intent_counts[r["intent"]] += 1

    # 5. Load Trained Model
    if model_path is None:
        model_name = f"{file_prefix}intent_model.joblib"
        possible_paths = [
            os.path.join(artifacts_dir, model_name),
            os.path.join(artifacts_dir, "intent_model.joblib"),
            os.path.join(artifacts_dir, "preliminary_intent_model.joblib"),
            os.path.join(artifacts_dir, "pipeline_test_intent_model.joblib"),
        ]
        model_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not model_path or not os.path.exists(model_path):
        print(f"[FATAL ERROR] Trained model artifact not found. Looked in: {possible_paths}")
        print("Run 'python ml/train_intent.py' first.")
        return 1

    print(f"Loading model artifact  : {os.path.abspath(model_path)}")
    model_size_kb = os.path.getsize(model_path) / 1024.0
    model = joblib.load(model_path)

    # 6. Profile Classifier Latency & Predictions on Full Test Set
    X_test_full = [r["text"] for r in test_rows]
    y_test_full = [r["intent"] for r in test_rows]

    # Warmup
    for q in X_test_full[:10]:
        _ = model.predict([q])

    latencies_ms = []
    y_pred_full = []
    y_conf_full = []

    for text in X_test_full:
        t0 = time.perf_counter()
        proba = model.predict_proba([text])[0]
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

        best_idx = proba.argmax()
        best_intent = model.classes_[best_idx]
        conf = float(proba[best_idx])
        y_pred_full.append(best_intent)
        y_conf_full.append(conf)

    # Latency statistics
    latencies_ms.sort()
    mean_lat = sum(latencies_ms) / len(latencies_ms)
    p50_lat = latencies_ms[int(len(latencies_ms) * 0.50)]
    p95_lat = latencies_ms[int(len(latencies_ms) * 0.95)]

    acc_full = accuracy_score(y_test_full, y_pred_full)
    f1_macro_full = f1_score(y_test_full, y_pred_full, average="macro", zero_division=0)
    ece, cal_bins = compute_calibration_ece(y_conf_full, y_pred_full, y_test_full)

    # Distress support recall on full test set
    distress_full_targets = [1 if t == "distress_support" else 0 for t in y_test_full]
    distress_full_preds = [1 if p == "distress_support" else 0 for p in y_pred_full]
    distress_full_recall = recall_score(distress_full_targets, distress_full_preds, zero_division=0)

    # 7. Create Identical Benchmark Sample (up to 200 rows, stratified by intent)
    sample_size = min(gemini_sample_size, len(test_rows))
    if sample_size < len(test_rows):
        from sklearn.model_selection import StratifiedShuffleSplit
        sss = StratifiedShuffleSplit(n_splits=1, train_size=sample_size, random_state=42)
        bench_indices, _ = next(sss.split(X_test_full, y_test_full))
        bench_rows = [test_rows[i] for i in sorted(bench_indices)]
    else:
        bench_rows = test_rows

    print(f"\nCreated Identical Benchmark Subset: {len(bench_rows)} questions (Stratified by intent, random_state=42)")

    X_bench = [r["text"] for r in bench_rows]
    y_bench = [r["intent"] for r in bench_rows]

    # (A) Classifier on Benchmark Subset
    bench_indices_map = [test_rows.index(r) for r in bench_rows]
    y_clf_bench = [y_pred_full[i] for i in bench_indices_map]
    acc_clf_bench = accuracy_score(y_bench, y_clf_bench)
    f1_clf_bench = f1_score(y_bench, y_clf_bench, average="macro", zero_division=0)

    clf_ci = bootstrap_ci(y_bench, y_clf_bench, n_resamples=1000, random_state=42)

    # Distress support recall for classifier on benchmark
    distress_b_targets = [1 if t == "distress_support" else 0 for t in y_bench]
    distress_clf_preds = [1 if p == "distress_support" else 0 for p in y_clf_bench]
    distress_clf_recall = recall_score(distress_b_targets, distress_clf_preds, zero_division=0)

    # (B) Rule-Based Baseline (Rules ONLY) on Benchmark Subset
    y_rules_bench = []
    rules_matched_count = 0
    rules_latencies_ms = []

    for q in X_bench:
        t0 = time.perf_counter()
        matched = run_rule_only_nlu(q)
        t1 = time.perf_counter()
        rules_latencies_ms.append((t1 - t0) * 1000.0)

        if matched is not None:
            rules_matched_count += 1
            y_rules_bench.append(matched)
        else:
            y_rules_bench.append("unmatched")  # Counted as wrong

    rules_coverage = rules_matched_count / len(X_bench)
    acc_rules_bench = accuracy_score(y_bench, y_rules_bench)
    f1_rules_bench = f1_score(y_bench, y_rules_bench, average="macro", zero_division=0)
    rules_ci = bootstrap_ci(y_bench, y_rules_bench, n_resamples=1000, random_state=42)

    rules_latencies_ms.sort()
    mean_rules_lat = sum(rules_latencies_ms) / len(rules_latencies_ms)
    p50_rules_lat = rules_latencies_ms[int(len(rules_latencies_ms) * 0.50)]
    p95_rules_lat = rules_latencies_ms[int(len(rules_latencies_ms) * 0.95)]

    distress_rules_preds = [1 if p == "distress_support" else 0 for p in y_rules_bench]
    distress_rules_recall = recall_score(distress_b_targets, distress_rules_preds, zero_division=0)

    # (C) Google Gemini Zero-Shot Baseline on Benchmark Subset
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    try:
        from app.config import settings
        gemini_model_id = str(settings.GEMINI_MODEL)
        if not gemini_api_key:
            gemini_api_key = str(settings.GEMINI_API_KEY or "").strip()
    except Exception:
        gemini_model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    y_gemini_bench = []
    gemini_latencies_ms = []
    failed_gemini_calls = 0
    gemini_evaluated = False
    valid_pairs = []
    gemini_eval_date = datetime.now(timezone.utc).isoformat()
    gemini_failure_reason = None

    if gemini_api_key:
        print(f"\nRunning Google Gemini Zero-Shot Baseline:")
        print(f"  • Model ID     : {gemini_model_id} (read from app config)")
        print(f"  • Evaluation Date: {gemini_eval_date}")
        print(f"  • Sample Size  : {len(X_bench)} questions (drawn strictly from dataset)")
        for q_idx, q in enumerate(X_bench):
            t0 = time.perf_counter()
            pred, err = run_gemini_with_retry(q, valid_intents, gemini_api_key, model_id=gemini_model_id)
            t1 = time.perf_counter()
            gemini_latencies_ms.append((t1 - t0) * 1000.0)

            if (q_idx + 1) % 10 == 0 or q_idx == 0 or q_idx == len(X_bench) - 1:
                print(f"  [Gemini Progress] Evaluated {q_idx + 1}/{len(X_bench)} questions (latest: {pred or err})...", flush=True)

            if err:
                failed_gemini_calls += 1
                gemini_failure_reason = err
                y_gemini_bench.append(None)
                print(f"  [GEMINI API ERROR] Question {q_idx+1} failed with model '{gemini_model_id}': {err}")
                if "404" in str(err) or "NOT_FOUND" in str(err):
                    print(f"  [NOTICE] Model '{gemini_model_id}' is unavailable (404). Aborting remaining calls to save time.")
                    for _ in range(q_idx + 1, len(X_bench)):
                        y_gemini_bench.append(None)
                        failed_gemini_calls += 1
                    break
            else:
                y_gemini_bench.append(pred)

        # Exclude API errors: evaluate only valid calls; NEVER count API errors as wrong answers!
        valid_pairs = [(y_bench[i], y_gemini_bench[i]) for i in range(len(y_bench)) if y_gemini_bench[i] is not None]
        if valid_pairs:
            y_bench_gemini_valid = [p[0] for p in valid_pairs]
            y_gemini_valid = [p[1] for p in valid_pairs]
            acc_gemini_bench = accuracy_score(y_bench_gemini_valid, y_gemini_valid)
            f1_gemini_bench = f1_score(y_bench_gemini_valid, y_gemini_valid, average="macro", zero_division=0)
            gemini_ci = bootstrap_ci(y_bench_gemini_valid, y_gemini_valid, n_resamples=1000, random_state=42)
            gemini_latencies_ms.sort()
            mean_gemini_lat = sum(gemini_latencies_ms) / len(gemini_latencies_ms)
            p50_gemini_lat = gemini_latencies_ms[int(len(gemini_latencies_ms) * 0.50)]
            p95_gemini_lat = gemini_latencies_ms[int(len(gemini_latencies_ms) * 0.95)]
            dist_gem_targets = [1 if t == "distress_support" else 0 for t in y_bench_gemini_valid]
            dist_gem_preds = [1 if p == "distress_support" else 0 for p in y_gemini_valid]
            distress_gemini_recall = recall_score(dist_gem_targets, dist_gem_preds, zero_division=0)
            gemini_evaluated = True
        else:
            print(f"[FATAL ERROR] Model '{gemini_model_id}' failed all calls. Not substituting any other model.")
            acc_gemini_bench = 0.0
            f1_gemini_bench = 0.0
            gemini_ci = {"accuracy": (0.0, 0.0), "macro_f1": (0.0, 0.0)}
            mean_gemini_lat = p50_gemini_lat = p95_gemini_lat = 0.0
            distress_gemini_recall = 0.0
    else:
        print(f"\n[INFO] GEMINI_API_KEY not set. Gemini zero-shot baseline (Model: '{gemini_model_id}') skipped in offline test.")
        acc_gemini_bench = None
        f1_gemini_bench = None
        gemini_ci = None
        mean_gemini_lat = p50_gemini_lat = p95_gemini_lat = None
        distress_gemini_recall = None

    # (D) Paired Comparison (Classifier vs Rules on same questions)
    paired_clf_rules = compute_paired_comparison(y_bench, y_clf_bench, y_rules_bench)
    paired_clf_gemini = None
    if gemini_evaluated:
        # Paired on valid calls
        valid_indices = [i for i in range(len(y_bench)) if y_gemini_bench[i] is not None]
        paired_clf_gemini = compute_paired_comparison(
            [y_bench[i] for i in valid_indices],
            [y_clf_bench[i] for i in valid_indices],
            [y_gemini_bench[i] for i in valid_indices],
        )

    # 8. Per-Language Breakdown (ONLY where test author has >= 20 rows)
    lang_breakdown = {}
    lang_groups = defaultdict(list)
    for idx, r in enumerate(test_rows):
        lang_groups[r["lang"]].append(idx)

    print("\n" + "=" * 80)
    print("      PER-LANGUAGE ACCURACY REPORT (Reported only for languages with >= 20 rows)")
    print("=" * 80)
    for lang, idxs in sorted(lang_groups.items()):
        cnt = len(idxs)
        if cnt >= 20:
            l_targets = [y_test_full[i] for i in idxs]
            l_preds = [y_pred_full[i] for i in idxs]
            l_acc = accuracy_score(l_targets, l_preds)
            l_f1 = f1_score(l_targets, l_preds, average="macro", zero_division=0)
            lang_breakdown[lang] = {
                "count": cnt,
                "accuracy": round(float(l_acc), 4),
                "macro_f1": round(float(l_f1), 4),
                "status": "VALID_SAMPLE",
            }
            print(f"  • {lang:<10}: Accuracy = {l_acc:.4f} ({l_acc * 100:.1f}%), Macro-F1 = {l_f1:.4f} ({cnt} rows)")
        else:
            lang_breakdown[lang] = {
                "count": cnt,
                "status": "SPARSE_EXCLUDED (< 20 rows; skipped from official report)",
            }
            print(f"  • {lang:<10}: {cnt} rows [SPARSE (<20 rows; skipped from official language breakdown)]")

    # 9. Print Comparative Benchmark Table
    print("\n" + "=" * 80)
    print(f"       COMPARATIVE BENCHMARK TABLE (IDENTICAL SUBSET: {len(bench_rows)} QUESTIONS)")
    print("=" * 80)
    print(f"{'Method':<26} | {'Accuracy (95% CI)':<22} | {'Macro-F1 (95% CI)':<22} | {'Distress Recall':<15} | {'Coverage':<9} | {'Mean Latency':<12}")
    print("-" * 117)

    clf_label = f"Trained Classifier ({len(bench_rows)})"
    clf_acc_str = f"{acc_clf_bench:.4f} [{clf_ci['accuracy'][0]:.2f}, {clf_ci['accuracy'][1]:.2f}]"
    clf_f1_str = f"{f1_clf_bench:.4f} [{clf_ci['macro_f1'][0]:.2f}, {clf_ci['macro_f1'][1]:.2f}]"
    print(f"{clf_label:<26} | {clf_acc_str:<22} | {clf_f1_str:<22} | {distress_clf_recall:<15.4f} | {'100.0%':<9} | {mean_lat:.2f} ms")

    rules_acc_str = f"{acc_rules_bench:.4f} [{rules_ci['accuracy'][0]:.2f}, {rules_ci['accuracy'][1]:.2f}]"
    rules_f1_str = f"{f1_rules_bench:.4f} [{rules_ci['macro_f1'][0]:.2f}, {rules_ci['macro_f1'][1]:.2f}]"
    print(f"{'Rule-Based Only (No LLM)':<26} | {rules_acc_str:<22} | {rules_f1_str:<22} | {distress_rules_recall:<15.4f} | {rules_coverage * 100:.1f}%     | {mean_rules_lat:.2f} ms")

    if gemini_evaluated:
        gem_acc_str = f"{acc_gemini_bench:.4f} [{gemini_ci['accuracy'][0]:.2f}, {gemini_ci['accuracy'][1]:.2f}]"
        gem_f1_str = f"{f1_gemini_bench:.4f} [{gemini_ci['macro_f1'][0]:.2f}, {gemini_ci['macro_f1'][1]:.2f}]"
        gem_name = f"Gemini ({gemini_model_id})"
        print(f"{gem_name:<26} | {gem_acc_str:<22} | {gem_f1_str:<22} | {distress_gemini_recall:<15.4f} | {'100.0%':<9} | {mean_gemini_lat:.2f} ms")
    else:
        gem_name = f"Gemini ({gemini_model_id})"
        print(f"{gem_name:<26} | {'N/A (No API Key)':<22} | {'N/A':<22} | {'N/A':<15} | {'N/A':<9} | {'N/A':<12}")

    print("-" * 117)
    print(f"{'Classifier (Full Test Set)':<26} | {acc_full:.4f}                 | {f1_macro_full:.4f}                 | {distress_full_recall:<15.4f} | {'100.0%':<9} | {mean_lat:.2f} ms")

    # 10. Paired Comparison Report
    print("\n" + "-" * 80)
    print("       PAIRED METHOD COMPARISONS (ON IDENTICAL SUBSET QUESTIONS)")
    print("-" * 80)
    print(f"Classifier vs Rules: Delta Accuracy = {paired_clf_rules['diff_acc']:+.4f} (95% CI: [{paired_clf_rules['ci_acc'][0]:+.2f}, {paired_clf_rules['ci_acc'][1]:+.2f}])")
    print(f"                     Delta Macro-F1 = {paired_clf_rules['diff_f1']:+.4f} (95% CI: [{paired_clf_rules['ci_f1'][0]:+.2f}, {paired_clf_rules['ci_f1'][1]:+.2f}])")
    if paired_clf_gemini:
        print(f"Classifier vs Gemini: Delta Accuracy = {paired_clf_gemini['diff_acc']:+.4f} (95% CI: [{paired_clf_gemini['ci_acc'][0]:+.2f}, {paired_clf_gemini['ci_acc'][1]:+.2f}])")
        print(f"                      Delta Macro-F1 = {paired_clf_gemini['diff_f1']:+.4f} (95% CI: [{paired_clf_gemini['ci_f1'][0]:+.2f}, {paired_clf_gemini['ci_f1'][1]:+.2f}])")

    # 11. Measured Latency Summary
    print("\n" + "-" * 80)
    print("                 MEASURED INFERENCE LATENCY (CONFIDENCE SCORES)")
    print("-" * 80)
    print(f"Trained Classifier Latency : Mean = {mean_lat:.2f} ms | p50 = {p50_lat:.2f} ms | p95 = {p95_lat:.2f} ms")
    print(f"Rule-Based Heuristic Latency: Mean = {mean_rules_lat:.2f} ms | p50 = {p50_rules_lat:.2f} ms | p95 = {p95_rules_lat:.2f} ms")
    if gemini_evaluated:
        print(f"Gemini API Latency          : Mean = {mean_gemini_lat:.2f} ms | p50 = {p50_gemini_lat:.2f} ms | p95 = {p95_gemini_lat:.2f} ms")

    # 12. Reliability & Calibration Summary
    print("\n" + "-" * 80)
    print("             RELIABILITY TABLE (CONFIDENCE CALIBRATION)")
    print("   Note: Test set is small; probabilities are uncalibrated confidence scores.")
    print("-" * 80)
    print(f"Expected Calibration Error (ECE): {ece:.4f}")
    print(f"{'Confidence Bin':<16} | {'Sample Count':<12} | {'Avg Confidence':<15} | {'Accuracy':<10} | {'Gap'}")
    print("-" * 70)
    for b in cal_bins:
        if b["count"] > 0:
            print(f"{b['bin']:<16} | {b['count']:<12} | {b['avg_confidence']:<15.4f} | {b['accuracy']:<10.4f} | {b['gap']:.4f}")

    # 13. Optional Crisis Test Evaluation (data/crisis_test.csv)
    crisis_file = crisis_test_path or os.path.join(data_dir, "crisis_test.csv")
    crisis_eval_data = None
    if os.path.exists(crisis_file):
        c_rows, c_errs = load_crisis_test_data(crisis_file)
        if c_errs:
            print(f"\n[WARNING] Found crisis test file {crisis_file} but encountered errors:")
            for err in c_errs:
                print(f"  - {err}")
        elif c_rows:
            print("\n" + "=" * 80)
            print(f"    CRISIS TEST RECALL EVALUATION ({len(c_rows)} phrases from {crisis_file})")
            print("=" * 80)
            try:
                from app.tools.distress_tool import detect_distress
            except ImportError:
                detect_distress = None

            kw_hits = 0
            if detect_distress:
                kw_hits = sum(1 for r in c_rows if detect_distress(r["text"]))
            kw_recall = kw_hits / len(c_rows) if c_rows else 0.0

            clf_hits = 0
            if model is not None:
                clf_preds = model.predict([r["text"] for r in c_rows])
                clf_hits = sum(1 for p in clf_preds if p == "distress_support")
            clf_recall = clf_hits / len(c_rows) if c_rows else 0.0

            print(f"  Total crisis test phrases      : {len(c_rows)}")
            if detect_distress:
                print(f"  Keyword Safety Guardrail Recall: {kw_hits}/{len(c_rows)} ({kw_recall * 100:.2f}%)")
            if model is not None:
                print(f"  Classifier distress_support    : {clf_hits}/{len(c_rows)} ({clf_recall * 100:.2f}%)")
            print("=" * 80)

            crisis_eval_data = {
                "file": crisis_file,
                "total_phrases": len(c_rows),
                "keyword_guardrail_recall": round(float(kw_recall), 4) if detect_distress else None,
                "keyword_guardrail_hits": kw_hits,
                "classifier_distress_recall": round(float(clf_recall), 4) if model is not None else None,
                "classifier_distress_hits": clf_hits,
            }

    # 14. Save Output Artifacts to BACKEND/artifacts/
    # NEVER write results_intent.json or results_intent.csv unless full production mode
    out_json_filename = f"{file_prefix}results_intent.json" if file_prefix else "results_intent.json"
    out_csv_filename = f"{file_prefix}results_intent.csv" if file_prefix else "results_intent.csv"

    # Prepend preliminary warning line if preliminary or pipeline test
    warning_line = None
    if mode == "PRELIMINARY":
        warning_line = "PRELIMINARY: incomplete data"
    elif mode == "PIPELINE_TEST":
        warning_line = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"

    dry_run_flag = (mode == "PIPELINE_TEST" or dry_run_notice is not None)
    dry_run_text = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)" if dry_run_flag else None
    dry_run_explanation = (
        f"In pipeline-test mode, sridhar has 0 rows. The {len(bench_rows)}-question subset was drawn from "
        f"stratified questions from 'agent' starter rows (data/intents.csv). Because the model was trained on these starter rows, "
        f"these metrics represent code dry-run verification, NOT a true measure of generalization."
    ) if dry_run_flag else None

    results_data: Dict[str, Any] = {
        "status": mode,
        "warning": warning_line,
        "dry_run_honesty": dry_run_text,
        "dry_run_explanation": dry_run_explanation,
        "preliminary_notice": "PRELIMINARY: incomplete data" if mode == "PRELIMINARY" else None,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_audit": {
            "test_author": test_author,
            "test_author_true_rows": len([r for r in rows if r["author"] == test_author]),
            "evaluated_test_rows": len(test_rows),
            "benchmark_subset_size": len(bench_rows),
            "subset_source": f"{len(bench_rows)} stratified questions from 'agent' starter rows (data/intents.csv) [TRAINING DATA]" if dry_run_flag else f"held-out questions from test author {test_author}",
            "row_counts_by_author": dict(author_counts),
            "row_counts_by_intent": dict(intent_counts),
        },
        "model_file": os.path.basename(model_path),
        "benchmark_comparison": {
            "classifier_bench": {
                "subset_size": len(bench_rows),
                "accuracy": round(float(acc_clf_bench), 4),
                "accuracy_ci_95": clf_ci["accuracy"],
                "macro_f1": round(float(f1_clf_bench), 4),
                "macro_f1_ci_95": clf_ci["macro_f1"],
                "distress_support_recall": round(float(distress_clf_recall), 4),
                "coverage": 1.0,
                "latency_ms": {
                    "mean": round(float(mean_lat), 2),
                    "p50": round(float(p50_lat), 2),
                    "p95": round(float(p95_lat), 2),
                }
            },
            "rules_only": {
                "subset_size": len(bench_rows),
                "accuracy": round(float(acc_rules_bench), 4),
                "accuracy_ci_95": rules_ci["accuracy"],
                "macro_f1": round(float(f1_rules_bench), 4),
                "macro_f1_ci_95": rules_ci["macro_f1"],
                "distress_support_recall": round(float(distress_rules_recall), 4),
                "coverage": round(float(rules_coverage), 4),
                "unmatched_count": len(X_bench) - rules_matched_count,
                "latency_ms": {
                    "mean": round(float(mean_rules_lat), 2),
                    "p50": round(float(p50_rules_lat), 2),
                    "p95": round(float(p95_rules_lat), 2),
                }
            },
            "gemini_zero_shot": {
                "model_id": gemini_model_id,
                "evaluation_date_utc": gemini_eval_date,
                "sample_size": len(bench_rows),
                "status": "COMPLETED" if gemini_evaluated else ("SKIPPED (no GEMINI_API_KEY)" if not gemini_api_key else "FAILED"),
                "failure_reason": gemini_failure_reason,
                "evaluated": gemini_evaluated,
                "failed_api_calls": failed_gemini_calls,
                "accuracy": round(float(acc_gemini_bench), 4) if gemini_evaluated else None,
                "accuracy_ci_95": gemini_ci["accuracy"] if gemini_evaluated else None,
                "macro_f1": round(float(f1_gemini_bench), 4) if gemini_evaluated else None,
                "macro_f1_ci_95": gemini_ci["macro_f1"] if gemini_evaluated else None,
                "distress_support_recall": round(float(distress_gemini_recall), 4) if gemini_evaluated else None,
                "latency_ms": {
                    "mean": round(float(mean_gemini_lat), 2) if gemini_evaluated else None,
                    "p50": round(float(p50_gemini_lat), 2) if gemini_evaluated else None,
                    "p95": round(float(p95_gemini_lat), 2) if gemini_evaluated else None,
                }
            },
            "paired_comparison": {
                "classifier_vs_rules": paired_clf_rules,
                "classifier_vs_gemini": paired_clf_gemini,
            }
        },
        "classifier_full_test_set": {
            "accuracy": round(float(acc_full), 4),
            "macro_f1": round(float(f1_macro_full), 4),
            "distress_support_recall": round(float(distress_full_recall), 4),
            "ece_calibration_error": ece,
            "reliability_note": "Note: Test set is small; probabilities are uncalibrated confidence scores.",
            "calibration_bins": cal_bins,
        },
        "per_language_metrics": lang_breakdown,
        "crisis_test_evaluation": crisis_eval_data,
    }

    primary_json_path = os.path.join(artifacts_dir, out_json_filename)
    with open(primary_json_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved evaluation metrics JSON: {os.path.abspath(primary_json_path)}")

    # Write CSV summary
    primary_csv_path = os.path.join(artifacts_dir, out_csv_filename)
    with open(primary_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if dry_run_flag:
            writer.writerow(["# EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"])
            writer.writerow([f"# Exactly {len(bench_rows)} questions drawn from agent starter rows (data/intents.csv); sridhar has 0 rows"])
        elif mode == "PRELIMINARY":
            writer.writerow(["# PRELIMINARY: incomplete data"])
        writer.writerow(["method", "accuracy", "macro_f1", "distress_recall", "coverage", "mean_latency_ms", "p50_latency_ms", "p95_latency_ms"])
        writer.writerow([f"classifier_benchmark_{len(bench_rows)}", f"{acc_clf_bench:.4f}", f"{f1_clf_bench:.4f}", f"{distress_clf_recall:.4f}", "1.0000", f"{mean_lat:.2f}", f"{p50_lat:.2f}", f"{p95_lat:.2f}"])
        writer.writerow(["rule_based_only", f"{acc_rules_bench:.4f}", f"{f1_rules_bench:.4f}", f"{distress_rules_recall:.4f}", f"{rules_coverage:.4f}", f"{mean_rules_lat:.2f}", f"{p50_rules_lat:.2f}", f"{p95_rules_lat:.2f}"])
        if gemini_evaluated:
            writer.writerow([f"gemini_zero_shot_{gemini_model_id}", f"{acc_gemini_bench:.4f}", f"{f1_gemini_bench:.4f}", f"{distress_gemini_recall:.4f}", "1.0000", f"{mean_gemini_lat:.2f}", f"{p50_gemini_lat:.2f}", f"{p95_gemini_lat:.2f}"])
        writer.writerow(["classifier_full_test_set", f"{acc_full:.4f}", f"{f1_macro_full:.4f}", f"{distress_full_recall:.4f}", "1.0000", f"{mean_lat:.2f}", f"{p50_lat:.2f}", f"{p95_lat:.2f}"])
    print(f"Saved evaluation metrics CSV : {os.path.abspath(primary_csv_path)}")

    # Write Misclassified Questions CSV
    out_misclassified_filename = f"{file_prefix}misclassified.csv" if file_prefix else "misclassified.csv"
    misclassified_path = os.path.join(artifacts_dir, out_misclassified_filename)
    with open(misclassified_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if mode == "PRELIMINARY":
            writer.writerow(["# PRELIMINARY: incomplete data"])
            writer.writerow([f"# Row counts - test evaluated: {len(test_rows)} questions (author: {test_author})"])
        writer.writerow(["text", "true_intent", "predicted_intent", "confidence", "language"])
        for idx in range(len(test_rows)):
            if y_pred_full[idx] != y_test_full[idx]:
                writer.writerow([
                    test_rows[idx]["text"],
                    y_test_full[idx],
                    y_pred_full[idx],
                    f"{y_conf_full[idx]:.4f}",
                    test_rows[idx].get("lang", "en"),
                ])
    print(f"Saved misclassified queries  : {os.path.abspath(misclassified_path)}")

    # Generate Confusion Matrix PNG
    out_cm_filename = f"{file_prefix}confusion_matrix.png" if file_prefix else "confusion_matrix.png"
    cm_path = os.path.join(artifacts_dir, out_cm_filename)
    try:
        from sklearn.metrics import confusion_matrix
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        cm = confusion_matrix(y_test_full, y_pred_full, labels=valid_intents)
        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        ax.set(
            xticks=np.arange(cm.shape[1]),
            yticks=np.arange(cm.shape[0]),
            xticklabels=valid_intents,
            yticklabels=valid_intents,
            xlabel="Predicted Intent",
            ylabel="True Intent"
        )
        title_prefix = f"[{mode}] " if mode != "PRODUCTION" else ""
        ax.set_title(f"{title_prefix}VIGBOT Intent Confusion Matrix ({len(test_rows)} Test Samples)", fontsize=13, fontweight="bold")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=9)
        plt.setp(ax.get_yticklabels(), fontsize=9)

        thresh = cm.max() / 2. if cm.max() > 0 else 1
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                val = cm[i, j]
                if val > 0:
                    ax.text(j, i, format(val, "d"),
                            ha="center", va="center",
                            color="white" if val > thresh else "black",
                            fontsize=8)
        fig.tight_layout()
        fig.savefig(cm_path, dpi=150)
        plt.close(fig)
        print(f"Saved confusion matrix plot : {os.path.abspath(cm_path)}")
    except Exception as e:
        print(f"[WARNING] Could not generate confusion matrix plot: {e}")

    print("\n" + "=" * 80)
    print(f"        EVALUATION COMPLETED SUCCESSFULLY ({mode} MODE)")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Evaluate VIGBOT intent classifier.")
    parser.add_argument("--data-dir", default="data", help="Directory containing dataset files")
    parser.add_argument("--yaml-path", default="ml/intents.yaml", help="Path to ml/intents.yaml")
    parser.add_argument("--test-author", default=TEST_AUTHOR, help="Author strictly reserved for testing")
    parser.add_argument("--artifacts-dir", default="BACKEND/artifacts", help="Output directory for model artifacts")
    parser.add_argument("--model-path", default=None, help="Path to trained model joblib file")
    parser.add_argument("--gemini-samples", type=int, default=200, help="Benchmark subset size (default: 200)")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Run evaluation in preliminary mode on whatever rows exist, prefixing files with preliminary_",
    )
    parser.add_argument(
        "--crisis-test",
        default=None,
        help="Optional path to crisis test CSV file (text,lang) to report crisis-phrase recall",
    )
    args = parser.parse_args()

    exit_code = evaluate_intent_pipeline(
        data_dir=args.data_dir,
        yaml_path=args.yaml_path,
        test_author=args.test_author,
        artifacts_dir=args.artifacts_dir,
        model_path=args.model_path,
        gemini_sample_size=args.gemini_samples,
        allow_partial=args.allow_partial,
        crisis_test_path=args.crisis_test,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
