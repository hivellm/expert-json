#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate synthetic dataset for JSON repair
Addresses the weakness: model doesn't fix missing commas and syntax errors
"""

import json
import random
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Common JSON syntax errors and their fixes
ERROR_PATTERNS = []

# 1. Missing commas between properties
base_objects = [
    ('{"name": "John", "age": 30}', '{"name": "John" "age": 30}'),
    ('{"id": 1, "title": "Test", "active": true}', '{"id": 1 "title": "Test" "active": true}'),
    ('{"x": 10, "y": 20, "z": 30}', '{"x": 10 "y": 20 "z": 30}'),
    ('{"email": "test@example.com", "verified": true, "role": "admin"}', '{"email": "test@example.com" "verified": true "role": "admin"}'),
]

for correct, broken in base_objects:
    ERROR_PATTERNS.append({
        "error_type": "missing_comma_properties",
        "broken": broken,
        "fixed": correct,
        "description": "Missing comma between object properties"
    })

# 2. Missing commas in arrays
array_errors = [
    ('[1, 2, 3, 4]', '[1 2 3 4]'),
    ('["apple", "banana", "orange"]', '["apple" "banana" "orange"]'),
    ('[{"id": 1}, {"id": 2}]', '[{"id": 1} {"id": 2}]'),
    ('[true, false, null]', '[true false null]'),
]

for correct, broken in array_errors:
    ERROR_PATTERNS.append({
        "error_type": "missing_comma_array",
        "broken": broken,
        "fixed": correct,
        "description": "Missing comma between array elements"
    })

# 3. Trailing commas
trailing_errors = [
    ('{"name": "John", "age": 30}', '{"name": "John", "age": 30,}'),
    ('[1, 2, 3]', '[1, 2, 3,]'),
    ('{"items": [1, 2], "count": 2}', '{"items": [1, 2,], "count": 2}'),
]

for correct, broken in trailing_errors:
    ERROR_PATTERNS.append({
        "error_type": "trailing_comma",
        "broken": broken,
        "fixed": correct,
        "description": "Trailing comma before closing bracket"
    })

# 4. Missing quotes on keys
quote_errors = [
    ('{"name": "value"}', '{name: "value"}'),
    ('{"id": 123, "active": true}', '{id: 123, active: true}'),
    ('{"key1": "val1", "key2": "val2"}', '{key1: "val1", key2: "val2"}'),
]

for correct, broken in quote_errors:
    ERROR_PATTERNS.append({
        "error_type": "unquoted_keys",
        "broken": broken,
        "fixed": correct,
        "description": "Missing quotes on object keys"
    })

# 5. Single quotes instead of double quotes
single_quote_errors = [
    ('{"name": "John"}', "{'name': 'John'}"),
    ('{"items": ["a", "b"]}', "{'items': ['a', 'b']}"),
]

for correct, broken in single_quote_errors:
    ERROR_PATTERNS.append({
        "error_type": "single_quotes",
        "broken": broken,
        "fixed": correct,
        "description": "Single quotes instead of double quotes"
    })

# 6. Multiple errors combined
combined_errors = [
    ('{"name": "John", "age": 30, "city": "NYC"}', '{name: "John" age: 30 "city": "NYC",}'),
    ('{"id": 1, "items": ["a", "b"]}', '{id: 1, "items": ["a" "b",]}'),
]

for correct, broken in combined_errors:
    ERROR_PATTERNS.append({
        "error_type": "multiple_errors",
        "broken": broken,
        "fixed": correct,
        "description": "Multiple syntax errors"
    })

# Generate dataset
output = []

for pattern in ERROR_PATTERNS:
    # Create variations
    prompts = [
        f"Fix this JSON: {pattern['broken']}",
        f"Correct this malformed JSON: {pattern['broken']}",
        f"Repair this JSON syntax: {pattern['broken']}",
        f"Fix JSON syntax errors: {pattern['broken']}",
    ]
    
    for prompt in prompts:
        output.append({
            "task": "json_repair",
            "input": {
                "instruction": "Fix the JSON syntax errors. Respond only with the corrected JSON.",
                "broken_json": pattern['broken'],
                "error_type": pattern['error_type']
            },
            "output": pattern['fixed']
        })

print(f"Generated {len(output)} JSON repair examples")

# Shuffle and split
random.shuffle(output)
split_1 = int(len(output) * 0.8)
split_2 = int(len(output) * 0.9)

train = output[:split_1]
val = output[split_1:split_2]
test = output[split_2:]

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

# Save to new enhanced repair dataset
import os

os.makedirs("../datasets/json_repair_enhanced", exist_ok=True)

with open("../datasets/json_repair_enhanced/train.jsonl", "w", encoding="utf-8") as f:
    for item in train:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("../datasets/json_repair_enhanced/valid.jsonl", "w", encoding="utf-8") as f:
    for item in val:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("../datasets/json_repair_enhanced/test.jsonl", "w", encoding="utf-8") as f:
    for item in test:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"Enhanced json_repair dataset: {len(train)} total examples")
print("\nSample:")
print(json.dumps(train[0], indent=2, ensure_ascii=False))

