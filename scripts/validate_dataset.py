#!/usr/bin/env python3
"""
Dataset Validation Script

Validates the preprocessed dataset:
- Sample 100 random examples for manual review
- Check format distribution
- Verify negative examples have valid corrections
- Validate JSON parseability
"""

import json
import random
from pathlib import Path
from collections import defaultdict

def main():
    dataset_file = Path("../datasets/train.jsonl")
    
    if not dataset_file.exists():
        print(f"Error: {dataset_file} not found")
        print("Run preprocess.py first")
        return
    
    # Load all examples
    print("Loading dataset...")
    examples = []
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))
    
    print(f"Total examples: {len(examples):,}\n")
    
    # Sample 100 random
    sample_size = min(100, len(examples))
    samples = random.sample(examples, sample_size)
    
    # Analyze samples
    stats = defaultdict(int)
    task_distribution = defaultdict(int)
    format_distribution = defaultdict(int)
    
    print(f"Analyzing {sample_size} random samples...\n")
    
    for idx, example in enumerate(samples):
        text = example.get("text", "")
        
        # Parse ChatML format
        if "Task: json_generation" in text:
            task_distribution["generation"] += 1
        elif "Task: json_correction" in text:
            task_distribution["correction"] += 1
        else:
            stats["unknown_task"] += 1
        
        # Extract format
        if "Format: openapi" in text:
            format_distribution["openapi"] += 1
        elif "Format: json_schema" in text:
            format_distribution["json_schema"] += 1
        elif "Format: cloudevents" in text:
            format_distribution["cloudevents"] += 1
        elif "Format: generic" in text:
            format_distribution["generic"] += 1
        
        # Check if JSON is parseable (extract from <|assistant|> section)
        try:
            assistant_start = text.find("<|assistant|>\n") + len("<|assistant|>\n")
            assistant_end = text.find("\n<|end|>", assistant_start)
            json_content = text[assistant_start:assistant_end]
            
            parsed = json.loads(json_content)
            stats["valid_json"] += 1
        except:
            stats["invalid_json"] += 1
            if stats["invalid_json"] <= 5:
                print(f"[WARN] Sample {idx} has unparseable JSON")
    
    # Print validation results
    print("="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print(f"\nSample size: {sample_size}")
    print(f"\nTask Distribution:")
    for task, count in task_distribution.items():
        pct = (count / sample_size) * 100
        print(f"  {task:15s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nFormat Distribution:")
    for fmt, count in format_distribution.items():
        pct = (count / sample_size) * 100
        print(f"  {fmt:15s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nJSON Validity:")
    print(f"  Valid JSON:     {stats['valid_json']} ({stats['valid_json']/sample_size*100:.1f}%)")
    print(f"  Invalid JSON:   {stats['invalid_json']} ({stats['invalid_json']/sample_size*100:.1f}%)")
    
    # Print sample examples
    print(f"\n" + "="*60)
    print("SAMPLE EXAMPLES (first 3)")
    print("="*60)
    
    for i in range(min(3, len(samples))):
        print(f"\nExample {i+1}:")
        print("-" * 60)
        text = samples[i]["text"]
        # Truncate if too long
        if len(text) > 500:
            print(text[:500] + "\n... (truncated)")
        else:
            print(text)
    
    # Validation recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if stats["invalid_json"] > sample_size * 0.05:
        print("⚠️  High invalid JSON rate (>5%) - review preprocessing")
    else:
        print("✅ JSON validity rate acceptable")
    
    correction_pct = (task_distribution["correction"] / sample_size) * 100
    if correction_pct < 20 or correction_pct > 40:
        print(f"⚠️  Correction tasks at {correction_pct:.1f}% (target: 20-40%)")
    else:
        print(f"✅ Correction tasks at {correction_pct:.1f}% (within target range)")
    
    if len(format_distribution) >= 3:
        print("✅ Format diversity achieved (≥3 formats)")
    else:
        print("⚠️  Low format diversity (<3 formats)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

