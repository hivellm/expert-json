#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalize all new datasets to ChatML format with 'text' field
Ensures compatibility with HuggingFace datasets loader
"""

import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_jsonl(path):
    examples = []
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        examples.append(json.loads(line))
                    except:
                        pass
    return examples

def save_jsonl(path, examples):
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

def convert_text_to_schema(example):
    """Convert text_to_schema format to ChatML"""
    instruction = example["input"]["instruction"]
    description = example["input"]["description"]
    schema_output = example["output"]
    
    chatml = (
        f"<|system|>\nTask: schema_generation\nFormat: json_schema\n<|end|>\n"
        f"<|user|>\n{description}\n<|end|>\n"
        f"<|assistant|>\n{schema_output}\n<|end|>"
    )
    
    return {"text": chatml}

def convert_json_repair(example):
    """Convert json_repair format to ChatML"""
    instruction = example["input"]["instruction"]
    broken_json = example["input"]["broken_json"]
    fixed_json = example["output"]
    error_type = example["input"].get("error_type", "syntax_error")
    
    chatml = (
        f"<|system|>\nTask: json_correction\nFormat: generic\nError type: {error_type}\n<|end|>\n"
        f"<|user|>\nFix this invalid JSON:\n{broken_json}\n<|end|>\n"
        f"<|assistant|>\n{fixed_json}\n<|end|>"
    )
    
    return {"text": chatml}

# Process text_to_schema (synthetic)
print("Converting text_to_schema...")
for split in ["train", "valid", "test"]:
    examples = load_jsonl(f"../datasets/text_to_schema/{split}.jsonl")
    converted = [convert_text_to_schema(ex) for ex in examples]
    save_jsonl(f"../datasets/text_to_schema/{split}_chatml.jsonl", converted)
    print(f"  {split}: {len(converted)} examples")

# Process microsoft_text_to_schema (REAL)
print("\nConverting microsoft_text_to_schema...")
for split in ["train", "valid", "test"]:
    examples = load_jsonl(f"../datasets/microsoft_text_to_schema/{split}.jsonl")
    converted = [convert_text_to_schema(ex) for ex in examples]
    save_jsonl(f"../datasets/microsoft_text_to_schema/{split}_chatml.jsonl", converted)
    print(f"  {split}: {len(converted)} examples")

# Process json_repair_enhanced
print("\nConverting json_repair_enhanced...")
for split in ["train", "valid", "test"]:
    examples = load_jsonl(f"../datasets/json_repair_enhanced/{split}.jsonl")
    converted = [convert_json_repair(ex) for ex in examples]
    save_jsonl(f"../datasets/json_repair_enhanced/{split}_chatml.jsonl", converted)
    print(f"  {split}: {len(converted)} examples")

print("\n✅ All datasets normalized to ChatML format")
print("Now run create_enhanced_dataset.py to combine them")

