#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create enhanced dataset with improved JSON Schema and Repair examples
Combines existing dataset with new synthetic examples
"""

import json
import os
import sys
import io

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_jsonl(path):
    """Load JSONL file, skipping empty lines"""
    examples = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        examples.append(json.loads(line))
                    except:
                        pass  # Skip malformed lines
    return examples

def save_jsonl(path, examples):
    """Save to JSONL"""
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print("Loading existing datasets...")

# Load current COMPLETE dataset (all splits combined)
train_all = load_jsonl("../datasets/train.jsonl")

print(f"Current complete dataset: {len(train_all)} examples")

# Load all new datasets (ChatML normalized versions)
schema_all = (load_jsonl("../datasets/text_to_schema/train_chatml.jsonl") + 
              load_jsonl("../datasets/text_to_schema/valid_chatml.jsonl") + 
              load_jsonl("../datasets/text_to_schema/test_chatml.jsonl"))

repair_all = (load_jsonl("../datasets/json_repair_enhanced/train_chatml.jsonl") + 
              load_jsonl("../datasets/json_repair_enhanced/valid_chatml.jsonl") + 
              load_jsonl("../datasets/json_repair_enhanced/test_chatml.jsonl"))

ms_all = (load_jsonl("../datasets/microsoft_text_to_schema/train_chatml.jsonl") + 
          load_jsonl("../datasets/microsoft_text_to_schema/valid_chatml.jsonl") + 
          load_jsonl("../datasets/microsoft_text_to_schema/test_chatml.jsonl"))

print(f"Synthetic text_to_schema: {len(schema_all)} examples")
print(f"Microsoft schemas (REAL): {len(ms_all)} examples")
print(f"Enhanced json_repair: {len(repair_all)} examples")

# Combine ALL examples
enhanced_all = train_all + schema_all + ms_all + repair_all

total_added = len(schema_all) + len(ms_all) + len(repair_all)
print(f"\nEnhanced dataset: {len(enhanced_all)} total examples (+{total_added})")

# Split into train/val/test (80/10/10)
import random
random.shuffle(enhanced_all)

split_1 = int(len(enhanced_all) * 0.8)
split_2 = int(len(enhanced_all) * 0.9)

enhanced_train = enhanced_all[:split_1]
enhanced_val = enhanced_all[split_1:split_2]
enhanced_test = enhanced_all[split_2:]

print(f"Splits: Train={len(enhanced_train)}, Val={len(enhanced_val)}, Test={len(enhanced_test)}")

# Backup original
import shutil
os.makedirs("../datasets/backup_v0.1.0", exist_ok=True)
if os.path.exists("../datasets/train.jsonl"):
    shutil.copy("../datasets/train.jsonl", "../datasets/backup_v0.1.0/train.jsonl")
    print("Backed up original train.jsonl")

# Save to root (overwrite)
save_jsonl("../datasets/train.jsonl", enhanced_train)
save_jsonl("../datasets/validation.jsonl", enhanced_val)
save_jsonl("../datasets/test.jsonl", enhanced_test)

# Create metadata
metadata = {
    "name": "expert-json-enhanced",
    "version": "0.2.0",
    "base_examples": len(train_all),
    "schema_synthetic_added": len(schema_all),
    "schema_microsoft_added": len(ms_all),
    "repair_examples_added": len(repair_all),
    "total_train": len(enhanced_train),
    "total_val": len(enhanced_val),
    "total_test": len(enhanced_test),
    "total_all": len(enhanced_all),
    "improvements": [
        f"Added synthetic text to JSON Schema ({len(schema_all)} examples)",
        f"Added Microsoft real JSON Schemas ({len(ms_all)} examples from production)",
        f"Enhanced JSON repair with syntax fixes ({len(repair_all)} examples)"
    ],
    "sources": [
        "apis.guru (OpenAPI specs)",
        "schemastore.org (JSON Schemas)",
        "cloudevents (CNCF events)",
        "paraloq (text-to-json)",
        "mastercontrol (document extraction)",
        "microsoft/json-schemas (REAL production schemas)",
        "synthetic text-to-schema",
        "synthetic json-repair-enhanced"
    ]
}

with open("../datasets/enhanced_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("\nDataset saved to: datasets/ (root)")
print(json.dumps(metadata, indent=2, ensure_ascii=False))

print("\nDataset ready for training!")
print("Run: expert-cli train --manifest manifest.json")

