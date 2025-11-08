#!/usr/bin/env python3
"""
Generate task distribution chart for the expert-json dataset.

Reads `datasets/metadata.json` and produces a bar chart showing the
number of examples per task type. Output is saved to
`docs/charts/task_distribution.png`.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load_stats(stats_path: Path) -> dict:
    """Load preprocessing statistics JSON."""
    if not stats_path.exists():
        raise FileNotFoundError(f"Statistics file not found: {stats_path}")

    with stats_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def generate_chart(stats: dict, output_path: Path) -> None:
    """Generate and save the bar chart."""
    tasks = stats.get("format_distribution", {})

    if not tasks:
        raise ValueError("No task distribution found in preprocessing stats.")

    labels = list(tasks.keys())
    counts = [tasks[label] for label in labels]
    total = stats.get("processed", sum(counts))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        labels,
        counts,
        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
    )

    ax.set_title(f"Expert-JSON Dataset Task Distribution (Total: {total:,})")
    ax.set_xlabel("Task Type")
    ax.set_ylabel("Number of Examples")
    ax.bar_label(bars, labels=[f"{count:,}" for count in counts], padding=3)

    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    stats_path = Path("datasets/preprocessing_stats.json")
    output_path = Path("docs/charts/task_distribution.png")

    stats = load_stats(stats_path)
    generate_chart(stats, output_path)

    print(f"Saved chart to {output_path}")


if __name__ == "__main__":
    main()

