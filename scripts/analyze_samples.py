#!/usr/bin/env python3
"""
Analyze collected data quality
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_file(file_path: Path, name: str, num_samples: int = 5):
    if not file_path.exists():
        print(f"\n{name}: File not found")
        return
    
    print(f"\n{'='*70}")
    print(f"{name.upper()}")
    print('='*70)
    
    samples = []
    stats = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            try:
                example = json.loads(line)
                if idx < num_samples:
                    samples.append(example)
                
                # Collect statistics
                stats['total'] += 1
                stats['format_' + example.get('format', 'unknown')] += 1
                stats['task_' + example.get('task', 'unknown')] += 1
                
                # Check if example has actual JSON
                if 'example' in example:
                    try:
                        ex_str = json.dumps(example['example'])
                        stats['has_valid_example'] += 1
                        stats['total_json_chars'] += len(ex_str)
                    except:
                        stats['invalid_example'] += 1
                
                # Check if has schema
                if 'schema' in example and example['schema']:
                    stats['has_schema'] += 1
            
            except Exception as e:
                stats['parse_errors'] += 1
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"  Total examples: {stats['total']:,}")
    print(f"  Valid examples: {stats['has_valid_example']:,}")
    print(f"  With schema: {stats['has_schema']:,}")
    print(f"  Parse errors: {stats['parse_errors']}")
    
    if stats['total'] > 0:
        avg_size = stats['total_json_chars'] / max(stats['has_valid_example'], 1)
        print(f"  Avg JSON size: {avg_size:.0f} chars")
    
    print(f"\nFormat distribution:")
    for key, val in stats.items():
        if key.startswith('format_'):
            format_name = key.replace('format_', '')
            pct = (val / stats['total']) * 100
            print(f"  {format_name:20s}: {val:,} ({pct:.1f}%)")
    
    print(f"\nTask distribution:")
    for key, val in stats.items():
        if key.startswith('task_'):
            task_name = key.replace('task_', '')
            pct = (val / stats['total']) * 100
            print(f"  {task_name:20s}: {val:,} ({pct:.1f}%)")
    
    # Print samples
    print(f"\nSample examples (first {num_samples}):")
    for i, sample in enumerate(samples):
        print(f"\n--- Sample {i+1} ---")
        print(f"Source: {sample.get('source', 'unknown')}")
        print(f"Format: {sample.get('format', 'unknown')}")
        print(f"Task: {sample.get('task', 'unknown')}")
        
        example_data = sample.get('example', {})
        example_str = json.dumps(example_data, indent=2, ensure_ascii=False)
        if len(example_str) > 300:
            print(f"Example: {example_str[:300]}...\n(truncated, {len(example_str)} total chars)")
        else:
            print(f"Example: {example_str}")

def main():
    raw_dir = Path("../datasets/raw")
    
    print("="*70)
    print("DATA QUALITY ANALYSIS")
    print("="*70)
    
    analyze_file(raw_dir / "cloudevents" / "cloudevents_examples.jsonl", "CloudEvents", 3)
    analyze_file(raw_dir / "schemastore" / "schemastore_examples.jsonl", "SchemaStore", 3)
    analyze_file(raw_dir / "apis_guru" / "apis_guru_examples.jsonl", "APIs.guru", 3)
    
    print("\n" + "="*70)
    print("OVERALL ASSESSMENT")
    print("="*70)
    
    # Count totals
    total = 0
    for file_name in ["cloudevents/cloudevents_examples.jsonl", "schemastore/schemastore_examples.jsonl", "apis_guru/apis_guru_examples.jsonl"]:
        file_path = raw_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in f)
                total += count
                print(f"{file_name:50s}: {count:,}")
    
    print(f"\n{'TOTAL COLLECTED':50s}: {total:,}")
    print(f"{'TARGET':50s}: 100,000+")
    print(f"{'PROGRESS':50s}: {total/100000*100:.1f}%")

if __name__ == "__main__":
    main()

