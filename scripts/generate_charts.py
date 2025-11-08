#!/usr/bin/env python3
"""
Generate charts and visualizations for Expert-JSON dataset
"""
import json
from pathlib import Path
import sys

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Warning: matplotlib not installed. Install with: pip install matplotlib")
    sys.exit(1)

def load_analysis(analysis_path):
    """Load dataset analysis JSON"""
    with open(analysis_path, 'r') as f:
        return json.load(f)

def create_task_distribution_chart(report, output_dir):
    """Create task distribution pie chart"""
    tasks = report['task_distribution']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    labels = [task.replace('_', ' ').title() for task in tasks.keys()]
    values = list(tasks.values())
    percentages = [report['task_percentages'][task] for task in tasks.keys()]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )
    
    # Add legend with counts
    legend_labels = [f"{label}: {value:,}" for label, value in zip(labels, values)]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    
    ax.set_title('Task Distribution in Expert-JSON Dataset', fontsize=16, weight='bold', pad=20)
    
    plt.tight_layout()
    output_path = output_dir / 'task_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated: {output_path}")

def create_format_distribution_chart(report, output_dir):
    """Create format distribution bar chart"""
    formats = report['format_distribution']
    
    # Sort by count
    sorted_formats = sorted(formats.items(), key=lambda x: -x[1])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = [fmt.replace('_', ' ').title() for fmt, _ in sorted_formats]
    values = [count for _, count in sorted_formats]
    percentages = [report['format_percentages'][fmt] for fmt, _ in sorted_formats]
    
    # Create horizontal bar chart
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(labels)))
    bars = ax.barh(labels, values, color=colors)
    
    # Add value labels
    for i, (bar, value, pct) in enumerate(zip(bars, values, percentages)):
        ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,} ({pct:.1f}%)',
                va='center', fontsize=10, weight='bold')
    
    ax.set_xlabel('Number of Examples', fontsize=12, weight='bold')
    ax.set_title('Format Distribution in Expert-JSON Dataset', fontsize=16, weight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    output_path = output_dir / 'format_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated: {output_path}")

def create_size_distribution_chart(report, output_dir):
    """Create size distribution chart"""
    size_stats = report['size_statistics']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Box plot
    box_data = [
        size_stats['min'],
        size_stats['p25'],
        size_stats['median'],
        size_stats['p75'],
        size_stats['max']
    ]
    
    bp = ax1.boxplot([box_data], vert=False, widths=0.5, patch_artist=True,
                      boxprops=dict(facecolor='#3498db', alpha=0.7),
                      medianprops=dict(color='red', linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5))
    
    ax1.set_xlabel('Example Size (characters)', fontsize=12, weight='bold')
    ax1.set_title('Example Size Distribution (Box Plot)', fontsize=14, weight='bold')
    ax1.set_yticks([])
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='x', alpha=0.3)
    
    # Add percentile labels
    percentiles = ['Min', 'P25', 'Median', 'P75', 'Max']
    for label, value in zip(percentiles, box_data):
        ax1.axvline(value, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
        ax1.text(value, 1.3, f'{label}\n{value:,}', ha='center', fontsize=9)
    
    # Statistics summary
    stats_labels = ['Min', 'P25', 'Median', 'Mean', 'P75', 'P90', 'P95', 'Max']
    stats_values = [
        size_stats['min'],
        size_stats['p25'],
        size_stats['median'],
        size_stats['mean'],
        size_stats['p75'],
        size_stats['p90'],
        size_stats['p95'],
        size_stats['max']
    ]
    
    colors_bar = plt.cm.Blues(np.linspace(0.4, 0.9, len(stats_labels)))
    bars = ax2.barh(stats_labels, stats_values, color=colors_bar)
    
    # Add value labels
    for bar, value in zip(bars, stats_values):
        ax2.text(value + max(stats_values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,.0f}',
                va='center', fontsize=10, weight='bold')
    
    ax2.set_xlabel('Size (characters)', fontsize=12, weight='bold')
    ax2.set_title('Size Statistics Summary', fontsize=14, weight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    output_path = output_dir / 'size_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated: {output_path}")

def create_error_types_chart(report, output_dir):
    """Create error types chart for correction tasks"""
    error_types = report.get('error_types', {})
    
    if not error_types:
        print("⚠ No error types data available")
        return
    
    # Sort by count
    sorted_errors = sorted(error_types.items(), key=lambda x: -x[1])[:10]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = [err.replace('_', ' ').title() for err, _ in sorted_errors]
    values = [count for _, count in sorted_errors]
    
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(labels)))
    bars = ax.barh(labels, values, color=colors)
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax.text(value + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,}',
                va='center', fontsize=10, weight='bold')
    
    ax.set_xlabel('Number of Examples', fontsize=12, weight='bold')
    ax.set_title('Top Error Types in Correction Tasks', fontsize=16, weight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    output_path = output_dir / 'error_types.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated: {output_path}")

def create_overview_dashboard(report, output_dir):
    """Create comprehensive overview dashboard"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    # Title
    fig.suptitle('Expert-JSON Dataset Overview Dashboard', fontsize=20, weight='bold', y=0.98)
    
    # 1. Summary stats (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    
    total = report['summary']['total_examples']
    total_size = report['summary']['total_size_bytes'] / 1024 / 1024
    
    summary_text = f"""
    📊 DATASET SUMMARY
    
    Total Examples: {total:,}
    Total Size: {total_size:.1f} MB
    Avg Size: {total_size / total * 1024:.1f} KB
    
    Tasks:
    • Generation: {report['task_distribution'].get('generation', 0):,}
    • Extraction: {report['task_distribution'].get('extraction', 0):,}
    • Correction: {report['task_distribution'].get('correction', 0):,}
    """
    
    ax1.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # 2. Task distribution pie (top center + right)
    ax2 = fig.add_subplot(gs[0, 1:])
    
    tasks = report['task_distribution']
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    labels = [task.replace('_', ' ').title() for task in tasks.keys()]
    values = list(tasks.values())
    
    wedges, texts, autotexts = ax2.pie(
        values,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    ax2.set_title('Task Distribution', fontsize=14, weight='bold')
    
    # 3. Format distribution (middle row)
    ax3 = fig.add_subplot(gs[1, :])
    
    formats = report['format_distribution']
    sorted_formats = sorted(formats.items(), key=lambda x: -x[1])[:8]
    
    labels = [fmt.replace('_', '\n').title() for fmt, _ in sorted_formats]
    values = [count for _, count in sorted_formats]
    
    colors_bar = plt.cm.viridis(np.linspace(0.3, 0.9, len(labels)))
    bars = ax3.bar(labels, values, color=colors_bar)
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:,}',
                ha='center', va='bottom', fontsize=10, weight='bold')
    
    ax3.set_ylabel('Number of Examples', fontsize=11, weight='bold')
    ax3.set_title('Format Distribution (Top 8)', fontsize=14, weight='bold')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.tick_params(axis='x', labelsize=9)
    
    # 4. Size percentiles (bottom left)
    ax4 = fig.add_subplot(gs[2, :2])
    
    size_stats = report['size_statistics']
    percentile_labels = ['Min', 'P25', 'Median', 'P75', 'P90', 'P95', 'Max']
    percentile_values = [
        size_stats['min'],
        size_stats['p25'],
        size_stats['median'],
        size_stats['p75'],
        size_stats['p90'],
        size_stats['p95'],
        size_stats['max']
    ]
    
    colors_perc = plt.cm.Blues(np.linspace(0.4, 0.9, len(percentile_labels)))
    bars = ax4.barh(percentile_labels, percentile_values, color=colors_perc)
    
    for bar, value in zip(bars, percentile_values):
        ax4.text(value + max(percentile_values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:,.0f}',
                va='center', fontsize=9, weight='bold')
    
    ax4.set_xlabel('Size (characters)', fontsize=11, weight='bold')
    ax4.set_title('Example Size Distribution', fontsize=14, weight='bold')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    
    # 5. Schema presence (bottom right)
    ax5 = fig.add_subplot(gs[2, 2])
    
    schema = report['schema_presence']
    schema_labels = ['With\nSchema', 'Without\nSchema']
    schema_values = [schema['with_schema'], schema['without_schema']]
    schema_colors = ['#2ecc71', '#95a5a6']
    
    wedges, texts, autotexts = ax5.pie(
        schema_values,
        labels=schema_labels,
        colors=schema_colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    ax5.set_title('Schema Presence', fontsize=14, weight='bold')
    
    plt.tight_layout()
    output_path = output_dir / 'overview_dashboard.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Generated: {output_path}")

def main():
    analysis_path = Path('docs/dataset_analysis.json')
    output_dir = Path('docs/charts')
    
    if not analysis_path.exists():
        print(f"Error: Analysis file not found at {analysis_path}")
        print("Run analyze_dataset.py first")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load analysis
    print(f"Loading analysis from {analysis_path}...")
    report = load_analysis(analysis_path)
    
    print(f"\nGenerating charts in {output_dir}/...\n")
    
    # Generate charts
    create_overview_dashboard(report, output_dir)
    create_task_distribution_chart(report, output_dir)
    create_format_distribution_chart(report, output_dir)
    create_size_distribution_chart(report, output_dir)
    create_error_types_chart(report, output_dir)
    
    print(f"\n✓ All charts generated successfully in {output_dir}/")

if __name__ == '__main__':
    main()

