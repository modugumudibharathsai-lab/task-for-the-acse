#!/usr/bin/env python3
"""Validate VIGBOT JSONL data before fine-tuning.

This is a read-only check: it never rewrites the input files.
"""

import argparse
import json
import re
import sys
from pathlib import Path

FRACTION_PATTERN = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")
CURRENT_PERCENT_PATTERN = re.compile(
    r"current\s+attendance[^\d]{0,80}(\d+(?:\.\d+)?)\s*%",
    re.IGNORECASE,
)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_number}: invalid JSON ({exc.msg})")
                continue

            messages = record.get("messages")
            if not isinstance(messages, list) or len(messages) < 2:
                errors.append(f"{path}:{line_number}: messages must contain at least two turns")
                continue

            for index, message in enumerate(messages):
                if message.get("role") not in {"system", "user", "assistant"}:
                    errors.append(f"{path}:{line_number}: invalid role at message {index}")
                if not isinstance(message.get("content"), str) or not message["content"].strip():
                    errors.append(f"{path}:{line_number}: empty content at message {index}")

                content = message.get("content", "")
                current_match = CURRENT_PERCENT_PATTERN.search(content)
                current_percentages = (
                    [float(current_match.group(1))] if current_match else []
                )
                fractions = FRACTION_PATTERN.finditer(
                    content[:current_match.start()] if current_match else content
                )
                for fraction_match in fractions:
                    numerator, denominator = fraction_match.groups()
                    denominator_value = int(denominator)
                    if denominator_value == 0:
                        errors.append(f"{path}:{line_number}: zero denominator in {numerator}/{denominator}")
                        continue
                    fraction_value = int(numerator) / denominator_value * 100
                    if current_percentages and all(
                        abs(fraction_value - value) > 0.6 for value in current_percentages
                    ):
                        errors.append(
                            f"{path}:{line_number}: {numerator}/{denominator} equals "
                            f"{fraction_value:.1f}%, conflicting with listed percentage(s) "
                            f"{', '.join(str(value) for value in current_percentages)}"
                        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VIGBOT JSONL training data")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    for path in args.paths:
        if not path.is_file():
            errors.append(f"{path}: file does not exist")
            continue
        errors.extend(validate_file(path))

    if errors:
        print("Training data validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Training data validation passed for {len(args.paths)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
