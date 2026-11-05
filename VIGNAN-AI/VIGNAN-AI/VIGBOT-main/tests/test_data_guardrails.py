"""
Tests for VIGBOT Data Guardrails & Integrity Checks (tests/test_data_guardrails.py).
Uses temporary CSV directories to verify:
1. Author column not matching file stem.
2. A sridhar row outside sridhar.csv.
3. A non-allowed author name.
4. A non-UTF-8 byte sequence in data file.
5. A test row that is a typo variant of a training row (must be reported by leakage check).
6. Exact duplicate query detection.
7. The --strict exit code behavior (code 1 on unmet quotas vs 0 on default mode).
8. Strict rejection of any CSV header other than 'text,intent,lang,author'.
9. Proper parsing of utf-8-sig and stripping of whitespace in CSV headers.
10. Crisis test data loader guardrails (optional crisis_test.csv).
"""

import os
import sys
import csv
import pytest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.dataset_loader import (
    load_all_intent_data,
    read_csv_utf8_strict,
    load_crisis_test_data,
    find_test_train_leakage,
    check_dataset_quotas,
    ALLOWED_AUTHORS,
    TEST_AUTHOR,
)
from ml.validate_data import validate_dataset


def create_minimal_intents_yaml(path: Path):
    """Creates a minimal intents.yaml schema for testing."""
    content = """
intents:
  attendance:
    description: Attendance inquiries
    is_minor: false
  distress_support:
    description: Crisis support
    is_minor: true
  services:
    description: Student services
    is_minor: false
  hostel:
    description: Hostel accommodation
    is_minor: false
  clubs:
    description: Student clubs
    is_minor: false
"""
    path.write_text(content.strip(), encoding="utf-8")


def write_test_csv(file_path: Path, rows, headers=None):
    """Helper to write CSV with proper quotes and UTF-8 encoding."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = ["text", "intent", "lang", "author"]
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)


def test_author_column_not_matching_file_stem(tmp_path):
    """Guardrail 1: Fail if author column differs from file stem (e.g. aman inside pragna.csv)."""
    csv_file = tmp_path / "pragna.csv"
    write_test_csv(csv_file, [
        ["Where is the library?", "hostel", "en", "aman"]  # mismatch!
    ])
    rows, errors = read_csv_utf8_strict(str(csv_file))
    assert len(errors) > 0
    assert any("does not match expected file stem 'pragna'" in err for err in errors)


def test_sridhar_row_outside_sridhar_csv(tmp_path):
    """Guardrail 2: Fail if any row with author sridhar appears outside sridhar.csv."""
    csv_file = tmp_path / "aman.csv"
    write_test_csv(csv_file, [
        ["How do I apply for bonafide?", "services", "en", "sridhar"]  # sridhar inside aman.csv!
    ])
    rows, errors = read_csv_utf8_strict(str(csv_file))
    assert len(errors) > 0
    assert any("not permitted outside data/authors/sridhar.csv" in err for err in errors)


def test_non_allowed_author(tmp_path):
    """Guardrail 3: Fail on non-allowed author names (e.g. unknown or typo)."""
    yaml_file = tmp_path / "intents.yaml"
    create_minimal_intents_yaml(yaml_file)

    data_dir = tmp_path / "data"
    starter_csv = data_dir / "intents.csv"
    write_test_csv(starter_csv, [
        ["What is my attendance?", "attendance", "en", "agent"]
    ])
    # An unknown author file
    unknown_csv = data_dir / "authors" / "john.csv"
    write_test_csv(unknown_csv, [
        ["What are the clubs?", "clubs", "en", "john"]
    ])

    exit_code = validate_dataset(data_dir=str(data_dir), yaml_path=str(yaml_file), strict_mode=False)
    assert exit_code == 1


def test_non_utf8_byte_detection(tmp_path):
    """Guardrail 4: Fail on non-UTF-8 bytes and show the offending file/line."""
    csv_file = tmp_path / "broken.csv"
    # Write invalid non-UTF-8 bytes directly
    with open(csv_file, "wb") as f:
        f.write(b"text,intent,lang,author\n")
        f.write(b"Valid line,attendance,en,broken\n")
        f.write(b"Invalid \xff\xfe byte,attendance,en,broken\n")

    rows, errors = read_csv_utf8_strict(str(csv_file))
    assert len(errors) > 0
    assert any("UTF-8 Encoding Error" in err and "line 3" in err for err in errors)


def test_test_row_typo_variant_leakage_reported():
    """Guardrail 5: Leakage check must catch typo variants between sridhar and training rows."""
    dataset = [
        # Training row (agent)
        {
            "text": "What is my attendance percentage?",
            "intent": "attendance",
            "lang": "en",
            "author": "agent",
            "_file": "data/intents.csv",
            "_line": 10,
        },
        # Test row (sridhar) with typo variant ("attendence" instead of "attendance")
        {
            "text": "What is my attendence percentage?",
            "intent": "attendance",
            "lang": "en",
            "author": "sridhar",
            "_file": "data/authors/sridhar.csv",
            "_line": 5,
        },
    ]

    leakage = find_test_train_leakage(dataset, test_author="sridhar", similarity_threshold=0.8)
    assert len(leakage) > 0
    assert leakage[0]["score"] >= 0.80
    assert "REMOVE TRAINING ROW" in leakage[0]["recommendation"]
    # Test row must remain untouched
    assert leakage[0]["test_row"]["author"] == "sridhar"


def test_exact_duplicate_detection(tmp_path):
    """Guardrail 6: Fail on exact duplicate queries across rows."""
    yaml_file = tmp_path / "intents.yaml"
    create_minimal_intents_yaml(yaml_file)

    data_dir = tmp_path / "data"
    starter_csv = data_dir / "intents.csv"
    write_test_csv(starter_csv, [
        ["Where can I see my attendance?", "attendance", "en", "agent"],
        ["Where can I see my attendance?", "attendance", "en", "agent"],  # exact duplicate
    ])

    exit_code = validate_dataset(data_dir=str(data_dir), yaml_path=str(yaml_file), strict_mode=False)
    assert exit_code == 1


def test_strict_mode_exit_code(tmp_path):
    """Guardrail 7: validate_data.py exits 0 on default mode and 1 on --strict when quotas unmet."""
    yaml_file = tmp_path / "intents.yaml"
    create_minimal_intents_yaml(yaml_file)

    data_dir = tmp_path / "data"
    starter_csv = data_dir / "intents.csv"
    write_test_csv(starter_csv, [
        ["How is my attendance calculated?", "attendance", "en", "agent"]
    ])
    # Empty teammate templates
    for a in ["aman", "pragna", "sirisha", "sridhar"]:
        af = data_dir / "authors" / f"{a}.csv"
        write_test_csv(af, [])

    # Default informational mode exits 0
    exit_default = validate_dataset(data_dir=str(data_dir), yaml_path=str(yaml_file), strict_mode=False)
    assert exit_default == 0

    # Strict mode exits 1 when human quotas are not met
    exit_strict = validate_dataset(data_dir=str(data_dir), yaml_path=str(yaml_file), strict_mode=True)
    assert exit_strict == 1


def test_header_validation_rejects_extra_or_invalid_headers(tmp_path):
    """Guardrail 8: Fail if headers are anything other than text,intent,lang,author."""
    csv_file = tmp_path / "invalid_headers.csv"
    write_test_csv(csv_file, [["Sample question", "attendance", "en", "agent", "extra_value"]], headers=["text", "intent", "lang", "author", "extra_col"])

    rows, errors = read_csv_utf8_strict(str(csv_file))
    assert len(errors) > 0
    assert any("contains disallowed column(s)" in err for err in errors)


def test_utf8_sig_and_header_space_stripping(tmp_path):
    """Guardrail 9: Parse utf-8-sig cleanly and strip leading/trailing spaces from headers."""
    csv_file = tmp_path / "intents.csv"
    # Write UTF-8 with BOM and spaced headers
    bom_content = "\ufeff text , intent , lang , author \nWhere is fee receipt?,fees,en,agent\n"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(bom_content)

    rows, errors = read_csv_utf8_strict(str(csv_file))
    assert len(errors) == 0
    assert len(rows) == 1
    assert rows[0]["text"] == "Where is fee receipt?"
    assert rows[0]["intent"] == "fees"


def test_crisis_test_data_loader_guardrails(tmp_path):
    """Guardrail 10: crisis_test.csv loader requires exact text,lang header and UTF-8."""
    # 1. Valid file
    valid_file = tmp_path / "crisis_valid.csv"
    with open(valid_file, "w", encoding="utf-8") as f:
        f.write("text,lang\nI feel like giving up,en\n")
    c_rows, c_errs = load_crisis_test_data(str(valid_file))
    assert len(c_errs) == 0
    assert len(c_rows) == 1
    assert c_rows[0]["text"] == "I feel like giving up"

    # 2. Invalid header (e.g. text,intent,lang)
    bad_header_file = tmp_path / "crisis_bad_header.csv"
    with open(bad_header_file, "w", encoding="utf-8") as f:
        f.write("text,intent,lang\nI feel like giving up,distress_support,en\n")
    _, c_errs2 = load_crisis_test_data(str(bad_header_file))
    assert len(c_errs2) > 0
    assert any("contains disallowed column(s)" in err for err in c_errs2)

    # 3. Non-UTF-8 byte
    bad_byte_file = tmp_path / "crisis_bad_byte.csv"
    with open(bad_byte_file, "wb") as f:
        f.write(b"text,lang\nInvalid \xff byte,en\n")
    _, c_errs3 = load_crisis_test_data(str(bad_byte_file))
    assert len(c_errs3) > 0
    assert any("UTF-8 Encoding Error" in err for err in c_errs3)
