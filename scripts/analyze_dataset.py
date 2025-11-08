#!/usr/bin/env python3
"""
Analyze Expert-JSON dataset and generate statistics for documentation
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
import sys

def analyze_dataset(dataset_path, sample_size=1000):
    """Analyze dataset comprehensively"""
    
    stats = {
        'total_examples': 0,
        'task_types': defaultdict(int),
        'formats': defaultdict(int),
        'sizes': [],
        'system_prompts': Counter(),
        'error_types': defaultdict(int),
        'sources': defaultdict(int),
        'example_sizes': {'json': [], 'text': []},
        'schema_presence': {'with_schema': 0, 'without_schema': 0}
    }
    
    print(f"Analyzing dataset: {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            stats['total_examples'] += 1
            
            try:
                data = json.loads(line.strip())
                text = data.get('text', '')
                
                # Overall size
                stats['sizes'].append(len(text))
                
                # Extract task type
                if 'Task: json_generation' in text:
                    stats['task_types']['generation'] += 1
                elif 'Task: json_correction' in text:
                    stats['task_types']['correction'] += 1
                elif 'Task: json_extraction' in text or 'Task: data_extraction' in text:
                    stats['task_types']['extraction'] += 1
                
                # Extract format
                if 'Format: openapi' in text:
                    if 'openapi_schema' in text:
                        stats['formats']['openapi_schema'] += 1
                    elif 'openapi_request' in text:
                        stats['formats']['openapi_request'] += 1
                    elif 'openapi_response' in text:
                        stats['formats']['openapi_response'] += 1
                    else:
                        stats['formats']['openapi_property'] += 1
                elif 'Format: json_schema' in text:
                    stats['formats']['json_schema'] += 1
                elif 'Format: cloudevents' in text:
                    stats['formats']['cloudevents'] += 1
                elif 'Format: data_extraction' in text:
                    stats['formats']['data_extraction'] += 1
                
                # Extract error types (for corrections)
                if 'Error type:' in text:
                    error_line = [l for l in text.split('\n') if 'Error type:' in l]
                    if error_line:
                        error_type = error_line[0].split('Error type:')[1].strip()
                        stats['error_types'][error_type] += 1
                
                # Schema presence
                if 'Schema:' in text:
                    stats['schema_presence']['with_schema'] += 1
                else:
                    stats['schema_presence']['without_schema'] += 1
                
                # Sample size limits
                if i < sample_size:
                    # Measure JSON output size
                    assistant_part = text.split('<|assistant|>')
                    if len(assistant_part) > 1:
                        json_output = assistant_part[1].split('<|end|>')[0].strip()
                        stats['example_sizes']['json'].append(len(json_output))
                
            except Exception as e:
                print(f"Error processing line {i}: {e}")
                continue
    
    return stats

def calculate_statistics(stats):
    """Calculate derived statistics"""
    
    # Size statistics
    sizes = stats['sizes']
    sizes.sort()
    
    size_stats = {
        'min': min(sizes) if sizes else 0,
        'max': max(sizes) if sizes else 0,
        'mean': sum(sizes) / len(sizes) if sizes else 0,
        'median': sizes[len(sizes) // 2] if sizes else 0,
        'p25': sizes[len(sizes) // 4] if sizes else 0,
        'p75': sizes[3 * len(sizes) // 4] if sizes else 0,
        'p90': sizes[9 * len(sizes) // 10] if sizes else 0,
        'p95': sizes[95 * len(sizes) // 100] if sizes else 0,
    }
    
    # JSON size statistics
    json_sizes = stats['example_sizes']['json']
    if json_sizes:
        json_sizes.sort()
        json_size_stats = {
            'min': min(json_sizes),
            'max': max(json_sizes),
            'mean': sum(json_sizes) / len(json_sizes),
            'median': json_sizes[len(json_sizes) // 2],
        }
    else:
        json_size_stats = {}
    
    # Task distribution percentages
    total = stats['total_examples']
    task_percentages = {
        task: (count / total * 100) if total > 0 else 0
        for task, count in stats['task_types'].items()
    }
    
    # Format distribution percentages
    format_percentages = {
        fmt: (count / total * 100) if total > 0 else 0
        for fmt, count in stats['formats'].items()
    }
    
    return {
        'size_stats': size_stats,
        'json_size_stats': json_size_stats,
        'task_percentages': task_percentages,
        'format_percentages': format_percentages
    }

def generate_report(stats, derived_stats, output_path):
    """Generate comprehensive analysis report"""
    
    report = {
        'summary': {
            'total_examples': stats['total_examples'],
            'total_size_bytes': sum(stats['sizes'])
        },
        'task_distribution': dict(stats['task_types']),
        'task_percentages': derived_stats['task_percentages'],
        'format_distribution': dict(stats['formats']),
        'format_percentages': derived_stats['format_percentages'],
        'error_types': dict(stats['error_types']),
        'schema_presence': stats['schema_presence'],
        'size_statistics': derived_stats['size_stats'],
        'json_size_statistics': derived_stats['json_size_stats']
    }
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Report saved to: {output_path}")
    return report

def print_summary(report):
    """Print human-readable summary"""
    
    print("\n" + "="*70)
    print("DATASET ANALYSIS SUMMARY")
    print("="*70)
    
    print(f"\nTotal Examples: {report['summary']['total_examples']:,}")
    print(f"Total Size: {report['summary']['total_size_bytes'] / 1024 / 1024:.2f} MB")
    
    print("\n📊 Task Distribution:")
    for task, count in report['task_distribution'].items():
        pct = report['task_percentages'][task]
        print(f"  {task:15s}: {count:6,} ({pct:5.1f}%)")
    
    print("\n📋 Format Distribution:")
    for fmt, count in sorted(report['format_distribution'].items(), key=lambda x: -x[1]):
        pct = report['format_percentages'][fmt]
        print(f"  {fmt:25s}: {count:6,} ({pct:5.1f}%)")
    
    if report.get('error_types'):
        print("\n🔧 Error Types (Correction Tasks):")
        for error, count in sorted(report['error_types'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {error:20s}: {count:6,}")
    
    print("\n📏 Size Statistics (characters):")
    size_stats = report['size_statistics']
    print(f"  Min:     {size_stats['min']:8,}")
    print(f"  P25:     {size_stats['p25']:8,}")
    print(f"  Median:  {size_stats['median']:8,}")
    print(f"  Mean:    {size_stats['mean']:8,.0f}")
    print(f"  P75:     {size_stats['p75']:8,}")
    print(f"  P90:     {size_stats['p90']:8,}")
    print(f"  P95:     {size_stats['p95']:8,}")
    print(f"  Max:     {size_stats['max']:8,}")
    
    if report.get('json_size_statistics'):
        print("\n📦 JSON Output Size (characters):")
        json_stats = report['json_size_statistics']
        print(f"  Min:     {json_stats['min']:8,}")
        print(f"  Median:  {json_stats['median']:8,}")
        print(f"  Mean:    {json_stats['mean']:8,.0f}")
        print(f"  Max:     {json_stats['max']:8,}")
    
    print("\n🔍 Schema Presence:")
    schema = report['schema_presence']
    total_schema = schema['with_schema'] + schema['without_schema']
    with_pct = schema['with_schema'] / total_schema * 100 if total_schema > 0 else 0
    print(f"  With schema:    {schema['with_schema']:6,} ({with_pct:5.1f}%)")
    print(f"  Without schema: {schema['without_schema']:6,} ({100-with_pct:5.1f}%)")
    
    print("="*70)

def main():
    dataset_path = Path("datasets/train.jsonl")
    output_path = Path("docs/dataset_analysis.json")
    
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        sys.exit(1)
    
    # Analyze dataset
    stats = analyze_dataset(dataset_path, sample_size=5000)
    
    # Calculate derived statistics
    derived_stats = calculate_statistics(stats)
    
    # Generate report
    report = generate_report(stats, derived_stats, output_path)
    
    # Print summary
    print_summary(report)

if __name__ == '__main__':
    main()

