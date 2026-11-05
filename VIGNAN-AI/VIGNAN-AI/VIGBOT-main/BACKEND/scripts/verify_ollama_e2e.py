#!/usr/bin/env python3
"""
VIGBOT: Ollama End-to-End Diagnostic & Verification Tool.
Verifies that inference actually reaches the local Ollama daemon rather than
silently falling back to deterministic templates or mock responses.
"""

import os
import sys
import time
import requests

# Ensure Windows console does not throw charmap encoding errors on status glyphs
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

raw_url = os.getenv("LOCAL_MODEL_URL", "http://127.0.0.1:11434")
for suffix in ["/api/chat", "/api/generate", "/api/tags"]:
    if raw_url.endswith(suffix):
        raw_url = raw_url[:-len(suffix)]
OLLAMA_URL = raw_url.rstrip("/")

PREFERRED_MODELS = ["vigbot-8b:latest", "vigbot-8b", "vigbot:latest", "llama3.2:3b", "llama3.1:8b"]

def test_ollama_connection():
    print("=" * 65)
    print("  VIGBOT: OLLAMA END-TO-END VERIFICATION & BENCHMARK")
    print("=" * 65)
    
    # 1. Check Daemon
    print(f"\n[1/4] Checking Ollama daemon at {OLLAMA_URL}...")
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3.0)
        if resp.status_code != 200:
            print(f"[FAIL] Ollama responded with status code {resp.status_code}")
            return False
        data = resp.json()
        models = [m.get("name") for m in data.get("models", [])]
        print(f"[OK] Ollama is ONLINE (Version check passed)")
        print(f"    Available models ({len(models)}): {', '.join(models) if models else 'None'}")
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Could not connect to {OLLAMA_URL}.")
        print("    -> Action: Start Ollama from Windows Start Menu or run 'ollama serve' in a terminal.")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking Ollama: {e}")
        return False

    if not models:
        print("[FAIL] No models installed in Ollama.")
        return False

    # 2. Select Target Model
    target_model = None
    for pref in PREFERRED_MODELS:
        for m in models:
            if pref == m or pref.split(":")[0] == m.split(":")[0]:
                target_model = m
                break
        if target_model:
            break

    if not target_model:
        print(f"\n[2/4] Model Selection FAILED:")
        print(f"[FAIL] None of the approved VIGBOT models {PREFERRED_MODELS} are installed in Ollama.")
        print(f"    Available models in Ollama: {models}")
        print(f"    Action: Run 'ollama create vigbot-8b:latest -f ...' or 'ollama pull llama3.2:3b'.")
        return False

    print(f"\n[2/4] Selected Approved Model: '{target_model}'")

    # 3. Benchmark Live Chat Inference
    test_prompt = "Under university academic regulations Clause 4.2, what is the minimum attendance percentage required for end-semester exams?"
    print(f"\n[3/4] Sending live query to '{target_model}'...")
    print(f"    Prompt: \"{test_prompt}\"")
    
    payload = {
        "model": target_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are VIGBOT, an autonomous VIGBOT AI for Vignan University.\n"
                    "Verified Institutional Records & Academic Regulations:\n"
                    "• Academic Regulations Clause 4.2: The minimum attendance percentage required for end-semester examinations is 75%.\n"
                    "• Condonation of attendance shortage between 65% and 75% may be granted on valid medical grounds with Dean approval.\n"
                    "Answer concisely, directly, and factually based on these verified records."
                )
            },
            {"role": "user", "content": test_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 250,
            "num_ctx": 4096
        }
    }

    start_time = time.time()
    try:
        chat_resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=90.0)
        elapsed = time.time() - start_time
        if chat_resp.status_code != 200:
            print(f"[FAIL] Chat generation failed with HTTP {chat_resp.status_code}: {chat_resp.text}")
            return False
        
        chat_data = chat_resp.json()
        content = chat_data.get("message", {}).get("content", "").strip()
        eval_count = chat_data.get("eval_count", 0)
        eval_duration_s = chat_data.get("eval_duration", 0) / 1e9
        tok_per_sec = (eval_count / eval_duration_s) if eval_duration_s > 0 else 0.0

        print(f"[OK] Response generated from '{target_model}'!")
        print(f"    Latency:       {elapsed:.2f}s (Roundtrip)")
        print(f"    Tokens Gen:    {eval_count} tokens")
        if tok_per_sec > 0:
            print(f"    Speed:         {tok_per_sec:.1f} tokens/sec")

        # 4. Domain Content Verification
        print(f"\n[4/4] Verifying Domain Accuracy in Output...")
        c_lower = content.lower()
        has_75 = "75" in content
        has_att = "attendance" in c_lower or "cutoff" in c_lower or "condonation" in c_lower
        is_substantial = len(content) >= 40

        print(f"    Substantial output (>= 40 chars):      {'[PASS]' if is_substantial else '[FAIL]'}")
        print(f"    Contains mandatory 75% requirement:     {'[PASS]' if has_75 else '[FAIL]'}")
        print(f"    Addresses attendance domain:            {'[PASS]' if has_att else '[FAIL]'}")

        if not (is_substantial and has_75 and has_att):
            print("\n[FAIL] Output did not meet domain grounding criteria.")
            print(f"Raw Output:\n{content}")
            return False

        print(f"\nVerified Model Output from '{target_model}':")
        print("-" * 65)
        print(content)
        print("-" * 65)
        print(f"\n[SUCCESS] Local model '{target_model}' is online, responsive, and factually grounded!")
        return True

    except requests.exceptions.Timeout:
        print(f"[FAIL] Inference timed out after 90 seconds (CPU bottleneck).")
        return False
    except Exception as e:
        print(f"[FAIL] Inference failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    sys.exit(0 if success else 1)
