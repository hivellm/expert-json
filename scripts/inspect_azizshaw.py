#!/usr/bin/env python3
"""
Deep inspection of azizshaw/text_to_json
"""

import json
from datasets import load_dataset

print("="*70)
print("DEEP INSPECTION: azizshaw/text_to_json")
print("="*70)

ds = load_dataset("azizshaw/text_to_json", split="train")

print(f"\nDataset size: {len(ds)} examples")
print(f"Columns: {ds.column_names}")

# Analyze 10 samples
print(f"\n" + "="*70)
print("SAMPLE ANALYSIS (10 examples)")
print("="*70)

for i in range(min(10, len(ds))):
    sample = ds[i]
    
    print(f"\n--- Sample {i+1} ---")
    print(f"Instruction: {sample['instruction'][:150]}...")
    print(f"Input: {sample['input'][:200]}...")
    
    # Try to parse output as JSON
    try:
        output_json = json.loads(sample['output'])
        output_str = json.dumps(output_json, indent=2, ensure_ascii=False)
        print(f"Output (JSON, {len(output_str)} chars):")
        if len(output_str) > 300:
            print(output_str[:300] + "...")
        else:
            print(output_str)
    except:
        print(f"Output (not JSON): {sample['output'][:100]}...")

# Statistics
print(f"\n" + "="*70)
print("STATISTICS")
print("="*70)

valid_json_count = 0
json_sizes = []

for i in range(min(100, len(ds))):
    try:
        output_json = json.loads(ds[i]['output'])
        valid_json_count += 1
        json_sizes.append(len(json.dumps(output_json, ensure_ascii=False)))
    except:
        pass

print(f"Valid JSON outputs: {valid_json_count}/100 ({valid_json_count}%)")
if json_sizes:
    print(f"Avg JSON size: {sum(json_sizes)/len(json_sizes):.0f} chars")
    print(f"Min: {min(json_sizes)}, Max: {max(json_sizes)}")

# Assessment
print(f"\n" + "="*70)
print("FINAL ASSESSMENT")
print("="*70)

if valid_json_count >= 90:
    print("[OK] High JSON validity (>=90%)")
else:
    print(f"[WARN] Lower JSON validity ({valid_json_count}%)")

if json_sizes and sum(json_sizes)/len(json_sizes) > 200:
    print("[OK] Good average size")
else:
    print("[WARN] Small average size")

print(f"\nRecommendation:")
if valid_json_count >= 80 and len(ds) >= 500:
    print("  [ADD] - 845 examples with text->JSON format")
    print("  Value: Adds variety to generation tasks")
    print("  Format: instruction + input -> JSON output")
else:
    print("  [SKIP] - Quality concerns or too small")

print(f"\nIf adding, create: collect_azizshaw.py")

