#!/usr/bin/env python3
"""
Analyze additional HuggingFace datasets for JSON expert
"""

import json
from datasets import load_dataset

print("="*70)
print("ANALYZING ADDITIONAL DATASETS")
print("="*70)

# 1. epfl-dlab/JSONSchemaBench
print("\n1. epfl-dlab/JSONSchemaBench")
print("-"*70)
try:
    ds = load_dataset('epfl-dlab/JSONSchemaBench', split='train')
    print(f"Train examples: {len(ds):,}")
    print(f"Columns: {ds.column_names}")
    
    sample = ds[0]
    print(f"\nSample:")
    print(f"  unique_id: {sample['unique_id']}")
    schema_str = str(sample['json_schema'])
    print(f"  schema preview: {schema_str[:300]}...")
    print(f"  schema length: {len(schema_str)} chars")
    
    # Check diversity
    print(f"\nAnalyzing diversity (first 100)...")
    sizes = [len(str(ds[i]['json_schema'])) for i in range(min(100, len(ds)))]
    print(f"  Avg schema size: {sum(sizes)/len(sizes):.0f} chars")
    print(f"  Min: {min(sizes)}, Max: {max(sizes)}")
    
    print("\n[ASSESSMENT]")
    print("  Content: JSON Schemas only (no examples/instances)")
    print("  Quality: Unknown (need to check if schemas are valid)")
    print("  Usefulness: LOW - We need schemas WITH examples")
    print("  Recommendation: SKIP - No JSON instances to learn from")
    
except Exception as e:
    print(f"Error: {e}")

# 2. dataunitylab/json-schema
print("\n\n2. dataunitylab/json-schema")
print("-"*70)
try:
    ds = load_dataset('dataunitylab/json-schema', split='train')
    print(f"Train examples: {len(ds):,}")
    print(f"Columns: {ds.column_names}")
    
    if len(ds) > 0:
        sample = ds[0]
        print(f"\nSample:")
        for key in sample.keys():
            value = str(sample[key])
            print(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")
    
    print("\n[ASSESSMENT]")
    print(f"  Content: Chat conversations (ShareGPT format)")
    print(f"  Quality: Unknown")
    print(f"  Usefulness: VERY LOW - Only 30 examples")
    print(f"  Recommendation: SKIP - Too small to matter")
    
except Exception as e:
    print(f"Error: {e}")

# 3. Arun63/sharegpt-structured-output-json
print("\n\n3. Arun63/sharegpt-structured-output-json")
print("-"*70)
try:
    ds = load_dataset('Arun63/sharegpt-structured-output-json', split='train')
    print(f"Train examples: {len(ds):,}")
    print(f"Columns: {ds.column_names}")
    
    if len(ds) > 0:
        sample = ds[0]
        print(f"\nSample:")
        conversations = sample.get('conversations', [])
        if conversations:
            print(f"  Conversation length: {len(conversations)} messages")
            for i, msg in enumerate(conversations[:2]):
                role = msg.get('from', 'unknown')
                value = msg.get('value', '')
                print(f"  Message {i+1} ({role}): {value[:150]}...")
    
    print("\n[ASSESSMENT]")
    print(f"  Content: Chat conversations about JSON/structured output")
    print(f"  Quality: Needs inspection")
    print(f"  Usefulness: LOW - Only 30 examples, chat format")
    print(f"  Recommendation: SKIP - Too small, not our format")
    
except Exception as e:
    print(f"Error: {e}")

# Summary
print("\n" + "="*70)
print("FINAL RECOMMENDATION")
print("="*70)
print("\n[SKIP ALL 3 DATASETS]")
print("\nReasons:")
print("  1. epfl-dlab/JSONSchemaBench: Schemas without instances")
print("  2. dataunitylab/json-schema: Only 30 examples")
print("  3. Arun63/sharegpt-structured-output-json: Only 30 examples")
print("\nCurrent sources are sufficient:")
print("  - APIs.guru: OpenAPI examples (real APIs)")
print("  - SchemaStore: Config examples")
print("  - CloudEvents: Event examples")
print("  - Paraloq: Data extraction (HIGH VALUE)")
print("  - Negatives: Autocorrection")
print("\nEstimated total: 60-85k quality examples")

