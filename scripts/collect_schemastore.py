#!/usr/bin/env python3
"""
SchemaStore.org Collector

Fetches JSON Schema files from SchemaStore and generates valid examples.
SchemaStore contains schemas for common tools and configurations.

Target: 15-20k examples
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Any
import random
import time
from collections import defaultdict

OUTPUT_DIR = Path("../datasets/raw/schemastore")
CATALOG_URL = "https://www.schemastore.org/api/json/catalog.json"

def fetch_catalog() -> Dict[str, Any]:
    """Fetch SchemaStore catalog"""
    print("Fetching SchemaStore catalog...")
    response = requests.get(CATALOG_URL, timeout=30)
    response.raise_for_status()
    return response.json()

def download_schema(url: str) -> Dict[str, Any]:
    """Download JSON Schema"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def generate_example_from_schema(schema: Dict[str, Any], depth: int = 0, force_complete: bool = False) -> Any:
    """Generate a valid example from JSON Schema
    
    Args:
        force_complete: If True, generate more complete objects (not minimal)
    """
    if depth > 10:  # Prevent infinite recursion
        return None
    
    schema_type = schema.get("type")
    
    # Handle examples in schema (prefer these)
    if "examples" in schema and schema["examples"]:
        return random.choice(schema["examples"])
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    if "const" in schema:
        return schema["const"]
    
    # Handle enum
    if "enum" in schema:
        return random.choice(schema["enum"])
    
    # Generate by type
    if schema_type == "string":
        if "format" in schema:
            # Common string formats
            formats = {
                "email": "user@example.com",
                "uri": "https://example.com/api/v1",
                "url": "https://example.com",
                "date": "2025-11-06",
                "date-time": "2025-11-06T12:00:00Z",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "ipv4": "192.168.1.1",
                "ipv6": "2001:db8::1",
                "hostname": "api.example.com",
                "json-pointer": "/path/to/field"
            }
            return formats.get(schema["format"], "example-string")
        
        # Generate realistic strings based on pattern/description
        if "pattern" in schema:
            return "example-value"
        return "example-string-value"
    
    elif schema_type == "number" or schema_type == "integer":
        minimum = schema.get("minimum", 1)
        maximum = schema.get("maximum", 100)
        return random.randint(int(minimum), min(int(maximum), 1000))
    
    elif schema_type == "boolean":
        return random.choice([True, False])
    
    elif schema_type == "null":
        return None
    
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 2 if force_complete else 1)
        max_items = schema.get("maxItems", 5 if force_complete else 3)
        count = random.randint(min_items, min(max_items, 5))
        return [generate_example_from_schema(items_schema, depth + 1, force_complete) for _ in range(count)]
    
    elif schema_type == "object" or ("properties" in schema):
        obj = {}
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Add ALL required properties
        for prop_name in required:
            if prop_name in properties:
                obj[prop_name] = generate_example_from_schema(properties[prop_name], depth + 1, force_complete)
        
        # Add MORE optional properties if force_complete
        optional = [p for p in properties.keys() if p not in required]
        if force_complete:
            # Add 50-80% of optional properties
            num_optional = max(3, int(len(optional) * random.uniform(0.5, 0.8)))
        else:
            # Add 2-3 optional properties
            num_optional = min(len(optional), random.randint(2, 3))
        
        if optional:
            selected_optional = random.sample(optional, min(num_optional, len(optional)))
            for prop_name in selected_optional:
                obj[prop_name] = generate_example_from_schema(properties[prop_name], depth + 1, force_complete)
        
        return obj
    
    # Handle anyOf/oneOf/allOf
    if "anyOf" in schema:
        return generate_example_from_schema(random.choice(schema["anyOf"]), depth + 1)
    if "oneOf" in schema:
        return generate_example_from_schema(random.choice(schema["oneOf"]), depth + 1)
    if "allOf" in schema:
        # Merge all schemas (simplified)
        merged = {}
        for subschema in schema["allOf"]:
            example = generate_example_from_schema(subschema, depth + 1)
            if isinstance(example, dict):
                merged.update(example)
        return merged
    
    return {}

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch catalog
    catalog = fetch_catalog()
    schemas_list = catalog.get("schemas", [])
    print(f"Found {len(schemas_list)} schemas in catalog")
    
    all_examples = []
    stats = defaultdict(int)
    
    # Process each schema
    for idx, schema_info in enumerate(schemas_list):
        try:
            name = schema_info.get("name", f"schema_{idx}")
            url = schema_info.get("url")
            
            if not url:
                stats["no_url"] += 1
                continue
            
            print(f"\n[{idx+1}/{len(schemas_list)}] Processing: {name}")
            
            # Download schema
            schema = download_schema(url)
            stats["schemas_downloaded"] += 1
            
            # Generate multiple examples per schema (variety)
            # Alternate between minimal and complete examples
            num_examples = random.randint(4, 6)
            for i in range(num_examples):
                try:
                    # Force complete object for half of examples
                    force_complete = (i % 2 == 0)
                    example_data = generate_example_from_schema(schema, force_complete=force_complete)
                    
                    if example_data is not None:
                        # Filter out tiny/useless examples
                        ex_str = json.dumps(example_data, ensure_ascii=False)
                        if len(ex_str) < 30:  # Skip very small
                            stats["too_small"] += 1
                            continue
                        
                        all_examples.append({
                            "source": f"schemastore/{name}",
                            "format": "json_schema",
                            "schema_name": name,
                            "schema": schema,
                            "example": example_data,
                            "task": "generate",
                            "variant": "complete" if force_complete else "minimal"
                        })
                        stats["examples_generated"] += 1
                except Exception as e:
                    stats["generation_errors"] += 1
                    if stats["generation_errors"] < 10:
                        print(f"  Generation error: {e}")
            
            print(f"  Generated: {num_examples} examples")
            
            # Rate limiting
            if idx % 20 == 0 and idx > 0:
                time.sleep(1)
        
        except Exception as e:
            stats["errors"] += 1
            print(f"  Error: {e}")
            continue
    
    # Save all examples
    output_file = OUTPUT_DIR / "schemastore_examples.jsonl"
    print(f"\n\nSaving {len(all_examples)} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats_file = OUTPUT_DIR / "collection_stats.json"
    stats_data = {
        "total_schemas": len(schemas_list),
        "schemas_downloaded": stats["schemas_downloaded"],
        "examples_generated": len(all_examples),
        "generation_errors": stats["generation_errors"],
        "errors": stats["errors"],
        "skipped": {
            "no_url": stats["no_url"]
        }
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("SCHEMASTORE COLLECTION SUMMARY")
    print("="*60)
    print(f"Total schemas:          {len(schemas_list)}")
    print(f"Schemas downloaded:     {stats['schemas_downloaded']}")
    print(f"Examples generated:     {len(all_examples)}")
    print(f"Generation errors:      {stats['generation_errors']}")
    print(f"Errors:                 {stats['errors']}")
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")

if __name__ == "__main__":
    main()

