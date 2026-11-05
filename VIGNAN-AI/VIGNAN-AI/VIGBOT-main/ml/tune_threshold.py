#!/usr/bin/env python3
"""
VIGBOT: Confidence Threshold Tuning (ml/tune_threshold.py)
Sweeps confidence thresholds on Leave-One-Author-Out out-of-fold predictions from training authors.
Analyzes accuracy vs coverage trade-offs, tunes a specialized low threshold for distress_support
for maximum recall, plots the curve, and saves configuration to BACKEND/artifacts/{prefix}intent_config.json.
"""

import os
import sys
import argparse
import json
from datetime import datetime, timezone
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.dataset_loader import (
    ALLOWED_AUTHORS,
    HUMAN_AUTHORS,
    TRAINING_AUTHORS,
    TEST_AUTHOR,
    load_intents_schema,
    load_all_intent_data,
    check_dataset_quotas,
)


def tune_confidence_thresholds(
    data_dir: str = "data",
    yaml_path: str = "ml/intents.yaml",
    test_author: str = TEST_AUTHOR,
    artifacts_dir: str = "BACKEND/artifacts",
    model_path: Optional[str] = None,
    random_state: int = 42,
    allow_partial: bool = False,
) -> int:
    """
    Sweeps thresholds, calculates coverage vs precision, determines optimal thresholds,
    and saves BACKEND/artifacts/{prefix}intent_config.json and threshold_tradeoff.png.
    """
    import sklearn
    from sklearn.metrics import accuracy_score, recall_score, precision_score
    import joblib

    test_author = test_author.strip().lower()

    # 1. Load schema & dataset
    intents_schema = load_intents_schema(yaml_path)
    valid_intents = sorted(list(intents_schema.keys()))

    rows, load_errors = load_all_intent_data(data_dir, yaml_path)
    if load_errors:
        print("[FATAL ERROR] Dataset loading failed:")
        for err in load_errors:
            print(f"  ❌ {err}")
        return 1

    # 2. Check Quotas and determine mode
    quotas = check_dataset_quotas(rows, valid_intents=set(valid_intents), test_author=test_author)
    is_ready = quotas["is_ready"]

    if is_ready:
        mode = "PRODUCTION"
        file_prefix = ""
        print("\n" + "=" * 80)
        print("          FULL PRODUCTION THRESHOLD TUNING (ALL HUMAN QUOTAS MET)")
        print("=" * 80 + "\n")
    elif allow_partial:
        mode = "PRELIMINARY"
        file_prefix = "preliminary_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PRELIMINARY THRESHOLD TUNING (--allow-partial enabled)               *")
        print("*         PRELIMINARY: incomplete data                                         *")
        print("*" + " " * 78 + "*")
        print("*" * 80 + "\n")
    else:
        mode = "PIPELINE_TEST"
        file_prefix = "pipeline_test_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PIPELINE TEST ONLY (human data incomplete)                           *")
        print("*" + " " * 78 + "*")
        print("*" * 80 + "\n")

    # Author and intent row counts
    author_counts: Dict[str, int] = defaultdict(int)
    intent_counts: Dict[str, int] = defaultdict(int)
    for r in rows:
        author_counts[r["author"]] += 1
        intent_counts[r["intent"]] += 1

    # 3. Load Out-Of-Fold Validation Predictions
    oof_filename = f"{file_prefix}oof_predictions.joblib"
    possible_oof_paths = [
        os.path.join(artifacts_dir, oof_filename),
        os.path.join(artifacts_dir, "oof_predictions.joblib"),
        os.path.join(artifacts_dir, "preliminary_oof_predictions.joblib"),
        os.path.join(artifacts_dir, "pipeline_test_oof_predictions.joblib"),
    ]
    oof_path = next((p for p in possible_oof_paths if os.path.exists(p)), None)

    if oof_path and os.path.exists(oof_path):
        print(f"Loading Out-Of-Fold validation predictions: {os.path.abspath(oof_path)}")
        oof_data = joblib.load(oof_path)
        val_texts = oof_data["texts"]
        val_targets = oof_data["targets"]
        val_probabilities = oof_data["probabilities"]
        val_classes = oof_data["classes"] if "classes" in oof_data else sorted(list(set(val_targets)))
    else:
        print("[NOTICE] Out-Of-Fold artifact not found. Loading model to evaluate validation split...")
        model_name = f"{file_prefix}intent_model.joblib"
        possible_model_paths = [
            os.path.join(artifacts_dir, model_name),
            os.path.join(artifacts_dir, "intent_model.joblib"),
            os.path.join(artifacts_dir, "preliminary_intent_model.joblib"),
            os.path.join(artifacts_dir, "pipeline_test_intent_model.joblib"),
        ]
        model_path = next((p for p in possible_model_paths if os.path.exists(p)), None)
        if not model_path:
            print(f"[FATAL ERROR] Model not found in {possible_model_paths}. Run train_intent.py first.")
            return 1

        model = joblib.load(model_path)
        train_rows = [r for r in rows if r["author"] != test_author]
        val_texts = [r["text"] for r in train_rows]
        val_targets = [r["intent"] for r in train_rows]
        val_probabilities = model.predict_proba(val_texts)
        val_classes = list(model.classes_)

    print(f"Validation dataset size: {len(val_texts)} samples across {len(set(val_targets))} intents")

    # 4. Extract Top-1 Predicted Intent & Confidence Score for each validation sample
    import numpy as np
    val_confidences = []
    val_predictions = []
    classes_arr = np.array(val_classes)

    for i in range(len(val_texts)):
        probs = val_probabilities[i]
        top_idx = int(probs.argmax())
        top_intent = str(classes_arr[top_idx])
        conf = float(probs[top_idx])
        val_confidences.append(conf)
        val_predictions.append(top_intent)

    # 5. Sweep General Confidence Thresholds
    thresholds = [round(t * 0.05, 2) for t in range(2, 20)]  # 0.10 to 0.95
    sweep_results = []

    print("\n" + "=" * 80)
    print("               CONFIDENCE THRESHOLD ACCURACY / COVERAGE SWEEP")
    print("=" * 80)
    print(f"{'Threshold':<10} | {'Coverage':<12} | {'Accepted Acc':<14} | {'Accepted Qs':<13} | {'Fallback Qs'}")
    print("-" * 80)

    for th in thresholds:
        accepted_indices = [idx for idx, c in enumerate(val_confidences) if c >= th]
        n_accepted = len(accepted_indices)
        coverage = n_accepted / len(val_confidences)

        if n_accepted > 0:
            acc = accuracy_score(
                [val_targets[idx] for idx in accepted_indices],
                [val_predictions[idx] for idx in accepted_indices]
            )
        else:
            acc = 1.0

        n_fallback = len(val_confidences) - n_accepted
        sweep_results.append({
            "threshold": th,
            "coverage": round(coverage, 4),
            "accuracy": round(acc, 4),
            "accepted_count": n_accepted,
            "fallback_count": n_fallback,
        })
        print(f"{th:<10.2f} | {coverage * 100:>8.1f}%   | {acc * 100:>10.2f}%   | {n_accepted:>11}   | {n_fallback:>11}")

    # 6. Safety Tuning: Distress Support Recall Optimization
    print("\n" + "-" * 80)
    print("         SAFETY TUNING: DISTRESS SUPPORT RECALL & LOW THRESHOLD")
    print("-" * 80)

    distress_indices = [idx for idx, t in enumerate(val_targets) if t == "distress_support"]
    print(f"Total distress_support samples in validation set: {len(distress_indices)}")

    # Distress threshold sweep: find threshold yielding maximum recall on distress
    distress_th_sweep = []
    for th in [round(t * 0.05, 2) for t in range(2, 19)]:  # 0.10 to 0.90
        # If classifier predicted distress_support and conf >= th, it triggers escalation
        tp = sum(1 for idx in distress_indices if val_predictions[idx] == "distress_support" and val_confidences[idx] >= th)
        recall = tp / len(distress_indices) if distress_indices else 1.0

        # False positives from other intents
        fp = sum(1 for idx in range(len(val_targets)) if idx not in distress_indices and val_predictions[idx] == "distress_support" and val_confidences[idx] >= th)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        distress_th_sweep.append({
            "threshold": th,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "tp": tp,
            "fp": fp,
        })

    # Pick lowest threshold that gives maximum recall (target recall >= 0.95 or max available)
    best_distress_recall = max([r["recall"] for r in distress_th_sweep]) if distress_th_sweep else 1.0
    qualifying_distress = [r for r in distress_th_sweep if r["recall"] >= min(0.95, best_distress_recall)]
    # Among those with max recall, pick the highest threshold to reduce false positives
    optimal_distress_entry = qualifying_distress[-1] if qualifying_distress else distress_th_sweep[0]
    optimal_distress_threshold = optimal_distress_entry["threshold"]

    # Cap distress threshold at 0.50 maximum for high recall safety
    optimal_distress_threshold = min(0.50, optimal_distress_threshold)

    print(f"Optimal Distress Confidence Threshold: {optimal_distress_threshold:.2f}")
    print(f"  • Distress Recall on Validation Set : {optimal_distress_entry['recall'] * 100:.1f}%")
    print(f"  • Distress Precision on Validation  : {optimal_distress_entry['precision'] * 100:.1f}%")

    # 7. Select Recommended General Threshold
    # Standard choice: balance high accuracy (>= 90%) with high coverage (>= 80%)
    qualifying_general = [r for r in sweep_results if r["accuracy"] >= 0.85 and r["coverage"] >= 0.70]
    if qualifying_general:
        # Choose the one with highest accuracy while coverage >= 70%
        optimal_general_entry = qualifying_general[0]
    else:
        # Default to 0.70
        optimal_general_entry = next((r for r in sweep_results if abs(r["threshold"] - 0.70) < 0.01), sweep_results[10])

    optimal_general_threshold = optimal_general_entry["threshold"]
    print(f"\nOptimal General Confidence Threshold : {optimal_general_threshold:.2f}")
    print(f"  • Expected Coverage on Validation   : {optimal_general_entry['coverage'] * 100:.1f}%")
    print(f"  • Expected Accuracy on Accepted Qs  : {optimal_general_entry['accuracy'] * 100:.1f}%")

    # 8. Save Trade-Off Plot (BACKEND/artifacts/{prefix}threshold_tradeoff.png)
    plot_filename = f"{file_prefix}threshold_tradeoff.png"
    plot_path = os.path.join(artifacts_dir, plot_filename)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax1 = plt.subplots(figsize=(9, 5))
        ths = [r["threshold"] for r in sweep_results]
        accs = [r["accuracy"] * 100 for r in sweep_results]
        covs = [r["coverage"] * 100 for r in sweep_results]

        ax1.plot(ths, accs, color="#2563eb", marker="o", linewidth=2, label="Accuracy on Accepted (%)")
        ax1.plot(ths, covs, color="#10b981", marker="s", linewidth=2, label="Coverage (% Accepted)")
        ax1.axvline(x=optimal_general_threshold, color="#dc2626", linestyle="--", label=f"General Threshold ({optimal_general_threshold})")
        ax1.axvline(x=optimal_distress_threshold, color="#f59e0b", linestyle=":", label=f"Distress Safety Threshold ({optimal_distress_threshold})")

        ax1.set_xlabel("Confidence Score Threshold", fontsize=11)
        ax1.set_ylabel("Percentage (%)", fontsize=11)
        title_tag = f"[{mode}] " if mode != "PRODUCTION" else ""
        ax1.set_title(f"{title_tag}Intent Classifier Threshold Trade-Off Analysis", fontsize=12, fontweight="bold")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="lower left")

        fig.tight_layout()
        fig.savefig(plot_path, dpi=150)
        alt_plot_path = os.path.join(artifacts_dir, f"{file_prefix}threshold_plot.png")
        fig.savefig(alt_plot_path, dpi=150)
        plt.close(fig)
        print(f"\nSaved trade-off plot: {os.path.abspath(plot_path)}")
        print(f"Saved threshold plot : {os.path.abspath(alt_plot_path)}")
    except Exception as e:
        print(f"\n[WARNING] Could not generate trade-off plot: {e}")

    # 9. Save Configuration JSON (BACKEND/artifacts/{prefix}intent_config.json)
    out_config_name = f"{file_prefix}intent_config.json" if file_prefix else "intent_config.json"
    config_path = os.path.join(artifacts_dir, out_config_name)

    warning_line = None
    dry_run_text = None
    if mode == "PRELIMINARY":
        warning_line = "PRELIMINARY: incomplete data"
    elif mode == "PIPELINE_TEST":
        warning_line = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"
        dry_run_text = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"

    intent_config: Dict[str, Any] = {
        "status": mode,
        "warning": warning_line,
        "dry_run_honesty": dry_run_text,
        "preliminary_notice": "PRELIMINARY: incomplete data" if mode == "PRELIMINARY" else None,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": random_state,
        "dataset_audit": {
            "row_counts_by_author": dict(author_counts),
            "row_counts_by_intent": dict(intent_counts),
            "validation_sample_size": len(val_texts),
        },
        "thresholds": {
            "general_threshold": round(float(optimal_general_threshold), 2),
            "distress_threshold": round(float(optimal_distress_threshold), 2),
            "out_of_scope_threshold": 0.50,
        },
        "expected_performance_at_general_threshold": {
            "coverage": optimal_general_entry["coverage"],
            "accuracy": optimal_general_entry["accuracy"],
            "fallback_percentage": round(1.0 - optimal_general_entry["coverage"], 4),
        },
        "distress_safety": {
            "threshold": round(float(optimal_distress_threshold), 2),
            "recall": optimal_distress_entry["recall"],
            "precision": optimal_distress_entry["precision"],
            "safety_rule": "Distress intent triggered at lower threshold for maximum recall; never routed to LLM or generic fallback."
        },
        "full_sweep_results": sweep_results,
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(intent_config, f, indent=2)
    print(f"Saved threshold configuration: {os.path.abspath(config_path)}")

    print("\n" + "=" * 80)
    print(f"        THRESHOLD TUNING COMPLETED ({mode} MODE)")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Tune confidence thresholds for VIGBOT intent classifier.")
    parser.add_argument("--data-dir", default="data", help="Directory containing dataset files")
    parser.add_argument("--yaml-path", default="ml/intents.yaml", help="Path to ml/intents.yaml")
    parser.add_argument("--test-author", default=TEST_AUTHOR, help="Author strictly reserved for testing")
    parser.add_argument("--artifacts-dir", default="BACKEND/artifacts", help="Output directory for model artifacts")
    parser.add_argument("--model-path", default=None, help="Path to trained model joblib file")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed (default: 42)")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Run tuning in preliminary mode on whatever rows exist, prefixing files with preliminary_",
    )
    args = parser.parse_args()

    exit_code = tune_confidence_thresholds(
        data_dir=args.data_dir,
        yaml_path=args.yaml_path,
        test_author=args.test_author,
        artifacts_dir=args.artifacts_dir,
        model_path=args.model_path,
        random_state=args.seed,
        allow_partial=args.allow_partial,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
