#!/usr/bin/env python3
"""
Create final dataset splits for Expert-JSON
- Train: 90%
- Validation: 5%
- Test: 5%
"""
import json
import random
from pathlib import Path
from collections import defaultdict

def load_dataset(path):
    """Load dataset from JSONL"""
    examples = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line.strip()))
    return examples

def stratified_split(examples, val_ratio=0.05, test_ratio=0.05, seed=42):
    """Split dataset with stratification by task type"""
    random.seed(seed)
    
    # Group by task type
    by_task = defaultdict(list)
    for ex in examples:
        text = ex['text']
        if 'json_generation' in text:
            by_task['generation'].append(ex)
        elif 'json_correction' in text:
            by_task['correction'].append(ex)
        else:
            by_task['other'].append(ex)
    
    train, val, test = [], [], []
    
    for task_type, task_examples in by_task.items():
        # Shuffle
        random.shuffle(task_examples)
        
        n = len(task_examples)
        n_val = int(n * val_ratio)
        n_test = int(n * test_ratio)
        n_train = n - n_val - n_test
        
        # Split
        train.extend(task_examples[:n_train])
        val.extend(task_examples[n_train:n_train+n_val])
        test.extend(task_examples[n_train+n_val:])
        
        print(f"  {task_type:12s}: {n:6,} → train={n_train:6,}, val={n_val:4,}, test={n_test:4,}")
    
    # Shuffle final sets
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    
    return train, val, test

def save_split(examples, path):
    """Save split to JSONL"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

def analyze_split(examples, split_name):
    """Analyze split composition"""
    stats = {
        'total': len(examples),
        'tasks': defaultdict(int),
        'avg_size': 0,
        'sizes': []
    }
    
    for ex in examples:
        text = ex['text']
        stats['sizes'].append(len(text))
        
        if 'json_generation' in text:
            stats['tasks']['generation'] += 1
        elif 'json_correction' in text:
            stats['tasks']['correction'] += 1
        else:
            stats['tasks']['other'] += 1
    
    stats['avg_size'] = sum(stats['sizes']) / len(stats['sizes']) if stats['sizes'] else 0
    stats['median_size'] = sorted(stats['sizes'])[len(stats['sizes']) // 2] if stats['sizes'] else 0
    
    return stats

def main():
    # Paths
    input_path = Path('datasets/train.jsonl')
    output_dir = Path('datasets/final')
    
    train_path = output_dir / 'train.jsonl'
    val_path = output_dir / 'validation.jsonl'
    test_path = output_dir / 'test.jsonl'
    
    print("="*70)
    print("CREATING FINAL DATASET SPLITS")
    print("="*70)
    
    # Load
    print(f"\nLoading dataset from {input_path}...")
    examples = load_dataset(input_path)
    print(f"✓ Loaded {len(examples):,} examples")
    
    # Split
    print(f"\nSplitting dataset (90% train, 5% val, 5% test)...")
    train, val, test = stratified_split(examples, val_ratio=0.05, test_ratio=0.05)
    
    print(f"\n✓ Split complete:")
    print(f"  Train:      {len(train):6,} examples ({len(train)/len(examples)*100:.1f}%)")
    print(f"  Validation: {len(val):6,} examples ({len(val)/len(examples)*100:.1f}%)")
    print(f"  Test:       {len(test):6,} examples ({len(test)/len(examples)*100:.1f}%)")
    
    # Save
    print(f"\nSaving splits to {output_dir}/...")
    save_split(train, train_path)
    save_split(val, val_path)
    save_split(test, test_path)
    
    print(f"✓ Saved:")
    print(f"  {train_path}")
    print(f"  {val_path}")
    print(f"  {test_path}")
    
    # Analyze splits
    print("\n" + "="*70)
    print("SPLIT ANALYSIS")
    print("="*70)
    
    for split_name, split_data in [('Train', train), ('Validation', val), ('Test', test)]:
        stats = analyze_split(split_data, split_name)
        
        print(f"\n{split_name}:")
        print(f"  Total:      {stats['total']:,}")
        print(f"  Tasks:")
        for task, count in stats['tasks'].items():
            pct = count / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"    {task:12s}: {count:6,} ({pct:5.1f}%)")
        print(f"  Avg size:   {stats['avg_size']:,.0f} chars")
        print(f"  Median:     {stats['median_size']:,} chars")
    
    # Save metadata
    metadata = {
        'total_examples': len(examples),
        'splits': {
            'train': {
                'count': len(train),
                'percentage': len(train) / len(examples) * 100,
                'path': str(train_path)
            },
            'validation': {
                'count': len(val),
                'percentage': len(val) / len(examples) * 100,
                'path': str(val_path)
            },
            'test': {
                'count': len(test),
                'percentage': len(test) / len(examples) * 100,
                'path': str(test_path)
            }
        },
        'split_strategy': 'stratified by task type',
        'random_seed': 42
    }
    
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Metadata saved to {metadata_path}")
    
    print("\n" + "="*70)
    print("DATASET CREATION COMPLETE")
    print("="*70)
    print(f"\nFinal dataset ready in: {output_dir}/")
    print(f"  • train.jsonl       ({len(train):,} examples)")
    print(f"  • validation.jsonl  ({len(val):,} examples)")
    print(f"  • test.jsonl        ({len(test):,} examples)")
    print(f"  • metadata.json")
    print("\nReady for training! 🚀")

if __name__ == '__main__':
    main()

