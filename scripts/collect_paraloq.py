#!/usr/bin/env python3
"""
Paraloq JSON Data Extraction Collector

Downloads paraloq/json_data_extraction from HuggingFace.
High-quality dataset (484 examples) for text → JSON extraction.

Covers 8 domains:
- Medical (patient records, prescriptions)
- Manufacturing (BOMs, work orders, COAs)
- Travel (bookings, reservations)
- Business (invoices, contracts)
- E-commerce (products, orders)
- Media (reviews, albums)
- Technology (licenses, API responses)
- Simple (to-do lists, recipes)

Target: 484 examples
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

OUTPUT_DIR = Path("../datasets/raw/paraloq")

def load_paraloq_dataset() -> List[Dict[str, Any]]:
    """Load dataset from HuggingFace"""
    try:
        from datasets import load_dataset
        print("Loading paraloq/json_data_extraction from HuggingFace...")
        ds = load_dataset("paraloq/json_data_extraction", split="train")
        print(f"Loaded {len(ds)} examples")
        return list(ds)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("\nMake sure 'datasets' is installed:")
        print("  pip install datasets")
        return []

def convert_to_format(example: Dict[str, Any]) -> Dict[str, Any]:
    """Convert paraloq format to our unified format"""
    
    # Parse schema (it's a string in the dataset)
    schema_str = example.get("schema", "{}")
    try:
        schema = json.loads(schema_str)
    except:
        schema = {}
    
    # Parse item (target JSON, also a string)
    item_str = example.get("item", "{}")
    try:
        item = json.loads(item_str)
    except:
        item = {}
    
    return {
        "source": f"paraloq/{example.get('topic', 'unknown')}",
        "format": "data_extraction",
        "topic": example.get("topic"),
        "title": example.get("title"),
        "medium": example.get("medium"),
        "schema": schema,
        "example": item,  # The extracted JSON
        "text": example.get("text"),  # The unstructured text
        "task": "extract",  # New task type: extract JSON from text
        "schema_name": example.get("title")
    }

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load dataset
    raw_examples = load_paraloq_dataset()
    
    if not raw_examples:
        return
    
    # Convert to our format
    all_examples = []
    stats = defaultdict(int)
    
    print("\nConverting to unified format...")
    
    for idx, example in enumerate(raw_examples):
        try:
            converted = convert_to_format(example)
            all_examples.append(converted)
            
            # Track statistics
            stats["total"] += 1
            stats[f"topic_{converted.get('topic', 'unknown')}"] += 1
            stats[f"medium_{converted.get('medium', 'unknown')}"] += 1
            
        except Exception as e:
            stats["errors"] += 1
            print(f"  Error converting example {idx}: {e}")
    
    # Save all examples
    output_file = OUTPUT_DIR / "paraloq_examples.jsonl"
    print(f"\nSaving {len(all_examples)} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats_file = OUTPUT_DIR / "collection_stats.json"
    
    # Extract topic and medium distributions
    topic_dist = {k.replace('topic_', ''): v for k, v in stats.items() if k.startswith('topic_')}
    medium_dist = {k.replace('medium_', ''): v for k, v in stats.items() if k.startswith('medium_')}
    
    stats_data = {
        "total_examples": len(all_examples),
        "errors": stats["errors"],
        "topics": topic_dist,
        "mediums": medium_dist,
        "source": "paraloq/json_data_extraction (HuggingFace)"
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("PARALOQ COLLECTION SUMMARY")
    print("="*60)
    print(f"Total examples:         {len(all_examples)}")
    print(f"Errors:                 {stats['errors']}")
    
    print(f"\nBy topic:")
    for topic, count in sorted(topic_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(all_examples)) * 100
        print(f"  {topic:15s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nBy medium:")
    for medium, count in sorted(medium_dist.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / len(all_examples)) * 100
        print(f"  {medium:20s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")
    
    print(f"\n" + "="*60)
    print("DATASET VALUE")
    print("="*60)
    print("[OK] High-quality curated data (Gemini-Pro generated)")
    print("[OK] 8 diverse domains (medical, manufacturing, travel, etc.)")
    print("[OK] Text extraction task (complements generation tasks)")
    print("[OK] Real-world scenarios with unstructured input")
    print("[OK] Will significantly improve data extraction capabilities")

if __name__ == "__main__":
    main()

