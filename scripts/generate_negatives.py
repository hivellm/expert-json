#!/usr/bin/env python3
"""
Negative Examples Generator

Creates invalid JSON examples + corrections for autocorrection training.
For each valid JSON, generates 2-3 corrupted variants.

Target: 30-40k negative examples
"""

import json
import random
import copy
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

OUTPUT_DIR = Path("../datasets/raw/negatives")

def corrupt_missing_field(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Remove a random required field"""
    if not isinstance(obj, dict) or not obj:
        return obj
    
    corrupted = copy.deepcopy(obj)
    if len(corrupted) > 1:
        key_to_remove = random.choice(list(corrupted.keys()))
        del corrupted[key_to_remove]
        return corrupted
    return obj

def corrupt_type_mismatch(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Change type of a random field"""
    if not isinstance(obj, dict) or not obj:
        return obj
    
    corrupted = copy.deepcopy(obj)
    key = random.choice(list(corrupted.keys()))
    value = corrupted[key]
    
    # Type mutations
    if isinstance(value, str):
        corrupted[key] = random.randint(1, 100)
    elif isinstance(value, (int, float)):
        corrupted[key] = str(value)
    elif isinstance(value, bool):
        corrupted[key] = "true" if value else "false"
    elif isinstance(value, list) and value:
        corrupted[key] = value[0]  # Convert array to single item
    elif isinstance(value, dict):
        corrupted[key] = str(value)  # Convert object to string
    
    return corrupted

def corrupt_extra_field(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Add an unknown/unexpected field"""
    if not isinstance(obj, dict):
        return obj
    
    corrupted = copy.deepcopy(obj)
    random_fields = ["unknownField", "extraData", "invalidKey", "_metadata", "tmp"]
    corrupted[random.choice(random_fields)] = random.choice([
        "unexpected value",
        12345,
        True,
        None,
        ["extra", "array"]
    ])
    return corrupted

def corrupt_syntax_error(obj: Any) -> str:
    """Introduce JSON syntax errors"""
    json_str = json.dumps(obj, ensure_ascii=False)
    
    mutations = [
        # Trailing comma in object
        lambda s: s.replace('"}', '",}') if '"}' in s else s,
        # Trailing comma in array
        lambda s: s.replace('"]', ',]') if '"]' in s else s,
        # Unquoted key
        lambda s: s.replace('"key":', 'key:') if '"key":' in s else s.replace('"{', '{') if '"{' in s else s,
        # Single quotes instead of double
        lambda s: s.replace('"', "'", 2) if '"' in s else s,
        # Missing closing brace
        lambda s: s[:-1] if s.endswith('}') else s,
        # Double comma
        lambda s: s.replace(',', ',,', 1) if ',' in s else s
    ]
    
    mutation = random.choice(mutations)
    return mutation(json_str)

def generate_negative_examples(valid_example: Dict[str, Any], example_id: str) -> List[Dict[str, Any]]:
    """Generate 2-3 negative examples from a valid one"""
    negatives = []
    
    # Determine original example data
    original_json = valid_example.get("example", {})
    if not original_json:
        return []
    
    # Choose 2-3 corruption strategies
    num_variants = random.randint(2, 3)
    corruption_funcs = [
        ("missing_field", corrupt_missing_field),
        ("type_mismatch", corrupt_type_mismatch),
        ("extra_field", corrupt_extra_field),
        ("syntax_error", lambda x: corrupt_syntax_error(x))
    ]
    
    selected = random.sample(corruption_funcs, min(num_variants, len(corruption_funcs)))
    
    for corruption_name, corruption_func in selected:
        try:
            if corruption_name == "syntax_error":
                corrupted = corruption_func(original_json)
                is_string = True
            else:
                corrupted = corruption_func(original_json)
                is_string = False
            
            negatives.append({
                "source": f"{valid_example.get('source', 'unknown')}/negative",
                "format": valid_example.get("format", "generic"),
                "corruption_type": corruption_name,
                "task": "fix",
                "invalid_json": corrupted if is_string else json.dumps(corrupted, ensure_ascii=False),
                "valid_json": json.dumps(original_json, ensure_ascii=False),
                "schema": valid_example.get("schema")  # Keep schema for validation
            })
        except Exception:
            continue
    
    return negatives

def process_source_file(source_file: Path) -> List[Dict[str, Any]]:
    """Process a source file and generate negatives"""
    print(f"Processing: {source_file.name}")
    
    all_negatives = []
    valid_count = 0
    
    with open(source_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                valid_example = json.loads(line)
                valid_count += 1
                
                # Generate 2-3 negatives per valid
                negatives = generate_negative_examples(valid_example, f"{source_file.stem}_{line_num}")
                all_negatives.extend(negatives)
                
                if valid_count % 1000 == 0:
                    print(f"  Processed {valid_count} examples, generated {len(all_negatives)} negatives")
            
            except Exception as e:
                continue
    
    print(f"  Total: {valid_count} valid -> {len(all_negatives)} negatives")
    return all_negatives

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all source files
    raw_dir = OUTPUT_DIR.parent
    source_files = []
    
    # APIs.guru
    apis_guru_dir = raw_dir / "apis_guru"
    if apis_guru_dir.exists():
        source_files.extend(list(apis_guru_dir.glob("*.jsonl")))
    
    # SchemaStore
    schemastore_dir = raw_dir / "schemastore"
    if schemastore_dir.exists():
        source_files.extend(list(schemastore_dir.glob("*.jsonl")))
    
    # CloudEvents
    cloudevents_dir = raw_dir / "cloudevents"
    if cloudevents_dir.exists():
        source_files.extend(list(cloudevents_dir.glob("*.jsonl")))
    
    if not source_files:
        print("No source files found. Run collection scripts first.")
        print("Expected files:")
        print("  - datasets/raw/apis_guru/apis_guru_examples.jsonl")
        print("  - datasets/raw/schemastore/schemastore_examples.jsonl")
        print("  - datasets/raw/cloudevents/cloudevents_examples.jsonl")
        return
    
    print(f"Found {len(source_files)} source files")
    
    all_negatives = []
    for source_file in source_files:
        negatives = process_source_file(source_file)
        all_negatives.extend(negatives)
    
    # Save all negative examples
    output_file = OUTPUT_DIR.parent / "negatives" / "negative_examples.jsonl"
    output_file.parent.mkdir(exist_ok=True)
    
    print(f"\n\nSaving {len(all_negatives)} negative examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_negatives:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Statistics by corruption type
    corruption_stats = defaultdict(int)
    for ex in all_negatives:
        corruption_stats[ex.get("corruption_type", "unknown")] += 1
    
    # Save statistics
    stats_file = OUTPUT_DIR.parent / "negatives" / "generation_stats.json"
    stats_data = {
        "total_negatives": len(all_negatives),
        "source_files": len(source_files),
        "corruption_types": dict(corruption_stats)
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("NEGATIVE EXAMPLES GENERATION SUMMARY")
    print("="*60)
    print(f"Source files:           {len(source_files)}")
    print(f"Negatives generated:    {len(all_negatives)}")
    print(f"\nBy corruption type:")
    for corruption_type, count in corruption_stats.items():
        print(f"  {corruption_type:20s}: {count}")
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")

if __name__ == "__main__":
    main()

