#!/usr/bin/env python3
"""
Monitor collection progress

Checks output files and shows statistics
"""

import json
from pathlib import Path
import time

def check_file(file_path: Path, name: str):
    if not file_path.exists():
        print(f"  {name:20s}: Not started")
        return 0
    
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            count += 1
    
    size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"  {name:20s}: {count:,} examples ({size_mb:.1f} MB)")
    return count

def main():
    raw_dir = Path("../datasets/raw")
    
    print("="*60)
    print("COLLECTION PROGRESS MONITOR")
    print("="*60 + "\n")
    
    total = 0
    
    total += check_file(raw_dir / "apis_guru" / "apis_guru_examples.jsonl", "APIs.guru")
    total += check_file(raw_dir / "schemastore" / "schemastore_examples.jsonl", "SchemaStore")
    total += check_file(raw_dir / "cloudevents" / "cloudevents_examples.jsonl", "CloudEvents")
    total += check_file(raw_dir / "negatives" / "negative_examples.jsonl", "Negatives")
    
    print(f"\n  {'TOTAL':20s}: {total:,} examples")
    print(f"  {'TARGET':20s}: 100,000+ examples")
    print(f"  {'PROGRESS':20s}: {total/100000*100:.1f}%")

if __name__ == "__main__":
    while True:
        main()
        print(f"\nRefreshing in 30 seconds... (Ctrl+C to stop)")
        time.sleep(30)
        print("\033[2J\033[H")  # Clear screen

