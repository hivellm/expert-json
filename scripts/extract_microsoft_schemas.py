#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract JSON Schemas from Microsoft repository
Generate text-to-schema training examples from real schemas
"""

import json
import os
import sys
import io
from pathlib import Path

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MICROSOFT_SCHEMAS_PATH = Path("../datasets/raw/microsoft_schemas")
OUTPUT_PATH = Path("../datasets/microsoft_text_to_schema")

def extract_schema_description(schema_data, schema_path):
    """Generate natural language description from JSON Schema"""
    
    # Get schema metadata
    title = schema_data.get("title", "")
    description = schema_data.get("description", "")
    schema_type = schema_data.get("type", "object")
    
    # Build description from path and title
    path_parts = Path(schema_path).parts
    product = path_parts[0] if len(path_parts) > 0 else "unknown"
    
    # Start with title or generate from path
    if title:
        desc_parts = [title]
    elif description:
        desc_parts = [description.split(".")[0]]  # First sentence
    else:
        # Generate from filename
        filename = Path(schema_path).stem.replace("-", " ").replace("_", " ")
        desc_parts = [f"{product} {filename}"]
    
    # Add properties description
    if schema_type == "object" and "properties" in schema_data:
        props = schema_data["properties"]
        
        # Get key properties (limit to first 5 for readability)
        prop_list = []
        for i, (key, value) in enumerate(props.items()):
            if i >= 5:
                prop_list.append("...")
                break
            
            prop_type = value.get("type", "any")
            required = key in schema_data.get("required", [])
            
            if prop_type == "array":
                item_type = value.get("items", {}).get("type", "any")
                prop_desc = f"{key} (array of {item_type})"
            elif prop_type == "object":
                prop_desc = f"{key} (object)"
            else:
                prop_desc = f"{key} ({prop_type})"
            
            if required:
                prop_desc += " [required]"
            
            prop_list.append(prop_desc)
        
        if prop_list:
            desc_parts.append("with " + ", ".join(prop_list))
    
    return " ".join(desc_parts)

def should_include_schema(schema_data):
    """Filter schemas that are good for training"""
    # Must be object type
    if schema_data.get("type") != "object":
        return False
    
    # Must have properties
    if "properties" not in schema_data:
        return False
    
    # Must have at least 2 properties
    if len(schema_data.get("properties", {})) < 2:
        return False
    
    # Schema shouldn't be too complex (< 50 properties)
    if len(schema_data.get("properties", {})) > 50:
        return False
    
    # Convert to JSON and check size (< 10KB)
    schema_str = json.dumps(schema_data, ensure_ascii=False)
    if len(schema_str) > 10000:
        return False
    
    return True

def extract_schemas():
    """Extract all valid schemas from Microsoft repository"""
    examples = []
    skipped = 0
    
    print(f"Scanning {MICROSOFT_SCHEMAS_PATH}...")
    
    for schema_file in MICROSOFT_SCHEMAS_PATH.rglob("*.json"):
        # Skip test files and package.json
        if "test" in str(schema_file).lower() or "package" in str(schema_file).lower():
            continue
        
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            
            # Check if it's a valid JSON Schema
            if not should_include_schema(schema_data):
                skipped += 1
                continue
            
            # Generate description
            rel_path = schema_file.relative_to(MICROSOFT_SCHEMAS_PATH)
            description = extract_schema_description(schema_data, str(rel_path))
            
            # Create training example
            examples.append({
                "task": "text_to_schema",
                "input": {
                    "instruction": "Generate a JSON Schema based on the description. Respond only with the JSON Schema.",
                    "description": f"Create JSON schema for: {description}"
                },
                "output": json.dumps(schema_data, ensure_ascii=False),
                "source": "microsoft_json_schemas",
                "source_file": str(rel_path)
            })
            
        except Exception as e:
            skipped += 1
            continue
    
    print(f"Extracted {len(examples)} valid schemas")
    print(f"Skipped {skipped} files")
    
    return examples

def main():
    if not MICROSOFT_SCHEMAS_PATH.exists():
        print("ERROR: Microsoft schemas not found")
        print(f"Expected at: {MICROSOFT_SCHEMAS_PATH}")
        print("Run: git clone https://github.com/microsoft/json-schemas datasets/raw/microsoft_schemas")
        return
    
    examples = extract_schemas()
    
    if not examples:
        print("No schemas extracted!")
        return
    
    # Split train/val/test
    import random
    random.shuffle(examples)
    
    split_1 = int(len(examples) * 0.8)
    split_2 = int(len(examples) * 0.9)
    
    train = examples[:split_1]
    val = examples[split_1:split_2]
    test = examples[split_2:]
    
    print(f"\nSplits: Train={len(train)}, Val={len(val)}, Test={len(test)}")
    
    # Save
    OUTPUT_PATH.mkdir(exist_ok=True)
    
    with open(OUTPUT_PATH / "train.jsonl", "w", encoding="utf-8") as f:
        for ex in train:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    
    with open(OUTPUT_PATH / "valid.jsonl", "w", encoding="utf-8") as f:
        for ex in val:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    
    with open(OUTPUT_PATH / "test.jsonl", "w", encoding="utf-8") as f:
        for ex in test:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    
    # Metadata
    metadata = {
        "source": "https://github.com/microsoft/json-schemas",
        "total_schemas": len(examples),
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "date_extracted": "2025-11-06"
    }
    
    with open(OUTPUT_PATH / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nDataset saved to: {OUTPUT_PATH}")
    
    # Show samples
    print("\nSample examples:")
    for i, ex in enumerate(train[:3], 1):
        print(f"\n{i}. {ex['input']['description'][:80]}...")
        print(f"   Output schema size: {len(ex['output'])} chars")
        print(f"   Source: {ex['source_file']}")

if __name__ == "__main__":
    main()

