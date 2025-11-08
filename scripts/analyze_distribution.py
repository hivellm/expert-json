#!/usr/bin/env python3
"""
Analyze distribution of Expert-JSON dataset
Similar to SQL and Neo4j distribution analysis scripts
"""
import json
import re
from collections import Counter
from pathlib import Path
import sys

def extract_task_from_chatml(text: str) -> str:
    """Extract task type from ChatML format"""
    if not text:
        return "unknown"
    
    # Look for Task: in system message
    task_match = re.search(r'Task:\s*(\w+)', text)
    if task_match:
        task = task_match.group(1)
        # Normalize task names
        if 'generation' in task.lower():
            return "generation"
        elif 'correction' in task.lower() or 'repair' in task.lower():
            return "correction"
        elif 'extraction' in task.lower():
            return "extraction"
        elif 'schema' in task.lower():
            return "schema_generation"
        return task.lower()
    
    return "unknown"

def extract_format_from_chatml(text: str) -> str:
    """Extract format type from ChatML format"""
    if not text:
        return "unknown"
    
    # Look for Format: in system message
    format_match = re.search(r'Format:\s*(\w+)', text)
    if format_match:
        return format_match.group(1).lower()
    
    return "unknown"

def analyze_complexity(text: str) -> str:
    """Analyze JSON complexity based on structure"""
    if not text:
        return "simple"
    
    # Extract assistant response (JSON)
    assistant_match = re.search(r'<\|assistant\|>\s*\n(.*?)\n<\|end\|>', text, re.DOTALL)
    if not assistant_match:
        return "simple"
    
    json_text = assistant_match.group(1).strip()
    
    try:
        json_obj = json.loads(json_text)
        
        # Count nesting depth
        def max_depth(obj, current=0):
            if not isinstance(obj, (dict, list)):
                return current
            if not obj:
                return current
            if isinstance(obj, dict):
                return max([max_depth(v, current + 1) for v in obj.values()], default=current)
            else:  # list
                return max([max_depth(item, current + 1) for item in obj], default=current)
        
        depth = max_depth(json_obj)
        
        # Count keys/items
        def count_items(obj):
            if isinstance(obj, dict):
                return len(obj) + sum(count_items(v) for v in obj.values())
            elif isinstance(obj, list):
                return len(obj) + sum(count_items(item) for item in obj)
            return 0
        
        items = count_items(json_obj)
        
        # Classify complexity
        if depth <= 2 and items <= 5:
            return "simple"
        elif depth <= 3 and items <= 15:
            return "medium"
        elif depth <= 4 and items <= 30:
            return "complex"
        else:
            return "very_complex"
    
    except:
        return "simple"

def load_and_analyze_dataset(dataset_path: Path):
    """Load and analyze dataset distribution"""
    print("="*80)
    print("EXPERT-JSON DATASET DISTRIBUTION ANALYSIS")
    print("="*80)
    print(f"\nLoading dataset: {dataset_path}")
    
    tasks = Counter()
    formats = Counter()
    complexity_levels = Counter()
    empty_count = 0
    total = 0
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            total += 1
            try:
                example = json.loads(line.strip())
                text = example.get("text", "")
                
                if not text:
                    empty_count += 1
                    continue
                
                # Extract task type
                task = extract_task_from_chatml(text)
                tasks[task] += 1
                
                # Extract format
                format_type = extract_format_from_chatml(text)
                formats[format_type] += 1
                
                # Analyze complexity
                complexity = analyze_complexity(text)
                complexity_levels[complexity] += 1
                
            except Exception as e:
                empty_count += 1
                if empty_count < 10:
                    print(f"  Warning: Error processing line {i+1}: {e}")
                continue
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed: {i + 1:,} examples...")
    
    print(f"\nTotal examples analyzed: {total:,}")
    print(f"Empty/invalid examples: {empty_count:,}")
    
    return {
        "tasks": tasks,
        "formats": formats,
        "complexity": complexity_levels,
        "total": total,
        "empty": empty_count
    }

def print_distribution_summary(analysis_results):
    """Print distribution summary"""
    tasks = analysis_results["tasks"]
    formats = analysis_results["formats"]
    complexity = analysis_results["complexity"]
    total = analysis_results["total"]
    empty = analysis_results["empty"]
    
    valid_total = total - empty
    
    print("\n" + "="*80)
    print("DISTRIBUTION SUMMARY")
    print("="*80)
    
    print("\n[TASK DISTRIBUTION]")
    print("-" * 80)
    for task, count in tasks.most_common():
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {task:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n[FORMAT DISTRIBUTION]")
    print("-" * 80)
    for fmt, count in formats.most_common(15):
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {fmt:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n[COMPLEXITY DISTRIBUTION]")
    print("-" * 80)
    for comp, count in complexity.most_common():
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {comp:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n" + "="*80)
    print(f"Total valid examples: {valid_total:,}")
    print(f"Total examples: {total:,}")
    print(f"Empty/invalid: {empty:,}")
    print("="*80)

def main():
    dataset_path = Path("datasets/train.jsonl")
    
    if not dataset_path.exists():
        print(f"[ERROR] Dataset not found: {dataset_path}")
        return
    
    analysis_results = load_and_analyze_dataset(dataset_path)
    print_distribution_summary(analysis_results)

if __name__ == "__main__":
    main()

