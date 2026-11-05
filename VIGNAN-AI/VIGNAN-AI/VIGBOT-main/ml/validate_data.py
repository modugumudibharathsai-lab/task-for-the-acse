#!/usr/bin/env python3
"""
VIGBOT: Dataset Validation Pipeline (ml/validate_data.py)
Enforces data integrity, UTF-8 compliance, exact header adherence (text,intent,lang,author),
author attribution guardrails, exact duplicate detection, test-to-train leakage auditing,
and quota tracking across the team's 18 topics.
"""

import os
import sys
import argparse
import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add parent directory to path so imports work cleanly from any cwd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    find_test_train_leakage,
)


def compute_jaccard_similarity(s1: str, s2: str) -> float:
    """Computes word-level Jaccard similarity between two texts."""
    words1 = set(re.findall(r"\w+", s1.lower()))
    words2 = set(re.findall(r"\w+", s2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union > 0 else 0.0


def validate_dataset(
    data_dir: str = "data",
    yaml_path: str = "ml/intents.yaml",
    test_author: str = TEST_AUTHOR,
    strict_mode: bool = False,
) -> int:
    """
    Validates dataset integrity and prints comprehensive progress report.
    Returns 0 on success, 1 on validation error.
    """
    test_author = test_author.strip().lower()
    print("=" * 80)
    print("      VIGBOT: DATASET VALIDATION & TEAM PROGRESS REPORT (18 TOPICS)")
    print("=" * 80)
    print(f"Data Directory  : {os.path.abspath(data_dir)}")
    print(f"Intents Schema  : {os.path.abspath(yaml_path)}")
    print(f"Allowed Authors : {', '.join(ALLOWED_AUTHORS)}")
    print(f"Training Authors: {', '.join(TRAINING_AUTHORS)} (Counted toward quota: 20 each / 14 each for special)")
    print(f"Test Author     : {test_author.upper()} (Excluded from training/tuning; needs >=20 / 15 per intent)")
    print(f"Validation Mode : {'STRICT (Enforces full human quotas)' if strict_mode else 'INFORMATIONAL (Progress reporting)'}")
    print("-" * 80)

    # 1. Load intent schema
    try:
        intents_schema = load_intents_schema(yaml_path)
    except Exception as e:
        print(f"\n[FATAL ERROR] Failed to load intents schema: {e}")
        return 1

    valid_intents = set(intents_schema.keys())
    print(f"Registered Intents in Schema: {len(valid_intents)} topics")

    # 2. Load merged data with strict UTF-8 decoding & exact header validation
    rows, load_errors = load_all_intent_data(data_dir, yaml_path)
    if load_errors:
        print(f"\n[FATAL ERROR] Found {len(load_errors)} file loading / author integrity errors:")
        for err in load_errors:
            print(f"  ❌ {err}")
        print("\nFix encoding, header, or author integrity errors before proceeding.")
        return 1

    print(f"Total Rows Loaded (Starter + Teammate Files): {len(rows)}")

    # 3. Structural & Value Validations
    structural_errors: List[str] = []
    normalized_rows = []

    for idx, r in enumerate(rows):
        file_info = f"{r.get('_file', 'unknown')}:{r.get('_line', idx+1)}"
        text = r.get("text", "").strip()
        intent = r.get("intent", "").strip().lower()
        lang = r.get("lang", "").strip().lower()
        author = r.get("author", "").strip().lower()

        if not text:
            structural_errors.append(f"{file_info}: Empty 'text' column.")

        if author not in ALLOWED_AUTHORS:
            structural_errors.append(
                f"{file_info}: Invalid author '{author}'. Must be one of: {ALLOWED_AUTHORS}"
            )

        if intent not in valid_intents:
            structural_errors.append(
                f"{file_info}: Unknown intent '{intent}'. Not found in {yaml_path}"
            )

        if lang not in ALLOWED_LANGS:
            structural_errors.append(
                f"{file_info}: Invalid language code '{lang}'. Must be one of: {ALLOWED_LANGS}"
            )

        normalized_rows.append({
            "text": text,
            "intent": intent,
            "lang": lang,
            "author": author,
            "_file": r.get("_file"),
            "_line": r.get("_line"),
        })

    if structural_errors:
        print(f"\n[VALIDATION FAILED] Found {len(structural_errors)} structural / author errors:")
        for err in structural_errors[:20]:
            print(f"  ❌ {err}")
        if len(structural_errors) > 20:
            print(f"  ... and {len(structural_errors) - 20} more errors.")
        return 1

    # 4. Duplicate Detection (Exact & Near Duplicates)
    print("\nScanning for exact and near-duplicate queries...")
    exact_duplicates: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in normalized_rows:
        norm_key = re.sub(r"\s+", " ", r["text"].lower().strip())
        exact_duplicates[norm_key].append(r)

    found_exact_dupes = {k: v for k, v in exact_duplicates.items() if len(v) > 1}
    if found_exact_dupes:
        print(f"  ❌ Found {len(found_exact_dupes)} exact duplicate query text(s):")
        for text_key, dup_list in list(found_exact_dupes.items())[:10]:
            locs = [f"{d['_file']}:{d['_line']} (author: {d['author']})" for d in dup_list]
            print(f"    - \"{text_key}\" -> present in: {', '.join(locs)}")
        if len(found_exact_dupes) > 10:
            print(f"    ... and {len(found_exact_dupes) - 10} more exact duplicates.")
        print("  [ERROR] Exact duplicates are not allowed. Please ensure question variety.")
        return 1
    else:
        print("  ✅ Zero exact duplicates found.")

    # Near duplicates (within each intent)
    near_duplicates: List[Tuple[Dict[str, Any], Dict[str, Any], float]] = []
    rows_by_intent: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in normalized_rows:
        rows_by_intent[r["intent"]].append(r)

    for intent, i_rows in rows_by_intent.items():
        n = len(i_rows)
        for i in range(n):
            for j in range(i + 1, min(i + 25, n)):
                sim = compute_jaccard_similarity(i_rows[i]["text"], i_rows[j]["text"])
                if sim >= 0.85:
                    near_duplicates.append((i_rows[i], i_rows[j], sim))

    if near_duplicates:
        print(f"  ⚠️  Found {len(near_duplicates)} potential near-duplicate pairs (Jaccard >= 0.85):")
        for r1, r2, score in near_duplicates[:5]:
            print(f"    - Score {score:.2f}: \"{r1['text']}\" ({r1['author']}) vs \"{r2['text']}\" ({r2['author']})")
    else:
        print("  ✅ Near-duplicate check passed.")

    # 5. Data Leakage Check: Test Author (Sridhar) vs All Training Rows
    print("\n" + "-" * 80)
    print("            LEAKAGE CHECK: TEST AUTHOR vs ALL TRAINING ROWS")
    print(f"   Auditing {test_author.upper()} rows against (aman, pragna, sirisha, agent)")
    print("-" * 80)

    leakage_matches = find_test_train_leakage(normalized_rows, test_author=test_author, similarity_threshold=0.8)
    if leakage_matches:
        print(f"  ⚠️  POTENTIAL DATA LEAKAGE DETECTED ({len(leakage_matches)} matches with similarity >= 0.80):")
        for match in leakage_matches:
            t_row = match["test_row"]
            tr_row = match["train_row"]
            print(f"    • Score: {match['score']:.2f} (Token Jaccard: {match['jaccard']:.2f}, Char Ratio: {match['char_ratio']:.2f})")
            print(f"      - TEST ROW     ({test_author}): \"{t_row['text']}\" [{t_row['_file']}:{t_row['_line']}]")
            print(f"      - TRAINING ROW ({tr_row['author']}): \"{tr_row['text']}\" [{tr_row['_file']}:{tr_row['_line']}]")
            print(f"      - ACTION REQUIRED: {match['recommendation']}")
        print("\n  [RULE] Never delete or edit test rows automatically. Remove the offending training row instead.")
    else:
        print(f"  ✅ Zero test-train leakage detected for {test_author.upper()} (checked token Jaccard & char ratio).")

    # 6. Author and Language Overview
    author_counts: Dict[str, int] = defaultdict(int)
    lang_counts: Dict[str, int] = defaultdict(int)
    for r in normalized_rows:
        author_counts[r["author"]] += 1
        lang_counts[r["lang"]] += 1

    print("\n" + "=" * 80)
    print("                       TEAM CONTRIBUTION BREAKDOWN")
    print("=" * 80)
    for a in ALLOWED_AUTHORS:
        role = "Test Author" if a == test_author else ("Starter Data" if a == "agent" else "Training Author")
        count = author_counts.get(a, 0)
        status = "✅ Active" if count > 0 else "⏳ Awaiting input"
        print(f"  • {a:<10} ({role:<16}): {count:>4} rows  [{status}]")

    print("\nSummary by Language (Entire Dataset):")
    for lang in ALLOWED_LANGS:
        print(f"  • {lang:<10}: {lang_counts.get(lang, 0):>4} rows")

    # 7. Quota Audit: Table 1 - Training Authors Only (aman, pragna, sirisha)
    quotas = check_dataset_quotas(normalized_rows, valid_intents=valid_intents, test_author=test_author)

    print("\n" + "=" * 80)
    print("  TABLE 1: TRAINING QUOTAS (aman, pragna, sirisha ONLY; agent & sridhar excluded)")
    print("  Target: 60 rows for Standard Topics (20 each), 42 rows for Special Topics (14 each)")
    print("=" * 80)
    print(f"{'Intent Key':<22} | {'Category':<8} | {'Target':<6} | {'Training':<8} | {'Status'}")
    print("-" * 80)

    for intent in sorted(valid_intents):
        is_special = intent in SPECIAL_QUOTA_INTENTS
        target = 42 if is_special else 60
        actual = quotas["training_intent_counts"].get(intent, 0)
        category = "Special" if is_special else "Standard"
        if actual >= target:
            status = "✅ Met Target"
        else:
            deficit = target - actual
            status = f"⚠️ Deficit (-{deficit})"
        print(f"{intent:<22} | {category:<8} | {target:<6} | {actual:<8} | {status}")

    # 8. Quota Audit: Table 2 - Test Author (sridhar) Requirements
    print("\n" + "=" * 80)
    print(f"  TABLE 2: TEST AUTHOR REQUIREMENTS ({test_author.upper()} ONLY)")
    print("  Target: >= 20 rows per intent (15 for special intents) & >= 20 rows per language")
    print("=" * 80)
    print(f"{'Intent Key':<22} | {'Category':<8} | {'Min Target':<10} | {'Test Rows':<9} | {'Status'}")
    print("-" * 80)

    for intent in sorted(valid_intents):
        is_special = intent in SPECIAL_QUOTA_INTENTS
        target = 15 if is_special else 20
        actual = quotas["test_intent_counts"].get(intent, 0)
        category = "Special" if is_special else "Standard"
        if actual >= target:
            status = "✅ Ready"
        else:
            deficit = target - actual
            status = f"⚠️ Deficit (-{deficit})"
        print(f"{intent:<22} | {category:<8} | {target:<10} | {actual:<9} | {status}")

    print(f"\nLanguage Distribution for Test Author ({test_author.upper()}):")
    for lang in ALLOWED_LANGS:
        actual = quotas["test_lang_counts"].get(lang, 0)
        status = "✅ Evaluator Ready (>= 20)" if actual >= 20 else f"ℹ️ Sparse ({actual}/20 rows; report will skip or label sparse)"
        print(f"  • {lang:<10}: {actual:>3} / 20 target [{status}]")

    # 9. Individual Human Teammate Target Checklist
    print("\n" + "-" * 80)
    print("               INDIVIDUAL HUMAN TEAMMATE WORK REMAINING")
    print("   Target: 20 rows per standard topic, 14 for special topics (15 for sridhar)")
    print("-" * 80)

    for member in HUMAN_AUTHORS:
        mem_counts = quotas["author_intent_counts"].get(member, {})
        total_member_rows = author_counts.get(member, 0)
        remaining = 0
        missing_intents = []
        for intent in sorted(valid_intents):
            is_special = intent in SPECIAL_QUOTA_INTENTS
            if member == test_author:
                target_per_mem = 15 if is_special else 20
            else:
                target_per_mem = 14 if is_special else 20

            c = mem_counts.get(intent, 0)
            if c < target_per_mem:
                diff = target_per_mem - c
                remaining += diff
                missing_intents.append(f"{intent}(-{diff})")

        role_tag = "[TEST AUTHOR]" if member == test_author else "[TRAINING]"
        print(f"\nTeammate: {member.upper()} {role_tag}")
        print(f"  • Rows Contributed  : {total_member_rows}")
        print(f"  • Remaining to Target: {remaining} rows")
        if missing_intents:
            sample = ", ".join(missing_intents[:4])
            if len(missing_intents) > 4:
                sample += f", and {len(missing_intents) - 4} more"
            print(f"  • Deficit Sample     : {sample}")
        else:
            print("  • Deficit Sample     : None (Target achieved!)")

    # 10. Optional Crisis Test Dataset Check
    crisis_file = os.path.join(data_dir, "crisis_test.csv")
    print("\n" + "-" * 80)
    print("                  CRISIS TEST SUITE AUDIT (OPTIONAL)")
    print("-" * 80)
    if os.path.exists(crisis_file):
        c_rows, c_errs = load_crisis_test_data(crisis_file)
        if c_errs:
            print(f"  ⚠️  Found {len(c_errs)} errors in {crisis_file}:")
            for ce in c_errs:
                print(f"     ❌ {ce}")
        else:
            print(f"  ✅ {crisis_file} found with {len(c_rows)} crisis test phrases (ready for crisis recall evaluation).")
    else:
        print(f"  ℹ️  {crisis_file} not present (optional; create with header text,lang to evaluate crisis-phrase recall).")

    # 11. Summary & Exit Handling
    print("\n" + "=" * 80)
    print("                         VALIDATION SUMMARY")
    print("=" * 80)
    print("  ✅ Strict UTF-8 Encoding     : Passed")
    print("  ✅ Required CSV Headers      : Passed (text, intent, lang, author strictly)")
    print("  ✅ File-Stem Author Guard   : Passed (author matches filename stem)")
    print("  ✅ Zero Sridhar Leakage Out  : Passed (sridhar rows only in sridhar.csv)")
    print("  ✅ Zero Exact Duplicates     : Passed")

    has_quota_deficits = (len(quotas["training_deficits"]) > 0) or (len(quotas["test_intent_deficits"]) > 0)

    if has_quota_deficits:
        print(f"\n  ℹ️  Notice: Human training/test data collection status:")
        print(f"      - Training author deficits: {len(quotas['training_deficits'])}/18 intents below quota.")
        print(f"      - Test author deficits    : {len(quotas['test_intent_deficits'])}/18 intents below test quota.")

    if strict_mode and has_quota_deficits:
        print("\n[VALIDATION FAILED] --strict was specified and human quotas are not yet fully met.")
        return 1

    print("\n[VALIDATION SUCCESS] All structural, syntax, and author integrity checks passed successfully!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate VIGBOT intent dataset across 18 topics.")
    parser.add_argument("--data-dir", default="data", help="Directory containing dataset files")
    parser.add_argument("--yaml-path", default="ml/intents.yaml", help="Path to ml/intents.yaml")
    parser.add_argument("--test-author", default=TEST_AUTHOR, help="Author reserved for testing")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail validation with non-zero exit code if any quota or test-author requirement is unmet",
    )
    args = parser.parse_args()

    exit_code = validate_dataset(
        data_dir=args.data_dir,
        yaml_path=args.yaml_path,
        test_author=args.test_author,
        strict_mode=args.strict,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
