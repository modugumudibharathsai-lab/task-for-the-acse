"""
Dataset loader and quota auditing module for VIGBOT intent classification.
Merges data/intents.csv (agent starter rows) with data/authors/*.csv files.
Enforces author normalization, file-stem author alignment, strict UTF-8 decoding,
leakage checking, and dataset readiness validation.
"""

import os
import glob
import csv
import difflib
import re
import yaml
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional, Set

# Author taxonomy
ALLOWED_AUTHORS = ["agent", "aman", "pragna", "sirisha", "sridhar"]
HUMAN_AUTHORS = ["aman", "pragna", "sirisha", "sridhar"]
TRAINING_AUTHORS = ["aman", "pragna", "sirisha"]
TEST_AUTHOR = "sridhar"
PUBLIC_AUTHORS = ["clinc150", "massive"]
ALL_VALID_AUTHORS = ALLOWED_AUTHORS + PUBLIC_AUTHORS

# Language taxonomy
ALLOWED_LANGS = ["en", "hinglish", "te_roman", "te", "hi"]

# 4 special topics with lower quotas:
# Human training authors: 14 each (42 combined)
# Test author (sridhar): 15 each
SPECIAL_QUOTA_INTENTS: Set[str] = {
    "policy_bylaws",
    "distress_support",
    "greeting_smalltalk",
    "out_of_scope",
}
MINOR_INTENTS = SPECIAL_QUOTA_INTENTS  # Backward compatibility alias


def load_intents_schema(yaml_path: str = "ml/intents.yaml") -> Dict[str, Any]:
    """Loads and returns the intent taxonomy from intents.yaml."""
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Intents schema not found at: {yaml_path}")
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("intents", {})


def read_csv_utf8_strict(filepath: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Reads a CSV file enforcing strict UTF-8 decoding and exact header validation.
    Reads with 'utf-8-sig' and strips spaces from header names.
    Fails on non-UTF-8 bytes and on any header other than text,intent,lang,author.
    Returns (rows, errors) where errors contains any UTF-8 decoding or parsing issues.
    """
    errors = []
    rows = []

    if not os.path.exists(filepath):
        return rows, [f"File does not exist: {filepath}"]

    # 1. Byte-level UTF-8 validation catching the exact line on failure
    try:
        with open(filepath, "rb") as bf:
            for line_idx, line_bytes in enumerate(bf, start=1):
                try:
                    line_bytes.decode("utf-8")
                except UnicodeDecodeError as ude:
                    errors.append(
                        f"UTF-8 Encoding Error in {filepath} at line {line_idx}: "
                        f"{ude.reason} for byte slice {line_bytes[max(0, ude.start-5):ude.end+5]!r}"
                    )
                    return [], errors
    except Exception as e:
        return [], [f"Error opening file {filepath}: {e}"]

    # 2. Parse CSV with utf-8-sig
    try:
        with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return [], [f"{filepath} is empty or missing header row."]

            # Strip spaces from header names
            raw_fieldnames = [c.strip() for c in reader.fieldnames if c is not None]
            required_cols = {"text", "intent", "lang", "author"}
            actual_cols = set(raw_fieldnames)

            # Strict header validation: fail on missing or extra headers
            missing = required_cols - actual_cols
            extra = actual_cols - required_cols
            if missing:
                errors.append(f"{filepath} is missing required columns: {sorted(missing)}")
                return [], errors
            if extra:
                errors.append(
                    f"{filepath} contains disallowed column(s): {sorted(extra)}. "
                    f"Headers must strictly be: text,intent,lang,author"
                )
                return [], errors

            # Update reader fieldnames to stripped versions
            reader.fieldnames = raw_fieldnames

            filename = os.path.basename(filepath)
            stem = os.path.splitext(filename)[0].lower()

            for row_idx, row in enumerate(reader, start=2):
                text = (row.get("text") or "").strip()
                intent = (row.get("intent") or "").strip().lower()
                lang = (row.get("lang") or "").strip().lower()
                author = (row.get("author") or "").strip().lower()

                if not text and not intent and not lang and not author:
                    continue  # Skip empty rows

                # Author integrity check
                if stem == "public_extra":
                    if author not in PUBLIC_AUTHORS:
                        errors.append(
                            f"Author integrity failure in {filepath}:{row_idx}: "
                            f"author '{author}' is not allowed in public dataset. Allowed: {PUBLIC_AUTHORS}."
                        )
                else:
                    if author in PUBLIC_AUTHORS:
                        errors.append(
                            f"Security leak in {filepath}:{row_idx}: "
                            f"public author '{author}' is only allowed in data/public/public_extra.csv, never in {filepath}."
                        )
                    expected_author = "agent" if stem == "intents" else stem
                    if author != expected_author:
                        errors.append(
                            f"Author integrity failure in {filepath}:{row_idx}: "
                            f"author '{author}' does not match expected file stem '{expected_author}'."
                        )

                # Prevent test author leakage outside sridhar.csv
                if author == TEST_AUTHOR and stem != TEST_AUTHOR:
                    errors.append(
                        f"Security leak in {filepath}:{row_idx}: "
                        f"author '{TEST_AUTHOR}' is not permitted outside data/authors/{TEST_AUTHOR}.csv."
                    )

                rows.append({
                    "text": text,
                    "intent": intent,
                    "lang": lang,
                    "author": author,
                    "_file": filepath,
                    "_line": row_idx,
                })

    except Exception as e:
        errors.append(f"Failed to parse CSV {filepath}: {e}")

    return rows, errors


def load_crisis_test_data(filepath: str = "data/crisis_test.csv") -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Loads optional data/crisis_test.csv (text,lang).
    Reads with utf-8-sig and strips spaces from header names.
    Fails on non-UTF-8 bytes and on any header other than text,lang.
    Returns (rows, errors).
    """
    errors = []
    rows = []

    if not os.path.exists(filepath):
        return rows, [f"File does not exist: {filepath}"]

    # 1. Byte-level UTF-8 validation
    try:
        with open(filepath, "rb") as bf:
            for line_idx, line_bytes in enumerate(bf, start=1):
                try:
                    line_bytes.decode("utf-8")
                except UnicodeDecodeError as ude:
                    errors.append(
                        f"UTF-8 Encoding Error in {filepath} at line {line_idx}: "
                        f"{ude.reason} for byte slice {line_bytes[max(0, ude.start-5):ude.end+5]!r}"
                    )
                    return [], errors
    except Exception as e:
        return [], [f"Error opening file {filepath}: {e}"]

    # 2. Parse CSV with utf-8-sig
    try:
        with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return [], [f"{filepath} is empty or missing header row."]

            raw_fieldnames = [c.strip() for c in reader.fieldnames if c is not None]
            required_cols = {"text", "lang"}
            actual_cols = set(raw_fieldnames)

            missing = required_cols - actual_cols
            extra = actual_cols - required_cols
            if missing:
                errors.append(f"{filepath} is missing required columns: {sorted(missing)}")
                return [], errors
            if extra:
                errors.append(
                    f"{filepath} contains disallowed column(s): {sorted(extra)}. "
                    f"Headers must strictly be: text,lang"
                )
                return [], errors

            reader.fieldnames = raw_fieldnames

            for row_idx, row in enumerate(reader, start=2):
                text = (row.get("text") or "").strip()
                lang = (row.get("lang") or "").strip().lower()
                if not text and not lang:
                    continue
                rows.append({
                    "text": text,
                    "lang": lang,
                    "_file": filepath,
                    "_line": row_idx,
                })
    except Exception as e:
        errors.append(f"Failed to parse crisis test CSV {filepath}: {e}")

    return rows, errors


def load_all_intent_data(
    data_dir: str = "data",
    yaml_path: str = "ml/intents.yaml",
    include_public: bool = False,
    public_file: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Discovers data/intents.csv, all data/authors/*.csv files,
    and optionally data/public/public_extra.csv (if include_public=True),
    parses and merges them, returning (rows, errors).
    """
    all_rows: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    # 1. Load starter file (author=agent)
    starter_file = os.path.join(data_dir, "intents.csv")
    if os.path.exists(starter_file):
        s_rows, s_errs = read_csv_utf8_strict(starter_file)
        all_rows.extend(s_rows)
        all_errors.extend(s_errs)
    else:
        all_errors.append(f"Starter dataset missing: {starter_file}")

    # 2. Load teammate files in data/authors/*.csv
    authors_pattern = os.path.join(data_dir, "authors", "*.csv")
    author_files = sorted(glob.glob(authors_pattern))
    for af in author_files:
        a_rows, a_errs = read_csv_utf8_strict(af)
        all_rows.extend(a_rows)
        all_errors.extend(a_errs)

    # 3. Load optional public training dataset if requested
    if include_public:
        target_public = public_file if public_file else os.path.join(data_dir, "public", "public_extra.csv")
        if os.path.exists(target_public):
            p_rows, p_errs = read_csv_utf8_strict(target_public)
            all_rows.extend(p_rows)
            all_errors.extend(p_errs)
        else:
            all_errors.append(f"Public dataset requested via include_public=True but file not found: {target_public}")

    return all_rows, all_errors


def check_dataset_quotas(
    rows: List[Dict[str, Any]],
    valid_intents: Optional[Set[str]] = None,
    test_author: str = TEST_AUTHOR
) -> Dict[str, Any]:
    """
    Audits dataset quotas:
    1. Human training authors (aman, pragna, sirisha):
       - 20 rows per topic each (combined target 60) for 14 standard topics.
       - 14 rows each (combined target 42) for policy_bylaws, distress_support, greeting_smalltalk, out_of_scope.
       - Agent starter rows and test author rows are strictly EXCLUDED from training quotas.
    2. Test author (sridhar):
       - At least 20 rows per topic (15 for the four special topics).
       - At least 20 rows per language to be reported.
    """
    if valid_intents is None:
        valid_intents = set(load_intents_schema().keys())

    # Count training authors (combined and individual)
    training_intent_counts: Dict[str, int] = defaultdict(int)
    author_intent_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Count test author
    test_intent_counts: Dict[str, int] = defaultdict(int)
    test_lang_counts: Dict[str, int] = defaultdict(int)

    for r in rows:
        author = r["author"]
        intent = r["intent"]
        lang = r["lang"]

        author_intent_counts[author][intent] += 1

        if author in TRAINING_AUTHORS:
            training_intent_counts[intent] += 1
        elif author == test_author:
            test_intent_counts[intent] += 1
            test_lang_counts[lang] += 1

    # 1. Combined training author deficits (60 standard, 42 special)
    training_deficits = []
    for intent in sorted(valid_intents):
        is_special = intent in SPECIAL_QUOTA_INTENTS
        target = 42 if is_special else 60
        actual = training_intent_counts.get(intent, 0)
        if actual < target:
            training_deficits.append({
                "intent": intent,
                "target": target,
                "actual": actual,
                "deficit": target - actual,
                "is_special": is_special,
            })

    # Individual training author deficits (20 standard, 14 special per author)
    individual_deficits = {}
    for author in TRAINING_AUTHORS:
        author_deficits = []
        for intent in sorted(valid_intents):
            is_special = intent in SPECIAL_QUOTA_INTENTS
            target = 14 if is_special else 20
            actual = author_intent_counts[author].get(intent, 0)
            if actual < target:
                author_deficits.append({
                    "intent": intent,
                    "target": target,
                    "actual": actual,
                    "deficit": target - actual,
                })
        individual_deficits[author] = author_deficits

    # 2. Test author intent deficits (20 standard, 15 special)
    test_intent_deficits = []
    for intent in sorted(valid_intents):
        is_special = intent in SPECIAL_QUOTA_INTENTS
        target = 15 if is_special else 20
        actual = test_intent_counts.get(intent, 0)
        if actual < target:
            test_intent_deficits.append({
                "intent": intent,
                "target": target,
                "actual": actual,
                "deficit": target - actual,
                "is_special": is_special,
            })

    # 3. Test author language counts
    test_lang_deficits = []
    for lang in ALLOWED_LANGS:
        target = 20
        actual = test_lang_counts.get(lang, 0)
        if actual < target:
            test_lang_deficits.append({
                "lang": lang,
                "target": target,
                "actual": actual,
                "deficit": target - actual,
            })

    is_ready = (len(training_deficits) == 0) and (len(test_intent_deficits) == 0)

    return {
        "is_ready": is_ready,
        "training_deficits": training_deficits,
        "individual_deficits": individual_deficits,
        "test_intent_deficits": test_intent_deficits,
        "test_lang_deficits": test_lang_deficits,
        "training_intent_counts": dict(training_intent_counts),
        "test_intent_counts": dict(test_intent_counts),
        "test_lang_counts": dict(test_lang_counts),
        "author_intent_counts": {k: dict(v) for k, v in author_intent_counts.items()},
    }


def find_test_train_leakage(
    rows: List[Dict[str, Any]],
    test_author: str = TEST_AUTHOR,
    similarity_threshold: float = 0.8
) -> List[Dict[str, Any]]:
    """
    Compares every test author row against all training rows (including agent starter rows).
    Computes both word-level Jaccard and character-level difflib ratio.
    Flags matches with either similarity >= similarity_threshold.
    Returns matched pairs and specifies the TRAINING row to remove.
    """
    test_rows = [r for r in rows if r["author"] == test_author]
    train_rows = [r for r in rows if r["author"] != test_author]

    leakage_matches = []

    for t_row in test_rows:
        t_text = t_row["text"].strip().lower()
        t_words = set(re.findall(r"\w+", t_text))

        for tr_row in train_rows:
            tr_text = tr_row["text"].strip().lower()
            tr_words = set(re.findall(r"\w+", tr_text))

            # 1. Word-level Jaccard
            union = len(t_words | tr_words)
            jaccard = (len(t_words & tr_words) / union) if union > 0 else 0.0

            # 2. Character-level similarity (difflib ratio)
            char_ratio = difflib.SequenceMatcher(None, t_text, tr_text).ratio()

            max_score = max(jaccard, char_ratio)
            if max_score >= similarity_threshold:
                leakage_matches.append({
                    "score": max_score,
                    "jaccard": jaccard,
                    "char_ratio": char_ratio,
                    "test_row": t_row,
                    "train_row": tr_row,
                    "recommendation": (
                        f"REMOVE TRAINING ROW from {tr_row['_file']}:{tr_row['_line']} "
                        f"(author: {tr_row['author']}): \"{tr_row['text']}\""
                    )
                })

    return leakage_matches
