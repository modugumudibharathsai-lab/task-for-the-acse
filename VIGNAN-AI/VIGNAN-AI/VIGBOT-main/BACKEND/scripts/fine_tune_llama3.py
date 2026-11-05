#!/usr/bin/env python3
"""
VIGBOT Fine-Tuning Script: The Stove & Recipe.
Fine-tunes Llama-3.2-3B-Instruct (or Mistral-7B) using QLoRA (4-bit LoRA) with Hugging Face TRL & PEFT.
Produces a domain-adapted conversational model tailored for university student advisory.

Requirements:
    pip install torch transformers peft trl bitsandbytes accelerate datasets
"""

import os
import sys
import argparse

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune Llama 3.1 8B / 3.2 3B for VIGBOT")
    parser.add_argument(
        "--model_name",
        type=str,
        default="meta-llama/Meta-Llama-3.1-8B-Instruct",
        help="Base model to fine-tune (e.g. meta-llama/Meta-Llama-3.1-8B-Instruct or meta-llama/Llama-3.2-3B-Instruct)"
    )
    clean_dir = os.path.join(os.path.dirname(__file__), "..", "data", "clean_vigbot")
    default_train = os.path.join(clean_dir, "train_data.jsonl") if os.path.exists(clean_dir) else os.path.join(os.path.dirname(__file__), "..", "data", "train_data.jsonl")
    default_val = os.path.join(clean_dir, "val_data.jsonl") if os.path.exists(clean_dir) else os.path.join(os.path.dirname(__file__), "..", "data", "val_data.jsonl")

    parser.add_argument(
        "--data_path",
        type=str,
        default=default_train,
        help="Path to training data in JSONL format"
    )
    parser.add_argument(
        "--val_path",
        type=str,
        default=default_val,
        help="Path to validation data in JSONL format"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./vigbot_lora",
        help="Directory to save the fine-tuned LoRA adapter"
    )
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per device batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--max_seq_length", type=int, default=1024, help="Maximum sequence length")
    return parser.parse_args()

def main():
    args = parse_args()

    print("=" * 70)
    print("  VIGBOT: FINE-TUNING LLAMA 3.2 (3B) / MISTRAL (7B) VIA QLORA")
    print("=" * 70)
    print(f"[*] Base Model:       {args.model_name}")
    print(f"[*] Training Data:    {args.data_path}")
    print(f"[*] Output Adapter:   {args.output_dir}")
    print(f"[*] Epochs:           {args.epochs}")
    print(f"[*] Batch Size:       {args.batch_size} (Grad Accum: {args.grad_accum})")
    print(f"[*] Learning Rate:    {args.learning_rate}")
    print("=" * 70)

    try:
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        from datasets import load_dataset
    except ImportError as e:
        print(f"\n[!] Missing dependency: {e}")
        print("Please install training dependencies:")
        print("    pip install torch transformers peft trl bitsandbytes accelerate datasets")
        print("\nNote: Fine-tuning requires an Nvidia GPU (CUDA). For free GPU training, use the provided")
        print("Google Colab notebook: backend/scripts/train_vigbot.ipynb")
        return

    # Check CUDA availability
    if not torch.cuda.is_available():
        print("\n[!] WARNING: CUDA is not available. Fine-tuning on CPU is prohibitively slow.")
        print("[!] For fast, free training (< 25 min), run `train_vigbot.ipynb` on Google Colab (Free T4 GPU).")
        response = input("Do you wish to continue on CPU anyway? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    # 1. 4-bit Quantization Config (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=True
    )

    # 2. Load Tokenizer & Model
    print("\n[*] Loading tokenizer and base model in 4-bit precision...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config if torch.cuda.is_available() else None,
        device_map="auto" if torch.cuda.is_available() else "cpu",
        trust_remote_code=True
    )

    model = prepare_model_for_kbit_training(model)

    # 3. LoRA Configuration (Target all projection layers)
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ]
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Ingest Dataset
    print(f"\n[*] Ingesting datasets...")
    print(f"    Train: {args.data_path}")
    print(f"    Val:   {args.val_path}")
    data_files = {
        "train": args.data_path,
        "validation": args.val_path,
    }
    dataset = load_dataset("json", data_files=data_files)

    def format_conversation(example):
        messages = example.get("messages", [])
        return {
            "text": tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
        }

    dataset = dataset.map(format_conversation)

    # 5. Training Arguments
    training_kwargs = {
        "output_dir": args.output_dir,
        "num_train_epochs": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "gradient_accumulation_steps": args.grad_accum,
        "optim": "paged_adamw_8bit" if torch.cuda.is_available() else "adamw_torch",
        "save_strategy": "epoch",
        "load_best_model_at_end": True,
        "metric_for_best_model": "eval_loss",
        "logging_steps": 10,
        "learning_rate": args.learning_rate,
        "weight_decay": 0.01,
        "fp16": (compute_dtype == torch.float16 and torch.cuda.is_available()),
        "bf16": (compute_dtype == torch.bfloat16 and torch.cuda.is_available()),
        "max_grad_norm": 0.3,
        "warmup_ratio": 0.05,
        "lr_scheduler_type": "cosine",
        "report_to": "none"
    }

    # Handle evaluation_strategy vs eval_strategy for transformers version compatibility
    import inspect
    sig = inspect.signature(TrainingArguments.__init__)
    if "eval_strategy" in sig.parameters:
        training_kwargs["eval_strategy"] = "epoch"
    else:
        training_kwargs["evaluation_strategy"] = "epoch"

    training_args = TrainingArguments(**training_kwargs)

    # 6. SFTTrainer (model is already wrapped via get_peft_model, so peft_config is omitted here)
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=None,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args
    )

    print("\n🚀 Starting QLoRA Training...")
    trainer.train()

    print(f"\n✅ Training Complete! Saving LoRA adapter to {args.output_dir}...")
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print("\n" + "=" * 70)
    print("  NEXT STEPS FOR LOCAL OLLAMA DEPLOYMENT:")
    print("  1. Merge LoRA weights into base model (or export directly to GGUF)")
    print("  2. Create Ollama model: ollama create vigbot -f backend/models/Modelfile.vigbot")
    print("=" * 70)

if __name__ == "__main__":
    main()
