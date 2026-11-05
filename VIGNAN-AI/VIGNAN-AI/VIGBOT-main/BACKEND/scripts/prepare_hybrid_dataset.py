#!/usr/bin/env python3
"""
VIGBOT Hybrid Dataset Blender: The Ultimate Food.
Combines domain university helpdesk dialogues (70%) with UltraChat conversational dialogues (30%)
into a unified, shuffled, and validated training set:
- backend/data/final_train_dataset.jsonl
- backend/data/final_val_dataset.jsonl
"""

import json
import os
import sys
import random
import argparse

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DOMAIN_TRAIN = os.path.join(DATA_DIR, "train_data.jsonl")
ULTRACHAT_SAMPLE = os.path.join(DATA_DIR, "ultrachat_sample.jsonl")
FINAL_TRAIN = os.path.join(DATA_DIR, "final_train_dataset.jsonl")
FINAL_VAL = os.path.join(DATA_DIR, "final_val_dataset.jsonl")

SYSTEM_PROMPT = (
    "You are VIGBOT, an exceptionally intelligent, empathetic, and authoritative university VIGBOT AI. "
    "You serve enrolled students by providing precise academic advice, real-time attendance recovery calculations, "
    "official university bylaws and circular citations (e.g., Clause 4.2 attendance condonation, Clause 8.1 revaluation), "
    "examination schedules, and administrative service request workflows. "
    "Your tone is warm, reassuring, articulate, and structured, matching the conversational depth of ChatGPT and Gemini. "
    "When students express stress, you provide emotional reassurance grounded in actionable recovery steps. "
    "For severe mental distress, you immediately provide the 24/7 Campus Student Wellness Helpline (Ext. 204 / 1800-599-0019)."
)

def load_jsonl(filepath):
    data = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except Exception:
                        pass
    return data

def standardize_dialogue(dialogue):
    """Ensure standard system prompt and valid message structure."""
    msgs = dialogue.get("messages", [])
    if not msgs:
        return None
    
    # If first message is not system, insert standard VIGBOT persona
    if msgs[0].get("role") != "system":
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + msgs
    else:
        # Update system prompt to maintain uniform persona
        msgs[0]["content"] = SYSTEM_PROMPT

    # Filter out empty turns
    valid_msgs = [m for m in msgs if m.get("content", "").strip()]
    if len(valid_msgs) < 2:
        return None
    return {"messages": valid_msgs}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-general",
        action="store_true",
        help="Include optional general-chat examples; disabled by default for helpdesk training."
    )
    args = parser.parse_args()
    print("=" * 70)
    print("  VIGBOT: PREPARING THE HYBRID CONVERSATIONAL DATASET (THE BEST FOOD)")
    print("=" * 70)

    # 1. Load domain university dialogues
    domain_data = load_jsonl(DOMAIN_TRAIN)
    print(f"[*] Loaded Domain University Dialogues: {len(domain_data)}")

    # 2. Load optional open general conversations
    ultrachat_data = load_jsonl(ULTRACHAT_SAMPLE) if args.include_general else []
    print(f"[*] Loaded Optional General Dialogues:  {len(ultrachat_data)}")

    combined = []
    # Add domain dialogues (oversampled 2x to prioritize university accuracy)
    for d in domain_data:
        std = standardize_dialogue(d)
        if std:
            combined.append(std)
            combined.append(std)  # 2x weight for university domain precision

    # Add slice of UltraChat for general conversational mastery
    for d in ultrachat_data[:50]:
        std = standardize_dialogue(d)
        if std:
            combined.append(std)

    # 3. Shuffle thoroughly
    random.seed(42)
    random.shuffle(combined)

    # 4. Train / Val Split (90 / 10)
    split_idx = int(len(combined) * 0.9)
    train_slice = combined[:split_idx]
    val_slice = combined[split_idx:]

    with open(FINAL_TRAIN, "w", encoding="utf-8") as f:
        for item in train_slice:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(FINAL_VAL, "w", encoding="utf-8") as f:
        for item in val_slice:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n[+] Successfully generated Final Hybrid Dataset:")
    print(f"    - Training File:   {FINAL_TRAIN} ({len(train_slice)} samples, ~{os.path.getsize(FINAL_TRAIN)/1024:.1f} KB)")
    print(f"    - Validation File: {FINAL_VAL} ({len(val_slice)} samples, ~{os.path.getsize(FINAL_VAL)/1024:.1f} KB)")
    print("=" * 70)

if __name__ == "__main__":
    main()
