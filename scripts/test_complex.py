#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run complex qualitative prompts across multiple checkpoints and log outputs."""
from transformers import AutoModelForCausalLM, AutoTokenizer
from datetime import datetime
from pathlib import Path
from typing import Optional
from peft import PeftModel
import torch
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MODEL = "F:/Node/hivellm/expert/models/Qwen3-0.6B"

BASE_DIR = Path(__file__).resolve().parent
EXPERT_ROOT = BASE_DIR.parent
LOG_DIR = EXPERT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"test_complex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

CHECKPOINTS = [
    {"name": "base", "path": None},
    {"name": "checkpoint-250", "path": "weights/qwen3-06b/checkpoint-250"},
    {"name": "checkpoint-500", "path": "weights/qwen3-06b/checkpoint-500"},
    {"name": "checkpoint-638", "path": "weights/qwen3-06b/checkpoint-638"},
    {"name": "final", "path": "weights/qwen3-06b/final"},
]

# Testes mais desafiadores
COMPLEX_TESTS = [
    {
        "name": "Deeply Nested Schema",
        "prompt": "Create JSON schema for: user with profile object containing settings object with preferences object containing theme (string) and language (string)",
    },
    {
        "name": "Multiple Syntax Errors",
        "prompt": 'Fix this JSON: {name: "John", "age": 30, "tags": ["dev" "designer",]}',
    },
    {
        "name": "Complex API Response Schema",
        "prompt": "Create JSON schema for: API response with status (number), message (string), data object, errors array of objects, and meta object with pagination",
    },
    {
        "name": "JSON Repair - Trailing Comma in Object",
        "prompt": 'Fix JSON: {"id": 123, "active": true,}',
    },
    {
        "name": "JSON Repair - Trailing Comma in Array",
        "prompt": 'Fix JSON: ["apple", "banana", "orange",]',
    },
    {
        "name": "JSON Repair - Single Quotes",
        "prompt": "Fix JSON: {'name': 'John', 'age': 30}",
    },
    {
        "name": "JSON Schema with Arrays",
        "prompt": "Create JSON schema for: blog post with title (string), content (string), tags (array of strings), and comments (array of objects with author and text)",
    },
    {
        "name": "JSON Transform Request",
        "prompt": 'Transform this flat JSON to nested: {"user_name": "Alice", "user_email": "alice@example.com", "user_age": 25}',
    },
    {
        "name": "OpenAPI Request Schema",
        "prompt": "Create JSON schema for: POST /api/users request body with username (string, required), email (string, required), age (number, optional), and role (enum: admin, user, guest)",
    },
    {
        "name": "CloudEvents Schema",
        "prompt": "Create JSON schema for: CloudEvents event with id (string), source (string), type (string), datacontenttype (string), and data (object)",
    },
    {
        "name": "JSON Repair - Unquoted Keys",
        "prompt": 'Fix JSON: {id: 1, name: "Product", active: true}',
    },
    {
        "name": "Complex Nested Object",
        "prompt": 'Create JSON: e-commerce order with id, customer object (name, email, address object with street, city, zip), items array of products (id, name, price, quantity), and totals object (subtotal, tax, shipping, total)',
    },
    {
        "name": "JSON Schema with Validation Rules",
        "prompt": "Create JSON schema for: user with email (string, format: email), age (number, minimum: 0, maximum: 150), and password (string, minLength: 8)",
    },
    {
        "name": "Pagination Response",
        "prompt": 'Create JSON: pagination response with page (1), per_page (20), total (100), total_pages (5), and data array with 3 user objects (id, name, email)',
    },
    {
        "name": "Error Response Schema",
        "prompt": "Create JSON schema for: error response with code (number), message (string), details array of objects with field and error properties, and timestamp (string)",
    },
]
def load_model(adapter_relative: Optional[str]):
    tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL,
        dtype=torch.bfloat16,
        device_map="cuda",
        trust_remote_code=True,
    )

    if adapter_relative:
        adapter_path = EXPERT_ROOT / adapter_relative
        if not adapter_path.exists():
            raise FileNotFoundError(f"Adapter path not found: {adapter_path}")
        model = PeftModel.from_pretrained(model, adapter_path)

    return tokenizer, model


def run_tests_for_checkpoint(checkpoint_name: str, adapter_relative: Optional[str]):
    print(f"\n{'=' * 70}\nRunning tests for: {checkpoint_name}\n{'=' * 70}")

    tok, mod = load_model(adapter_relative)
    checkpoint_results = []

    for idx, test in enumerate(COMPLEX_TESTS, 1):
        prompt = (
            "<|system|>\nYou are a JSON expert. Output only valid JSON.\n<|end|>\n"
            f"<|user|>\n{test['prompt']}\n<|end|>\n<|assistant|>\n"
        )
        inp = tok(prompt, return_tensors="pt").to("cuda")

        with torch.no_grad():
            out = mod.generate(
                **inp,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                pad_token_id=tok.eos_token_id,
            )

        res = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True).strip()

        if "<|end|>" in res:
            res = res.split("<|end|>")[0].strip()

        record = {
            "checkpoint": checkpoint_name,
            "adapter_path": adapter_relative,
            "test_index": idx,
            "test_name": test["name"],
            "prompt": test["prompt"],
            "output_raw": res,
            "output_length": len(res),
        }
        checkpoint_results.append(record)

        with LOG_FILE.open("a", encoding="utf-8") as logf:
            logf.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"[{checkpoint_name}] Test {idx}/{len(COMPLEX_TESTS)}: {test['name']}")
        print("Prompt:")
        print(test["prompt"])
        print("\nOutput:")
        print(res)
        print("-" * 60)

    del mod, tok
    torch.cuda.empty_cache()

    return checkpoint_results


def main():
    print(f"Logging outputs to: {LOG_FILE}")
    all_results = []
    for checkpoint in CHECKPOINTS:
        results = run_tests_for_checkpoint(checkpoint["name"], checkpoint["path"])
        all_results.extend(results)

    print(f"\nCompleted {len(all_results)} test cases across {len(CHECKPOINTS)} checkpoints.")
    print(f"Results written to: {LOG_FILE}")


if __name__ == "__main__":
    main()

