#!/usr/bin/env python3
"""
VIGBOT: Intent Model Training & Cross-Validation Tuning (ml/train_intent.py)
Trains a TF-IDF (word + char n-grams) + Logistic Regression pipeline.
Never trains on or tunes with the designated test author (sridhar).
Enforces reproducible tuning (random_state=42), audits dataset quotas,
supports Leave-One-Author-Out cross-validation across training authors,
and outputs artifacts to BACKEND/artifacts/ (single source of truth).
"""

import os
import sys
import argparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict

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


def build_pipeline(
    word_ngram_range: Tuple[int, int] = (1, 2),
    char_ngram_range: Tuple[int, int] = (2, 5),
    C: float = 5.0,
    random_state: int = 42,
):
    """Constructs the TF-IDF (word + char) + LogisticRegression pipeline."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.linear_model import LogisticRegression

    feature_union = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            analyzer="word",
            lowercase=True,
            sublinear_tf=True,
            ngram_range=word_ngram_range,
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char_wb",
            lowercase=True,
            sublinear_tf=True,
            ngram_range=char_ngram_range,
        )),
    ])

    return Pipeline([
        ("features", feature_union),
        ("clf", LogisticRegression(
            class_weight="balanced",
            random_state=random_state,
            max_iter=1000,
            solver="lbfgs",
            C=C,
        ))
    ])


def train_intent_model(
    data_dir: str = "data",
    yaml_path: str = "ml/intents.yaml",
    test_author: str = TEST_AUTHOR,
    artifacts_dir: str = "BACKEND/artifacts",
    random_state: int = 42,
    allow_partial: bool = False,
    use_public: bool = False,
) -> int:
    """
    Executes intent classifier training and cross-validation hyperparameter tuning.
    Saves the best pipeline artifact and metadata JSON into BACKEND/artifacts/.
    """
    import sklearn
    from sklearn.metrics import classification_report, f1_score, accuracy_score
    import joblib

    test_author = test_author.strip().lower()

    # 1. Load intent schema
    intents_schema = load_intents_schema(yaml_path)
    valid_intents = sorted(list(intents_schema.keys()))

    # 2. Load dataset
    rows, load_errors = load_all_intent_data(data_dir, yaml_path, include_public=use_public)
    if load_errors:
        print("[FATAL ERROR] Dataset loading failed:")
        for err in load_errors:
            print(f"  ❌ {err}")
        return 1

    if use_public:
        print("  ℹ️ Public training data ENABLED (--use-public). Loaded clinc150 and massive from data/public/public_extra.csv.")

    # 3. Audit Quotas and Determine Pipeline Mode
    quotas = check_dataset_quotas(rows, valid_intents=set(valid_intents), test_author=test_author)
    is_ready = quotas["is_ready"]

    if is_ready:
        mode = "PRODUCTION"
        file_prefix = ""
        print("\n" + "=" * 80)
        print("          FULL PRODUCTION TRAINING (ALL HUMAN QUOTAS MET)")
        print("=" * 80 + "\n")
    elif allow_partial:
        mode = "PRELIMINARY"
        file_prefix = "preliminary_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PRELIMINARY RUN (--allow-partial enabled)                            *")
        print("*         PRELIMINARY: incomplete data                                         *")
        print("*" + " " * 78 + "*")
        print("*" * 80)
        print("  ℹ️ Training on available data in preliminary mode.")
        print(f"  ℹ️ Output artifacts will be prefixed with '{file_prefix}'.\n")
    else:
        mode = "PIPELINE_TEST"
        file_prefix = "pipeline_test_"
        print("\n" + "*" * 80)
        print("*" + " " * 78 + "*")
        print("*         PIPELINE TEST ONLY (human data incomplete)                           *")
        print("*" + " " * 78 + "*")
        print("*" * 80)
        print(f"  ℹ️ Notice: Training authors (aman, pragna, sirisha) have {len(quotas['training_deficits'])}/18 intents below quota.")
        print(f"  ℹ️ Notice: Test author ({test_author.upper()}) has {len(quotas['test_intent_deficits'])}/18 intents below test quota.")
        print("  ℹ️ Training on available data (agent starter seeds + any human training rows).")
        print(f"  ℹ️ Output artifacts will be prefixed with '{file_prefix}' to prevent treating as final results.\n")

    # 4. Filter out test author strictly
    train_rows = [r for r in rows if r["author"] != test_author]
    test_rows_excluded = [r for r in rows if r["author"] == test_author]

    print("-" * 80)
    print("                      DATASET SPLIT & SEQUESTRATION")
    print("-" * 80)
    print(f"Total rows in dataset               : {len(rows)}")
    print(f"Rows assigned to training           : {len(train_rows)}")
    print(f"Test author rows excluded ({test_author}): {len(test_rows_excluded)} (Strictly sequestered)")

    train_author_counts: Dict[str, int] = defaultdict(int)
    train_intent_counts: Dict[str, int] = defaultdict(int)
    for r in train_rows:
        train_author_counts[r["author"]] += 1
        train_intent_counts[r["intent"]] += 1

    print("Training rows by author             :")
    for a, cnt in sorted(train_author_counts.items()):
        print(f"  • {a:<10}: {cnt} rows")

    if not train_rows:
        print(f"[FATAL ERROR] No training rows available after excluding {test_author}.")
        return 1

    X_train = [r["text"] for r in train_rows]
    y_train = [r["intent"] for r in train_rows]

    present_classes = sorted(list(set(y_train)))
    print(f"Intents represented in training set : {len(present_classes)} / {len(valid_intents)}")

    # 5. Cross-Validation: Leave-One-Author-Out (if human rows exist) or Stratified K-Fold
    print("\n" + "-" * 80)
    print("             MODEL ARCHITECTURE & HYPERPARAMETER TUNING")
    print("-" * 80)
    print("Pipeline Components:")
    print("  1. Word-level TfidfVectorizer (sublinear_tf=True, ngram_range=(1, 2))")
    print("  2. Character-level TfidfVectorizer (analyzer='char_wb', sublinear_tf=True, ngram_range=(2, 5))")
    print("  3. FeatureUnion (combining word and character n-gram feature spaces)")
    print("  4. LogisticRegression (class_weight='balanced', random_state=42, max_iter=1000)")

    # Check for active training authors among human teammates
    active_human_authors = [a for a in TRAINING_AUTHORS if train_author_counts.get(a, 0) > 0]

    cv_type = ""
    loao_scores: Dict[str, float] = {}
    oof_predictions = []
    best_params: Dict[str, Any] = {}
    best_score: float = 0.0

    if len(active_human_authors) >= 2:
        cv_type = f"leave_one_author_out ({', '.join(active_human_authors)})"
        print(f"\nRunning Leave-One-Author-Out Cross-Validation across {len(active_human_authors)} human authors...")
        print("Agent starter rows are kept in the training split of every fold.")

        # Candidate hyperparameter combinations to evaluate
        candidates = [
            {"clf__C": 1.0, "char_ngrams": (2, 4), "word_ngrams": (1, 2)},
            {"clf__C": 2.0, "char_ngrams": (2, 5), "word_ngrams": (1, 2)},
            {"clf__C": 5.0, "char_ngrams": (2, 5), "word_ngrams": (1, 2)},
            {"clf__C": 10.0, "char_ngrams": (2, 5), "word_ngrams": (1, 2)},
        ]

        best_cand = candidates[2]  # Default C=5.0
        best_cand_macro = -1.0
        best_cand_loao_scores = {}
        best_cand_oof = []

        for cand in candidates:
            cand_loao = {}
            cand_oof_preds = []
            cand_oof_targets = []
            cand_oof_probs = []
            cand_oof_texts = []

            for held_out in active_human_authors:
                # Train fold: agent + all human authors except held_out
                fold_train = [r for r in train_rows if r["author"] != held_out]
                fold_val = [r for r in train_rows if r["author"] == held_out]

                X_f_tr = [r["text"] for r in fold_train]
                y_f_tr = [r["intent"] for r in fold_train]
                X_f_val = [r["text"] for r in fold_val]
                y_f_val = [r["intent"] for r in fold_val]

                pipe = build_pipeline(
                    word_ngram_range=cand["word_ngrams"],
                    char_ngram_range=cand["char_ngrams"],
                    C=cand["clf__C"],
                    random_state=random_state,
                )
                pipe.fit(X_f_tr, y_f_tr)
                val_preds = pipe.predict(X_f_val)
                val_probs = pipe.predict_proba(X_f_val)

                author_macro = float(f1_score(y_f_val, val_preds, average="macro", zero_division=0))
                cand_loao[held_out] = author_macro

                for idx, r in enumerate(fold_val):
                    cand_oof_preds.append(val_preds[idx])
                    cand_oof_targets.append(y_f_val[idx])
                    cand_oof_probs.append(val_probs[idx])
                    cand_oof_texts.append(r["text"])

            mean_macro = sum(cand_loao.values()) / len(cand_loao)
            if mean_macro > best_cand_macro:
                best_cand_macro = mean_macro
                best_cand = cand
                best_cand_loao_scores = cand_loao
                best_cand_oof = {
                    "texts": cand_oof_texts,
                    "targets": cand_oof_targets,
                    "predictions": cand_oof_preds,
                    "probabilities": cand_oof_probs,
                }

        best_score = best_cand_macro
        best_params = {
            "clf__C": best_cand["clf__C"],
            "features__char_tfidf__ngram_range": list(best_cand["char_ngrams"]),
            "features__word_tfidf__ngram_range": list(best_cand["word_ngrams"]),
        }
        loao_scores = best_cand_loao_scores
        oof_data = best_cand_oof

        print("\nLeave-One-Author-Out Macro-F1 by Held-out Author:")
        for auth, score in sorted(loao_scores.items()):
            print(f"  • {auth:<10}: {score:.4f} ({score * 100:.2f}%)")
        print(f"  Mean LOAO Macro-F1: {best_score:.4f} ({best_score * 100:.2f}%)")

        best_pipeline = build_pipeline(
            word_ngram_range=best_cand["word_ngrams"],
            char_ngram_range=best_cand["char_ngrams"],
            C=best_cand["clf__C"],
            random_state=random_state,
        )
        best_pipeline.fit(X_train, y_train)

    else:
        # Fallback when human training rows do not yet exist
        from sklearn.model_selection import StratifiedKFold, GridSearchCV
        cv_type = "stratified_5_fold (fallback on starter data; pipeline test only)"
        class_counts = Counter(y_train)
        min_count = min(class_counts.values())
        n_splits = max(2, min(5, min_count))

        print(f"\n[PIPELINE NOTICE] Human training rows incomplete ({len(active_human_authors)} human authors found).")
        print(f"Running Stratified {n_splits}-Fold Cross-Validation on starter data for pipeline verification...")

        base_pipe = build_pipeline(random_state=random_state)
        param_grid = {
            "features__word_tfidf__ngram_range": [(1, 1), (1, 2)],
            "features__char_tfidf__ngram_range": [(2, 4), (2, 5)],
            "clf__C": [0.5, 1.0, 2.0, 5.0, 10.0],
        }

        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        grid_search = GridSearchCV(
            estimator=base_pipe,
            param_grid=param_grid,
            cv=cv,
            scoring="f1_macro",
            n_jobs=-1,
            verbose=0,
        )
        grid_search.fit(X_train, y_train)

        best_pipeline = grid_search.best_estimator_
        best_score = float(grid_search.best_score_)
        best_params = {}
        for k, v in grid_search.best_params_.items():
            best_params[k] = list(v) if isinstance(v, tuple) else v

        # Compute out-of-fold predictions on CV for threshold tuning
        from sklearn.model_selection import cross_val_predict
        oof_preds = cross_val_predict(best_pipeline, X_train, y_train, cv=cv, method="predict")
        oof_probs = cross_val_predict(best_pipeline, X_train, y_train, cv=cv, method="predict_proba")
        oof_data = {
            "texts": X_train,
            "targets": y_train,
            "predictions": list(oof_preds),
            "probabilities": oof_probs,
            "classes": list(best_pipeline.classes_),
        }

    # 6. Fit check on full training set
    y_train_pred = best_pipeline.predict(X_train)
    train_acc = float(accuracy_score(y_train, y_train_pred))
    train_macro_f1 = float(f1_score(y_train, y_train_pred, average="macro"))

    print("\n" + "=" * 80)
    print("                         TUNING RESULTS")
    print("=" * 80)
    print(f"Validation Strategy        : {cv_type}")
    print(f"Validation Macro-F1 Score  : {best_score:.4f} ({best_score * 100:.2f}%)")
    print("Chosen Hyperparameters     :")
    for k, v in best_params.items():
        print(f"  • {k}: {v}")
    print(f"\nTraining Set Accuracy      : {train_acc:.4f} ({train_acc * 100:.2f}%)")
    print(f"Training Set Macro-F1      : {train_macro_f1:.4f} ({train_macro_f1 * 100:.2f}%)")

    # 7. Save Artifacts ONLY to BACKEND/artifacts/ (Single Source of Truth)
    os.makedirs(artifacts_dir, exist_ok=True)

    model_filename = f"{file_prefix}intent_model.joblib"
    meta_filename = f"{file_prefix}intent_train_metadata.json"
    oof_filename = f"{file_prefix}oof_predictions.joblib"

    # Save joblib model
    primary_model_path = os.path.join(artifacts_dir, model_filename)
    joblib.dump(best_pipeline, primary_model_path)
    print(f"\nSaved model artifact        : {os.path.abspath(primary_model_path)}")
    model_size_kb = os.path.getsize(primary_model_path) / 1024.0
    print(f"Model file size             : {model_size_kb:.2f} KB")

    # Save OOF predictions for threshold tuning
    oof_path = os.path.join(artifacts_dir, oof_filename)
    joblib.dump(oof_data, oof_path)
    print(f"Saved out-of-fold data      : {os.path.abspath(oof_path)}")

    # Metadata JSON structure
    warning_line = None
    dry_run_text = None
    if mode == "PRELIMINARY":
        warning_line = "PRELIMINARY: incomplete data"
    elif mode == "PIPELINE_TEST":
        warning_line = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"
        dry_run_text = "EVALUATED ON TRAINING DATA (code dry run, not a performance measure)"

    metadata: Dict[str, Any] = {
        "status": mode,
        "warning": warning_line,
        "dry_run_honesty": dry_run_text,
        "preliminary_notice": "PRELIMINARY: incomplete data" if mode == "PRELIMINARY" else None,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": random_state,
        "use_public": use_public,
        "scikit_learn_version": sklearn.__version__,
        "dataset": {
            "total_rows": len(rows),
            "training_rows": len(train_rows),
            "test_rows_excluded": len(test_rows_excluded),
            "test_author": test_author,
            "training_author_counts": dict(train_author_counts),
            "training_intent_counts": dict(train_intent_counts),
        },
        "classes": list(best_pipeline.classes_),
        "num_classes": len(best_pipeline.classes_),
        "cross_validation": {
            "strategy": cv_type,
            "metric": "f1_macro",
            "validation_macro_f1": round(best_score, 4),
            "loao_scores_by_author": loao_scores,
            "best_params": best_params,
        },
        "training_performance": {
            "accuracy": round(train_acc, 4),
            "macro_f1": round(train_macro_f1, 4),
        },
        "model_file": {
            "filename": model_filename,
            "size_kb": round(model_size_kb, 2),
        }
    }

    primary_meta_path = os.path.join(artifacts_dir, meta_filename)
    with open(primary_meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved training metadata     : {os.path.abspath(primary_meta_path)}")

    print("\n" + "=" * 80)
    print(f"        TRAINING COMPLETED ({mode} MODE)")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Train VIGBOT intent classification pipeline.")
    parser.add_argument("--data-dir", default="data", help="Directory containing dataset files")
    parser.add_argument("--yaml-path", default="ml/intents.yaml", help="Path to ml/intents.yaml")
    parser.add_argument("--test-author", default=TEST_AUTHOR, help="Author strictly reserved for testing")
    parser.add_argument("--artifacts-dir", default="BACKEND/artifacts", help="Output directory for model artifacts")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed (default: 42)")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Run in preliminary mode on whatever human rows exist, prefixing files with preliminary_",
    )
    parser.add_argument(
        "--use-public",
        action="store_true",
        default=False,
        help="Include public dataset (data/public/public_extra.csv) in training folds (default: False)",
    )
    args = parser.parse_args()

    exit_code = train_intent_model(
        data_dir=args.data_dir,
        yaml_path=args.yaml_path,
        test_author=args.test_author,
        artifacts_dir=args.artifacts_dir,
        random_state=args.seed,
        allow_partial=args.allow_partial,
        use_public=args.use_public,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
