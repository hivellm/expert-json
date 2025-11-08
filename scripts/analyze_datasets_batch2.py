#!/usr/bin/env python3
"""
Analyze batch 2 of additional datasets
"""

import json
from datasets import load_dataset

datasets_to_analyze = [
    "azizshaw/text_to_json",
    "MasterControlAIML/JSON-Unstructured-Structured",
    "ChristianAzinn/json-training",
    "NousResearch/json-mode-eval",
    "araloq/json_data_extraction"
]

print("="*70)
print("ANALYZING ADDITIONAL JSON DATASETS - BATCH 2")
print("="*70)

recommendations = {}

for idx, dataset_name in enumerate(datasets_to_analyze, 1):
    print(f"\n{idx}. {dataset_name}")
    print("-"*70)
    
    try:
        # Try to load dataset
        ds = load_dataset(dataset_name)
        splits = list(ds.keys())
        first_split = splits[0]
        
        print(f"Splits: {splits}")
        print(f"Examples ({first_split}): {len(ds[first_split]):,}")
        print(f"Columns: {ds[first_split].column_names}")
        
        # Analyze first example
        if len(ds[first_split]) > 0:
            sample = ds[first_split][0]
            print(f"\nSample structure:")
            for key in sample.keys():
                value = sample[key]
                value_type = type(value).__name__
                if isinstance(value, str):
                    preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"  {key} ({value_type}): {preview}")
                elif isinstance(value, (dict, list)):
                    print(f"  {key} ({value_type}): {len(value)} items")
                else:
                    print(f"  {key} ({value_type}): {value}")
        
        # Analyze diversity (first 100)
        if len(ds[first_split]) >= 10:
            print(f"\nAnalyzing diversity (first 100)...")
            samples = ds[first_split].select(range(min(100, len(ds[first_split]))))
            
            # Try to find JSON fields
            json_fields = []
            for col in ds[first_split].column_names:
                first_val = samples[0][col]
                if isinstance(first_val, (dict, list, str)):
                    json_fields.append(col)
            
            print(f"  Potential JSON fields: {json_fields}")
        
        # Assessment
        print(f"\n[ASSESSMENT]")
        num_examples = len(ds[first_split])
        
        if num_examples < 100:
            print(f"  Size: TOO SMALL ({num_examples} examples)")
            rec = "SKIP"
        elif num_examples < 1000:
            print(f"  Size: Small ({num_examples} examples)")
            rec = "MAYBE"
        else:
            print(f"  Size: Good ({num_examples:,} examples)")
            rec = "CONSIDER"
        
        # Check if has text->JSON format
        has_text = any('text' in col.lower() or 'input' in col.lower() for col in ds[first_split].column_names)
        has_json = any('json' in col.lower() or 'output' in col.lower() or 'structured' in col.lower() for col in ds[first_split].column_names)
        
        if has_text and has_json:
            print(f"  Format: Has text->JSON mapping")
            rec = rec if rec != "SKIP" else "MAYBE"
        else:
            print(f"  Format: Unknown/incompatible")
            rec = "SKIP"
        
        recommendations[dataset_name] = rec
        print(f"  Recommendation: {rec}")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        recommendations[dataset_name] = "ERROR"

# Final summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

for dataset_name, rec in recommendations.items():
    if rec == "SKIP":
        status = "[SKIP]"
    elif rec == "MAYBE":
        status = "[MAYBE]"
    elif rec == "CONSIDER":
        status = "[ADD]"
    else:
        status = "[ERROR]"
    
    print(f"{status:10s} {dataset_name}")

print("\n" + "="*70)
print("ACTION PLAN")
print("="*70)

add_these = [k for k, v in recommendations.items() if v == "CONSIDER"]
maybe_these = [k for k, v in recommendations.items() if v == "MAYBE"]

if add_these:
    print(f"\nADD THESE ({len(add_these)}):")
    for ds in add_these:
        print(f"  - {ds}")

if maybe_these:
    print(f"\nINSPECT MANUALLY ({len(maybe_these)}):")
    for ds in maybe_these:
        print(f"  - {ds}")

print(f"\nSKIPPED: {len([v for v in recommendations.values() if v == 'SKIP'])}")

