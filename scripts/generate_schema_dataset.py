#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate synthetic dataset for text to JSON Schema
Addresses the weakness: model generates examples instead of schemas
"""

import json
import random
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Templates for JSON Schema generation
SCHEMA_TEMPLATES = [
    # Simple object schemas
    {
        "description": "user with name (string) and age (number)",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
    },
    {
        "description": "product with id (number), name (string), and price (number)",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "name": {"type": "string"},
                "price": {"type": "number"}
            },
            "required": ["id", "name", "price"]
        }
    },
    {
        "description": "blog post with title (string), content (string), and published (boolean)",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "published": {"type": "boolean"}
            },
            "required": ["title", "content"]
        }
    },
    # Array schemas
    {
        "description": "list of tags where each tag is a string",
        "schema": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    {
        "description": "array of numbers",
        "schema": {
            "type": "array",
            "items": {"type": "number"}
        }
    },
    # Nested schemas
    {
        "description": "user with name (string), email (string), and address object containing street (string), city (string), and zipcode (string)",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zipcode": {"type": "string"}
                    },
                    "required": ["street", "city"]
                }
            },
            "required": ["name", "email"]
        }
    },
    {
        "description": "product with id (number), name (string), tags (array of strings), and metadata object",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "name": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "metadata": {"type": "object"}
            },
            "required": ["id", "name"]
        }
    },
    # API response schemas
    {
        "description": "API response with status (number), message (string), and data object",
        "schema": {
            "type": "object",
            "properties": {
                "status": {"type": "number"},
                "message": {"type": "string"},
                "data": {"type": "object"}
            },
            "required": ["status"]
        }
    },
    {
        "description": "pagination with page (number), per_page (number), total (number), and items array",
        "schema": {
            "type": "object",
            "properties": {
                "page": {"type": "number"},
                "per_page": {"type": "number"},
                "total": {"type": "number"},
                "items": {"type": "array"}
            },
            "required": ["page", "total", "items"]
        }
    },
]

# Additional variations
ADDITIONAL_SCHEMAS = []

# Generate variations for e-commerce
ecommerce_fields = [
    ("order", ["order_id (string)", "customer_name (string)", "total (number)", "items (array)"]),
    ("customer", ["id (number)", "name (string)", "email (string)", "phone (string)"]),
    ("invoice", ["invoice_number (string)", "date (string)", "amount (number)", "paid (boolean)"]),
]

for entity, fields in ecommerce_fields:
    desc = f"{entity} with " + ", ".join(fields)
    props = {}
    required = []
    
    for field_desc in fields:
        field_name = field_desc.split(" (")[0]
        field_type = field_desc.split("(")[1].rstrip(")")
        
        if field_type == "array":
            props[field_name] = {"type": "array"}
        else:
            props[field_name] = {"type": field_type}
        
        required.append(field_name)
    
    ADDITIONAL_SCHEMAS.append({
        "description": desc,
        "schema": {
            "type": "object",
            "properties": props,
            "required": required
        }
    })

ALL_SCHEMAS = SCHEMA_TEMPLATES + ADDITIONAL_SCHEMAS

# Generate dataset
output = []

for template in ALL_SCHEMAS:
    # Create multiple variations with different prompt styles
    prompts = [
        f"Create JSON schema for: {template['description']}",
        f"Generate JSON schema for {template['description']}",
        f"JSON schema for: {template['description']}",
        f"Define JSON schema: {template['description']}",
    ]
    
    for prompt in prompts:
        output.append({
            "task": "text_to_schema",
            "input": {
                "instruction": "Generate a JSON Schema based on the description. Respond only with the JSON Schema.",
                "description": prompt
            },
            "output": json.dumps(template['schema'], ensure_ascii=False)
        })

# Save dataset
print(f"Generated {len(output)} examples for text to JSON Schema")

# Split train/val/test (80/10/10)
random.shuffle(output)
split_1 = int(len(output) * 0.8)
split_2 = int(len(output) * 0.9)

train = output[:split_1]
val = output[split_1:split_2]
test = output[split_2:]

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

# Save to new dataset directory
import os
os.makedirs("../datasets/text_to_schema", exist_ok=True)

with open("../datasets/text_to_schema/train.jsonl", "w", encoding="utf-8") as f:
    for item in train:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("../datasets/text_to_schema/valid.jsonl", "w", encoding="utf-8") as f:
    for item in val:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("../datasets/text_to_schema/test.jsonl", "w", encoding="utf-8") as f:
    for item in test:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("✅ Dataset saved to datasets/text_to_schema/")
print("\nSample:")
print(json.dumps(train[0], indent=2, ensure_ascii=False))

