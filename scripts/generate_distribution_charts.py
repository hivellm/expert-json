#!/usr/bin/env python3
"""
Generate distribution charts for Expert-JSON dataset
Similar to SQL and Neo4j distribution analysis scripts
"""
import json
import re
from collections import Counter
from pathlib import Path
import sys

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
except ImportError:
    print("Error: matplotlib not installed. Install with: pip install matplotlib")
    sys.exit(1)

def extract_format_from_chatml(text: str) -> str:
    """Extract format type from ChatML format"""
    if not text:
        return "generic"
    
    # Look for Format: in system message
    format_match = re.search(r'Format:\s*(\w+)', text)
    if format_match:
        return format_match.group(1).lower()
    
    return "generic"

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
    
    formats = Counter()
    tasks = Counter()
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
                
                # Extract format
                format_type = extract_format_from_chatml(text)
                formats[format_type] += 1
                
                # Extract task type
                task = extract_task_from_chatml(text)
                tasks[task] += 1
                
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
        "formats": formats,
        "tasks": tasks,
        "complexity": complexity_levels,
        "total": total,
        "empty": empty_count
    }

def plot_format_distribution(formats: Counter, output_dir: Path):
    """Plot format distribution (bar and pie charts)"""
    # Sort by count
    sorted_formats = sorted(formats.items(), key=lambda x: -x[1])
    
    labels = [fmt.replace('_', ' ').title() for fmt, _ in sorted_formats]
    values = [count for _, count in sorted_formats]
    percentages = [count / sum(values) * 100 for count in values]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Bar chart
    colors_bar = plt.cm.viridis(np.linspace(0.3, 0.9, len(labels)))
    bars = ax1.barh(labels, values, color=colors_bar)
    
    # Add value labels
    for i, (bar, value, pct) in enumerate(zip(bars, values, percentages)):
        ax1.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,} ({pct:.1f}%)',
                va='center', fontsize=10, weight='bold')
    
    ax1.set_xlabel('Number of Examples', fontsize=12, weight='bold')
    ax1.set_title('Format Distribution (Bar Chart)', fontsize=14, weight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='x', alpha=0.3)
    
    # Pie chart
    colors_pie = plt.cm.viridis(np.linspace(0.3, 0.9, len(labels)))
    wedges, texts, autotexts = ax2.pie(
        values,
        labels=labels,
        colors=colors_pie,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    
    ax2.set_title('Format Distribution (Pie Chart)', fontsize=14, weight='bold')
    
    plt.tight_layout()
    
    # Save as PNG and PDF
    plt.savefig(output_dir / "dataset_distribution.png", dpi=300, bbox_inches="tight")
    try:
        plt.savefig(output_dir / "dataset_distribution.pdf", bbox_inches="tight")
    except PermissionError:
        print(f"  Warning: Could not save PDF (file may be open)")
    
    plt.close()
    
    print(f"  Saved: dataset_distribution.png")
    print(f"  Saved: dataset_distribution.pdf")

def plot_task_distribution(tasks: Counter, output_dir: Path):
    """Plot task distribution"""
    sorted_tasks = sorted(tasks.items(), key=lambda x: -x[1])
    
    labels = [task.replace('_', ' ').title() for task, _ in sorted_tasks]
    values = [count for _, count in sorted_tasks]
    percentages = [count / sum(values) * 100 for count in values]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart
    colors = plt.cm.Set3(np.linspace(0.2, 0.8, len(labels)))
    bars = ax1.bar(labels, values, color=colors)
    
    for bar, value, pct in zip(bars, values, percentages):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:,}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=11, weight='bold')
    
    ax1.set_ylabel('Number of Examples', fontsize=12, weight='bold')
    ax1.set_title('Task Distribution (Bar Chart)', fontsize=14, weight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='y', alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(
        values,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    ax2.set_title('Task Distribution (Pie Chart)', fontsize=14, weight='bold')
    
    plt.tight_layout()
    
    plt.savefig(output_dir / "task_distribution.png", dpi=300, bbox_inches="tight")
    try:
        plt.savefig(output_dir / "task_distribution.pdf", bbox_inches="tight")
    except PermissionError:
        print(f"  Warning: Could not save PDF (file may be open)")
    
    plt.close()
    
    print(f"  Saved: task_distribution.png")
    print(f"  Saved: task_distribution.pdf")

def plot_complexity_distribution(complexity: Counter, output_dir: Path):
    """Plot complexity distribution"""
    # Order: simple, medium, complex, very_complex
    order = ["simple", "medium", "complex", "very_complex"]
    sorted_complexity = [(k, complexity.get(k, 0)) for k in order if k in complexity]
    
    labels = [comp.replace('_', ' ').title() for comp, _ in sorted_complexity]
    values = [count for _, count in sorted_complexity]
    percentages = [count / sum(values) * 100 for count in values]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(labels)))
    bars = ax1.bar(labels, values, color=colors)
    
    for bar, value, pct in zip(bars, values, percentages):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:,}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=11, weight='bold')
    
    ax1.set_ylabel('Number of Examples', fontsize=12, weight='bold')
    ax1.set_title('Complexity Distribution (Bar Chart)', fontsize=14, weight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(
        values,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    ax2.set_title('Complexity Distribution (Pie Chart)', fontsize=14, weight='bold')
    
    plt.tight_layout()
    
    plt.savefig(output_dir / "complexity_distribution.png", dpi=300, bbox_inches="tight")
    try:
        plt.savefig(output_dir / "complexity_distribution.pdf", bbox_inches="tight")
    except PermissionError:
        print(f"  Warning: Could not save PDF (file may be open)")
    
    plt.close()
    
    print(f"  Saved: complexity_distribution.png")
    print(f"  Saved: complexity_distribution.pdf")

def main():
    dataset_path = Path("datasets/train.jsonl")
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not dataset_path.exists():
        print(f"[ERROR] Dataset not found: {dataset_path}")
        return
    
    # Analyze dataset
    analysis_results = load_and_analyze_dataset(dataset_path)
    formats = analysis_results["formats"]
    tasks = analysis_results["tasks"]
    complexity = analysis_results["complexity"]
    total = analysis_results["total"]
    empty = analysis_results["empty"]
    
    valid_total = total - empty
    
    print(f"\nTotal valid examples: {valid_total:,}")
    
    # Generate charts
    print(f"\nGenerating charts in {output_dir}/...")
    plot_format_distribution(formats, output_dir)
    plot_task_distribution(tasks, output_dir)
    plot_complexity_distribution(complexity, output_dir)
    
    # Print summary
    print("\n" + "="*80)
    print("DISTRIBUTION SUMMARY")
    print("="*80)
    
    print("\n[FORMAT DISTRIBUTION]")
    print("-" * 80)
    for fmt, count in formats.most_common():
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {fmt:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n[TASK DISTRIBUTION]")
    print("-" * 80)
    for task, count in tasks.most_common():
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {task:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n[COMPLEXITY DISTRIBUTION]")
    print("-" * 80)
    for comp, count in complexity.most_common():
        pct = (count / valid_total * 100) if valid_total > 0 else 0
        print(f"  {comp:20s}: {count:8,} ({pct:5.2f}%)")
    
    print("\n" + "="*80)
    print(f"Charts saved to: {output_dir}/")
    print("="*80)

if __name__ == "__main__":
    main()

