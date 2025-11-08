#!/usr/bin/env python3
"""
Deep quality analysis of collected data
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_complexity(file_path: Path, name: str):
    print(f"\n{'='*70}")
    print(f"{name} - COMPLEXITY ANALYSIS")
    print('='*70)
    
    sizes = []
    complex_samples = []
    simple_samples = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= 1000:  # Analyze first 1000
                break
            try:
                example = json.loads(line)
                ex_json = example.get('example', {})
                ex_str = json.dumps(ex_json, ensure_ascii=False)
                size = len(ex_str)
                sizes.append(size)
                
                if size > 200 and len(complex_samples) < 3:
                    complex_samples.append((example, size))
                if size < 50 and len(simple_samples) < 5:
                    simple_samples.append((example, size))
            except:
                continue
    
    if sizes:
        print(f"\nSize distribution (first 1000):")
        print(f"  Min: {min(sizes)} chars")
        print(f"  Max: {max(sizes)} chars")
        print(f"  Avg: {sum(sizes)/len(sizes):.0f} chars")
        print(f"  Median: {sorted(sizes)[len(sizes)//2]} chars")
        
        # Buckets
        tiny = sum(1 for s in sizes if s < 50)
        small = sum(1 for s in sizes if 50 <= s < 200)
        medium = sum(1 for s in sizes if 200 <= s < 1000)
        large = sum(1 for s in sizes if s >= 1000)
        
        print(f"\n  Tiny (<50):     {tiny:4d} ({tiny/len(sizes)*100:5.1f}%)")
        print(f"  Small (50-200): {small:4d} ({small/len(sizes)*100:5.1f}%)")
        print(f"  Medium (200-1k): {medium:4d} ({medium/len(sizes)*100:5.1f}%)")
        print(f"  Large (1k+):    {large:4d} ({large/len(sizes)*100:5.1f}%)")
    
    # Show samples
    if complex_samples:
        print(f"\nComplex example ({complex_samples[0][1]} chars):")
        example_data = complex_samples[0][0].get('example', {})
        print(json.dumps(example_data, indent=2, ensure_ascii=False)[:400])
        if complex_samples[0][1] > 400:
            print("... (truncated)")
    
    if simple_samples:
        print(f"\nSimple examples:")
        for sample, size in simple_samples[:3]:
            schema_name = sample.get('schema_name', 'unknown')
            example_data = sample.get('example', {})
            print(f"  {schema_name} ({size} chars): {json.dumps(example_data, ensure_ascii=False)}")
    
    # Assessment
    print(f"\nQuality assessment:")
    if not sizes:
        print("  ❌ No valid examples found")
        return "poor"
    
    avg_size = sum(sizes) / len(sizes)
    tiny_pct = (tiny / len(sizes)) * 100 if sizes else 0
    
    if avg_size < 100:
        print(f"  [WARN] Very small average ({avg_size:.0f} chars)")
    elif avg_size < 300:
        print(f"  [WARN] Small average ({avg_size:.0f} chars)")
    else:
        print(f"  [OK] Good average size ({avg_size:.0f} chars)")
    
    if tiny_pct > 50:
        print(f"  [BAD] Too many tiny examples ({tiny_pct:.1f}%)")
        return "poor"
    elif tiny_pct > 30:
        print(f"  [WARN] Many tiny examples ({tiny_pct:.1f}%)")
        return "fair"
    else:
        print(f"  [OK] Good size distribution")
        return "good"

def main():
    raw_dir = Path("../datasets/raw")
    
    print("="*70)
    print("DATASET QUALITY ANALYSIS")
    print("="*70)
    
    assessments = {}
    
    if (raw_dir / "cloudevents" / "cloudevents_examples.jsonl").exists():
        assessments['cloudevents'] = analyze_complexity(
            raw_dir / "cloudevents" / "cloudevents_examples.jsonl",
            "CloudEvents"
        )
    
    if (raw_dir / "schemastore" / "schemastore_examples.jsonl").exists():
        assessments['schemastore'] = analyze_complexity(
            raw_dir / "schemastore" / "schemastore_examples.jsonl",
            "SchemaStore"
        )
    
    if (raw_dir / "apis_guru" / "apis_guru_examples.jsonl").exists():
        assessments['apis_guru'] = analyze_complexity(
            raw_dir / "apis_guru" / "apis_guru_examples.jsonl",
            "APIs.guru"
        )
    
    # Final recommendation
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print('='*70)
    
    for source, quality in assessments.items():
        if quality == "good":
            print(f"[KEEP] {source:15s}: Good quality")
        elif quality == "fair":
            print(f"[CAUTION] {source:15s}: Fair quality")
        else:
            print(f"[EXCLUDE] {source:15s}: Poor quality")
    
    print("\nOverall strategy:")
    if assessments.get('schemastore') == 'poor':
        print("[WARN] SchemaStore has very simple examples - consider:")
        print("   1. Exclude SchemaStore entirely")
        print("   2. Filter out examples < 100 chars")
        print("   3. Focus on APIs.guru + CloudEvents only")
    
    if assessments.get('apis_guru') == 'good':
        print("[OK] APIs.guru looks promising - continue collection")
    
    if assessments.get('cloudevents') == 'good':
        print("[OK] CloudEvents has good structure")

if __name__ == "__main__":
    main()

