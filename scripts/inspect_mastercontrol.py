#!/usr/bin/env python3
"""
Deep inspection of MasterControlAIML/JSON-Unstructured-Structured
10,000 examples - seems promising!
"""

import json
from datasets import load_dataset

print("="*70)
print("DEEP INSPECTION: MasterControlAIML/JSON-Unstructured-Structured")
print("="*70)

ds = load_dataset("MasterControlAIML/JSON-Unstructured-Structured", split="train")

print(f"\nDataset size: {len(ds):,} examples")
print(f"Columns: {ds.column_names}")

# Analyze 5 samples in detail
print(f"\n" + "="*70)
print("DETAILED SAMPLES")
print("="*70)

for i in range(min(5, len(ds))):
    sample = ds[i]
    
    print(f"\n--- Sample {i+1} ---")
    print(f"Text preview: {sample['text'][:250]}...")
    
    # Try to parse schema
    try:
        schema = json.loads(sample['schema'])
        print(f"Schema (valid JSON): {len(sample['schema'])} chars, {len(schema.get('properties', {}))} properties")
    except:
        print(f"Schema: Not valid JSON or not parseable")
    
    # Try to parse object (target JSON)
    try:
        obj = json.loads(sample['object'])
        obj_str = json.dumps(obj, indent=2, ensure_ascii=False)
        print(f"Target JSON ({len(obj_str)} chars):")
        if len(obj_str) > 400:
            print(obj_str[:400] + "...")
        else:
            print(obj_str)
    except Exception as e:
        print(f"Target JSON: Not parseable - {e}")

# Statistics
print(f"\n" + "="*70)
print("QUALITY STATISTICS (first 100)")
print("="*70)

valid_schema_count = 0
valid_json_count = 0
json_sizes = []
text_sizes = []

for i in range(min(100, len(ds))):
    sample = ds[i]
    
    # Check schema
    try:
        json.loads(sample['schema'])
        valid_schema_count += 1
    except:
        pass
    
    # Check object
    try:
        obj = json.loads(sample['object'])
        valid_json_count += 1
        json_sizes.append(len(json.dumps(obj, ensure_ascii=False)))
    except:
        pass
    
    # Text size
    text_sizes.append(len(sample['text']))

print(f"Valid schemas: {valid_schema_count}/100 ({valid_schema_count}%)")
print(f"Valid JSON objects: {valid_json_count}/100 ({valid_json_count}%)")

if json_sizes:
    print(f"\nJSON size distribution:")
    print(f"  Avg: {sum(json_sizes)/len(json_sizes):.0f} chars")
    print(f"  Min: {min(json_sizes)}, Max: {max(json_sizes)}")
    
    # Size buckets
    small = sum(1 for s in json_sizes if s < 200)
    medium = sum(1 for s in json_sizes if 200 <= s < 1000)
    large = sum(1 for s in json_sizes if s >= 1000)
    print(f"  Small (<200): {small}")
    print(f"  Medium (200-1k): {medium}")
    print(f"  Large (1k+): {large}")

if text_sizes:
    print(f"\nText size distribution:")
    print(f"  Avg: {sum(text_sizes)/len(text_sizes):.0f} chars")

# Final assessment
print(f"\n" + "="*70)
print("FINAL ASSESSMENT")
print("="*70)

if valid_json_count >= 95 and valid_schema_count >= 95:
    print("[EXCELLENT] High quality dataset!")
    print(f"  - 10,000 examples")
    print(f"  - Valid JSON: {valid_json_count}%")
    print(f"  - Valid schemas: {valid_schema_count}%")
    print(f"  - Has text + schema -> JSON format")
    print(f"\n[RECOMMENDATION: ADD THIS DATASET]")
    print(f"  Benefit: +10k high-quality text->JSON examples")
    print(f"  Format: Directly compatible with our training")
elif valid_json_count >= 80:
    print("[GOOD] Decent quality")
    print(f"\n[RECOMMENDATION: CONSIDER ADDING]")
    print(f"  Needs: Check if format aligns with our tasks")
else:
    print("[POOR] Quality issues")
    print(f"\n[RECOMMENDATION: SKIP]")
    print(f"  Reason: Too many invalid JSON outputs")

