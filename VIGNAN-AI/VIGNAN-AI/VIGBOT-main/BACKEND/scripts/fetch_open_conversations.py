#!/usr/bin/env python3
"""
Open Conversational Dataset Downloader & Blender: The General Knowledge Food.
Downloads high-quality conversational dialogues from Hugging Face Datasets (UltraChat 200k / SlimOrca / Dolly)
and converts them to Llama 3 / ChatML format without requiring an API key.
"""

import json
import os
import sys
import importlib

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def download_and_sample_ultrachat(sample_size: int = 200):
    """
    Pulls a curated slice of UltraChat-200k (multi-turn, ChatGPT-quality conversational data)
    from Hugging Face using streaming so it doesn't download the entire 1GB file.
    """
    # Dynamic import avoids static linter / Pyrefly warnings if interpreter path changes
    try:
        datasets_pkg = importlib.import_module("datasets")
        load_dataset = getattr(datasets_pkg, "load_dataset")
    except ImportError:
        print("[!] 'datasets' package is not installed in the active environment.")
        print("[!] Install via: pip install datasets")
        print("[!] Using local domain dataset in backend/data/train_data.jsonl.")
        return

    print(f"[*] Streaming {sample_size} high-quality multi-turn conversations from HuggingFaceH4/ultrachat_200k...")
    try:
        dataset = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft", streaming=True)
        samples = []
        for i, item in enumerate(dataset):
            if i >= sample_size:
                break
            messages = item.get("messages", [])
            if messages:
                samples.append({"messages": messages})

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_file = os.path.join(OUTPUT_DIR, "ultrachat_sample.jsonl")
        with open(out_file, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
                
        print(f"[+] Successfully saved {len(samples)} UltraChat dialogues to {out_file}")
    except Exception as e:
        print(f"[!] Network or streaming error: {e}")
        print("[!] You can proceed directly with backend/data/train_data.jsonl.")

if __name__ == "__main__":
    download_and_sample_ultrachat(sample_size=100)
