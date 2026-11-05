#!/usr/bin/env python3
"""
VIGBOT: Public Data Ingestion Pipeline (ml/add_public_data.py)

Builds data/public/public_extra.csv (text,intent,lang,author) from two CC BY 4.0 datasets:
1. CLINC150:
   - oos_train queries -> out_of_scope (lang: en, author: clinc150)
   - smalltalk intents (greeting, thank_you, goodbye) -> greeting_smalltalk (lang: en, author: clinc150)
2. MASSIVE (locales en-US, hi-IN, te-IN):
   - non-college scenarios (music, cooking, weather, takeaway, news, recommendation) -> out_of_scope
   - greeting items from general scenario (general_greet) -> greeting_smalltalk
   - lang: en, hi, te; author: massive

Enforces:
- Cap at 150 rows per intent and language (random_state=42).
- Authors clinc150 and massive are strictly confined to data/public/public_extra.csv.
- Public rows are for training only; they never count toward human quotas and never appear in test splits.
"""

import os
import sys
import csv
import json
import random
import tarfile
import argparse
import urllib.request
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Upstream sources
CLINC_URL = "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_full.json"
MASSIVE_URL = "https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.0.tar.gz"

CLINC_SMALLTALK_INTENTS = ["greeting", "thank_you", "goodbye"]
MASSIVE_NON_COLLEGE_SCENARIOS = ["music", "cooking", "weather", "takeaway", "news", "recommendation"]
MASSIVE_LOCALES = [("en-US", "en"), ("hi-IN", "hi"), ("te-IN", "te")]


def ensure_file_downloaded(url: str, dest_path: str, description: str) -> None:
    """Downloads a file if not already present in the local cache."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"  ✓ {description} cached at: {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return
    print(f"  Downloading {description} from {url}...")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    urllib.request.urlretrieve(url, dest_path)
    print(f"  ✓ Downloaded {description} ({os.path.getsize(dest_path)} bytes)")


def extract_clinc150_candidates(clinc_json_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[str]]:
    """
    Extracts out_of_scope and greeting_smalltalk candidates from CLINC150.
    Returns (oos_candidates, smalltalk_candidates, picked_intent_names).
    """
    with open(clinc_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    oos_candidates = []
    for item in data.get("oos_train", []):
        text = item[0].strip()
        if text:
            oos_candidates.append({
                "text": text,
                "intent": "out_of_scope",
                "lang": "en",
                "author": "clinc150",
            })

    smalltalk_candidates = []
    picked_intents = sorted(CLINC_SMALLTALK_INTENTS)
    for item in data.get("train", []):
        text = item[0].strip()
        orig_intent = item[1].strip()
        if orig_intent in CLINC_SMALLTALK_INTENTS and text:
            smalltalk_candidates.append({
                "text": text,
                "intent": "greeting_smalltalk",
                "lang": "en",
                "author": "clinc150",
            })

    return oos_candidates, smalltalk_candidates, picked_intents


def extract_massive_candidates(tar_gz_path: str) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """
    Extracts out_of_scope and greeting_smalltalk candidates from MASSIVE (locales en-US, hi-IN, te-IN).
    Only extracts from partition='train'.
    Returns structure: {lang: {'out_of_scope': [...], 'greeting_smalltalk': [...]}}
    """
    results: Dict[str, Dict[str, List[Dict[str, str]]]] = {
        "en": {"out_of_scope": [], "greeting_smalltalk": []},
        "hi": {"out_of_scope": [], "greeting_smalltalk": []},
        "te": {"out_of_scope": [], "greeting_smalltalk": []},
    }

    with tarfile.open(tar_gz_path, mode="r:gz") as tar:
        for loc, lang in MASSIVE_LOCALES:
            member_name = f"1.0/data/{loc}.jsonl"
            f = tar.extractfile(member_name)
            if not f:
                continue

            for line in f:
                record = json.loads(line.decode("utf-8"))
                if record.get("partition") != "train":
                    continue

                text = (record.get("utt") or "").strip()
                if not text:
                    continue

                scenario = record.get("scenario")
                intent = record.get("intent")

                if scenario in MASSIVE_NON_COLLEGE_SCENARIOS:
                    results[lang]["out_of_scope"].append({
                        "text": text,
                        "intent": "out_of_scope",
                        "lang": lang,
                        "author": "massive",
                    })
                elif scenario == "general" and intent == "general_greet":
                    results[lang]["greeting_smalltalk"].append({
                        "text": text,
                        "intent": "greeting_smalltalk",
                        "lang": lang,
                        "author": "massive",
                    })

    return results


def build_public_dataset(
    output_path: str = "data/public/public_extra.csv",
    cache_dir: str = "data/public/cache",
    cap_per_intent_lang: int = 150,
    seed: int = 42,
) -> List[Dict[str, str]]:
    """
    Builds data/public/public_extra.csv with balanced sampling and strict caps.
    """
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    clinc_path = os.path.join(cache_dir, "clinc_data_full.json")
    massive_path = os.path.join(cache_dir, "amazon-massive-dataset-1.0.tar.gz")

    print("\n" + "=" * 80)
    print("       VIGBOT: PUBLIC DATA INGESTION PIPELINE (CLINC150 + MASSIVE)")
    print("=" * 80)
    print("Ensuring upstream datasets are downloaded and cached...")
    ensure_file_downloaded(CLINC_URL, clinc_path, "CLINC150 dataset")
    ensure_file_downloaded(MASSIVE_URL, massive_path, "MASSIVE 1.0 dataset")

    # 1. CLINC150 Extraction
    print("\n--- Step 1: Extracting CLINC150 Queries (en) ---")
    clinc_oos, clinc_smalltalk, picked_clinc_intents = extract_clinc150_candidates(clinc_path)
    print(f"  • CLINC150 picked intent for out_of_scope: 'oos' (from oos_train)")
    print(f"  • CLINC150 picked intents for greeting_smalltalk: {picked_clinc_intents}")
    print(f"  • Extracted CLINC150 out_of_scope candidates: {len(clinc_oos)}")
    print(f"  • Extracted CLINC150 greeting_smalltalk candidates: {len(clinc_smalltalk)}")

    # 2. MASSIVE Extraction
    print("\n--- Step 2: Extracting MASSIVE Queries (en, hi, te) ---")
    massive_data = extract_massive_candidates(massive_path)
    print(f"  • Non-college scenarios used for out_of_scope: {MASSIVE_NON_COLLEGE_SCENARIOS}")
    print(f"  • General scenario items used for greeting_smalltalk: ['general_greet']")
    for lang in ["en", "hi", "te"]:
        oos_cnt = len(massive_data[lang]["out_of_scope"])
        greet_cnt = len(massive_data[lang]["greeting_smalltalk"])
        print(f"  • MASSIVE [{lang}]: out_of_scope={oos_cnt}, greeting_smalltalk={greet_cnt}")

    # 3. Balancing & Capping (cap=150 per intent and language, seed=42)
    print(f"\n--- Step 3: Capping at {cap_per_intent_lang} Rows per (Intent, Lang) with random_state={seed} ---")
    rng = random.Random(seed)
    final_rows: List[Dict[str, str]] = []

    # (a) out_of_scope, en: pool from clinc150 and massive
    # Balanced allocation: up to 75 from clinc150 and up to 75 from massive
    rng_clinc = random.Random(seed)
    rng_massive = random.Random(seed)

    clinc_oos_sample = rng_clinc.sample(clinc_oos, min(75, len(clinc_oos)))
    massive_oos_en = massive_data["en"]["out_of_scope"]
    massive_oos_sample = rng_massive.sample(massive_oos_en, min(cap_per_intent_lang - len(clinc_oos_sample), len(massive_oos_en)))
    oos_en_combined = clinc_oos_sample + massive_oos_sample
    final_rows.extend(oos_en_combined)
    print(f"  • (out_of_scope, en)      : {len(oos_en_combined)} rows ({len(clinc_oos_sample)} clinc150 + {len(massive_oos_sample)} massive)")

    # (b) greeting_smalltalk, en: pool from massive (25) and clinc150 (up to 125)
    massive_greet_en = massive_data["en"]["greeting_smalltalk"]
    needed_from_clinc = min(len(clinc_smalltalk), cap_per_intent_lang - len(massive_greet_en))
    clinc_greet_sample = rng_clinc.sample(clinc_smalltalk, needed_from_clinc)
    greet_en_combined = massive_greet_en + clinc_greet_sample
    final_rows.extend(greet_en_combined)
    print(f"  • (greeting_smalltalk, en): {len(greet_en_combined)} rows ({len(clinc_greet_sample)} clinc150 + {len(massive_greet_en)} massive)")

    # (c) out_of_scope, hi: massive only
    massive_oos_hi = massive_data["hi"]["out_of_scope"]
    oos_hi_sample = rng_massive.sample(massive_oos_hi, min(cap_per_intent_lang, len(massive_oos_hi)))
    final_rows.extend(oos_hi_sample)
    print(f"  • (out_of_scope, hi)      : {len(oos_hi_sample)} rows (massive)")

    # (d) greeting_smalltalk, hi: massive only
    massive_greet_hi = massive_data["hi"]["greeting_smalltalk"]
    final_rows.extend(massive_greet_hi)
    print(f"  • (greeting_smalltalk, hi): {len(massive_greet_hi)} rows (massive)")

    # (e) out_of_scope, te: massive only
    massive_oos_te = massive_data["te"]["out_of_scope"]
    oos_te_sample = rng_massive.sample(massive_oos_te, min(cap_per_intent_lang, len(massive_oos_te)))
    final_rows.extend(oos_te_sample)
    print(f"  • (out_of_scope, te)      : {len(oos_te_sample)} rows (massive)")

    # (f) greeting_smalltalk, te: massive only
    massive_greet_te = massive_data["te"]["greeting_smalltalk"]
    final_rows.extend(massive_greet_te)
    print(f"  • (greeting_smalltalk, te): {len(massive_greet_te)} rows (massive)")

    # 4. Save to CSV (text,intent,lang,author)
    print(f"\n--- Step 4: Writing {len(final_rows)} Rows to {output_path} ---")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "intent", "lang", "author"])
        writer.writeheader()
        for r in final_rows:
            writer.writerow({
                "text": r["text"],
                "intent": r["intent"],
                "lang": r["lang"],
                "author": r["author"],
            })

    print(f"  ✓ Successfully wrote: {os.path.abspath(output_path)}")

    # 5. Summary Statistics
    summary = Counter((r["intent"], r["lang"], r["author"]) for r in final_rows)
    print("\n" + "-" * 80)
    print(f"{'Intent':<22} | {'Lang':<6} | {'Author':<10} | {'Count':<6}")
    print("-" * 80)
    for (intent, lang, author), count in sorted(summary.items()):
        print(f"{intent:<22} | {lang:<6} | {author:<10} | {count:<6}")
    print("-" * 80)
    print(f"Total Public Training Rows: {len(final_rows)}")
    print("=" * 80 + "\n")

    return final_rows


def main():
    parser = argparse.ArgumentParser(description="Ingest public data from CLINC150 and MASSIVE.")
    parser.add_argument("--output", default="data/public/public_extra.csv", help="Target output CSV path")
    parser.add_argument("--cache-dir", default="data/public/cache", help="Cache directory for downloads")
    parser.add_argument("--cap", type=int, default=150, help="Max rows per (intent, lang) slice (default: 150)")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed (default: 42)")
    args = parser.parse_args()

    build_public_dataset(
        output_path=args.output,
        cache_dir=args.cache_dir,
        cap_per_intent_lang=args.cap,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()

