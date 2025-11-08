#!/usr/bin/env python3
"""
Hard Test Cases - Tasks the base model should fail
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from pathlib import Path
import json


def generate_response(model, tokenizer, prompt: str, max_tokens: int = 200) -> str:
    """Generate response from model"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for more focused answers
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    )
    return response.strip()


def test_json_repair(response: str) -> bool:
    """Check if response contains repaired JSON"""
    try:
        # Look for JSON in response
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            parsed = json.loads(json_str)
            # Check if quotes were added
            return "name" in parsed
    except:
        pass
    return False


# Comprehensive test suite - 25 tests
HARD_TESTS = [
    # Basic Extraction (5 tests)
    {
        "name": "Extract Nested Email",
        "prompt": """### Instruction:
Extract the email from this nested JSON.

### Input:
{"user": {"profile": {"contact": {"email": "test@example.com"}}}}

### Response:
""",
        "check": lambda r: "test@example.com" in r
    },
    {
        "name": "Extract Array Element by Index",
        "prompt": """### Instruction:
Get the second element from the tags array.

### Input:
{"tags": ["python", "rust", "javascript"]}

### Response:
""",
        "check": lambda r: "rust" in r.lower()
    },
    {
        "name": "Count Nested Objects",
        "prompt": """### Instruction:
How many objects are in the entities array?

### Input:
{"entities": [{"type": "Function"}, {"type": "Class"}, {"type": "Module"}]}

### Response:
""",
        "check": lambda r: "3" in r or "three" in r.lower()
    },
    {
        "name": "Extract Multiple Fields",
        "prompt": """### Instruction:
Extract both name and version fields.

### Input:
{"name": "expert-json", "version": "1.0.0", "author": "hivellm"}

### Response:
""",
        "check": lambda r: ("expert-json" in r or "json" in r) and "1.0.0" in r
    },
    {
        "name": "Find Maximum Value",
        "prompt": """### Instruction:
What is the maximum value in the scores array?

### Input:
{"scores": [85, 92, 78, 95, 88]}

### Response:
""",
        "check": lambda r: "95" in r
    },
    
    # Complex Structures (5 tests)
    {
        "name": "Deep Nesting - 5 Levels",
        "prompt": """### Instruction:
Extract the value of 'secret_key' from this deeply nested JSON.

### Input:
{"data": {"user": {"security": {"credentials": {"keys": {"secret_key": "xyz789"}}}}}}

### Response:
""",
        "check": lambda r: "xyz789" in r
    },
    {
        "name": "Array of Objects - Extract All Names",
        "prompt": """### Instruction:
Extract all names from this array of user objects.

### Input:
{"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]}

### Response:
""",
        "check": lambda r: ("Alice" in r and "Bob" in r and "Charlie" in r)
    },
    {
        "name": "Mixed Array Types",
        "prompt": """### Instruction:
How many different data types are in this array?

### Input:
[1, "text", true, null, {"key": "value"}, [1, 2]]

### Response:
""",
        "check": lambda r: "5" in r or "6" in r or "five" in r.lower() or "six" in r.lower()
    },
    {
        "name": "Filter by Type",
        "prompt": """### Instruction:
Extract only the number values from this object.

### Input:
{"a": 10, "b": "text", "c": 20, "d": true, "e": 30}

### Response:
""",
        "check": lambda r: ("10" in r and "20" in r and "30" in r)
    },
    {
        "name": "Parse Classification Result",
        "prompt": """### Instruction:
Extract the domain and confidence from the classification result.

### Input:
{"result": {"classification": {"template": "software", "confidence": 0.95, "domain": "tech"}}}

### Response:
""",
        "check": lambda r: ("tech" in r.lower() or "domain" in r.lower()) and ("95" in r or "0.95" in r)
    },
    
    # Validation Tasks (5 tests)
    {
        "name": "Type Detection - Number",
        "prompt": """### Instruction:
What is the data type of the 'count' field?

### Input:
{"count": 42, "name": "test"}

### Response:
""",
        "check": lambda r: "number" in r.lower() or "integer" in r.lower() or "int" in r.lower()
    },
    {
        "name": "Type Detection - Array",
        "prompt": """### Instruction:
What is the data type of the 'items' field?

### Input:
{"items": [1, 2, 3]}

### Response:
""",
        "check": lambda r: "array" in r.lower() or "list" in r.lower()
    },
    {
        "name": "Empty Object Detection",
        "prompt": """### Instruction:
Is this JSON object empty? Answer yes or no.

### Input:
{}

### Response:
""",
        "check": lambda r: "yes" in r.lower() or "empty" in r.lower()
    },
    {
        "name": "Non-Empty Object",
        "prompt": """### Instruction:
Is this JSON object empty? Answer yes or no.

### Input:
{"key": "value"}

### Response:
""",
        "check": lambda r: "no" in r.lower() or "not empty" in r.lower()
    },
    {
        "name": "Duplicate Keys",
        "prompt": """### Instruction:
Does this JSON have duplicate keys?

### Input:
{"name": "Alice", "age": 30, "name": "Bob"}

### Response:
""",
        "check": lambda r: "yes" in r.lower() or "duplicate" in r.lower()
    },
    
    # Extraction & Transformation (5 tests)
    {
        "name": "Extract All Keys",
        "prompt": """### Instruction:
List all keys in this JSON object.

### Input:
{"name": "Alice", "age": 30, "city": "NYC"}

### Response:
""",
        "check": lambda r: ("name" in r and "age" in r and "city" in r)
    },
    {
        "name": "Count Relationships",
        "prompt": """### Instruction:
How many relationships are in the graph?

### Input:
{"relationships": [{"type": "IMPORTS"}, {"type": "CONTAINS"}, {"type": "CALLS"}]}

### Response:
""",
        "check": lambda r: "3" in r or "three" in r.lower()
    },
    {
        "name": "Extract Entity Types",
        "prompt": """### Instruction:
List all unique entity types.

### Input:
{"entities": [{"type": "Module"}, {"type": "Function"}, {"type": "Module"}, {"type": "Class"}]}

### Response:
""",
        "check": lambda r: ("Module" in r or "module" in r.lower()) and ("Function" in r or "function" in r.lower()) and ("Class" in r or "class" in r.lower())
    },
    {
        "name": "Parse Performance Metrics",
        "prompt": """### Instruction:
Extract the total time and token count.

### Input:
{"performance": {"totalTimeMs": 33358, "tokens": {"total": 25534}}}

### Response:
""",
        "check": lambda r: ("33358" in r or "33" in r) and ("25534" in r or "25" in r)
    },
    {
        "name": "Extract Configuration Values",
        "prompt": """### Instruction:
What are the rank and alpha values?

### Input:
{"lora_config": {"rank": 16, "alpha": 16, "dropout": 0.05}}

### Response:
""",
        "check": lambda r: "16" in r
    },
    
    # Advanced Tasks (5 tests)
    {
        "name": "Calculate Percentage",
        "prompt": """### Instruction:
What percentage of parameters are trainable?

### Input:
{"params": {"total": 599719936, "trainable": 3670016}}

### Response:
""",
        "check": lambda r: "0.6" in r or "0.61" in r or "1%" in r or "less than 1" in r.lower()
    },
    {
        "name": "Filter by Condition",
        "prompt": """### Instruction:
List all public functions.

### Input:
{"functions": [{"name": "new", "visibility": "public"}, {"name": "parse", "visibility": "private"}, {"name": "validate", "visibility": "public"}]}

### Response:
""",
        "check": lambda r: ("new" in r.lower() and "validate" in r.lower()) and "parse" not in r.lower()
    },
    {
        "name": "Aggregate Values",
        "prompt": """### Instruction:
What is the sum of all numeric values?

### Input:
{"a": 10, "b": "text", "c": 20, "d": 30}

### Response:
""",
        "check": lambda r: "60" in r or "sixty" in r.lower()
    },
    {
        "name": "Parse Timestamp",
        "prompt": """### Instruction:
Extract the created_at timestamp.

### Input:
{"created_at": 1609459200, "updated_at": 1641081600}

### Response:
""",
        "check": lambda r: "1609459200" in r
    },
    {
        "name": "Extract Nested Array Length",
        "prompt": """### Instruction:
How many tags does the first user have?

### Input:
{"users": [{"tags": ["admin", "dev", "active"]}, {"tags": ["user"]}]}

### Response:
""",
        "check": lambda r: "3" in r or "three" in r.lower()
    }
]


if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("HARD TESTS: Base Model vs Expert")
    print("=" * 70)
    print("\nThese tests are designed to be difficult for the base model.")
    print("A good expert should significantly outperform the base.\n")
    
    # Paths (relative to expert directory when running from there)
    base_model_path = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
    expert_dir = Path(__file__).parent.parent  # tests/ -> expert-json-parser/
    adapter_path = expert_dir / "weights" / "adapter"
    
    # Check paths
    if not Path(base_model_path).exists():
        print(f"ERROR: Base model not found: {base_model_path}")
        sys.exit(1)
    
    if not Path(adapter_path).exists():
        print(f"ERROR: Adapter not found: {adapter_path}")
        sys.exit(1)
    
    # Load models
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    base_model.eval()
    
    print("Loading expert...")
    expert_model = PeftModel.from_pretrained(base_model, adapter_path)
    expert_model.eval()
    
    print("\n" + "=" * 70)
    print("Running Tests")
    print("=" * 70)
    
    base_passed = 0
    expert_passed = 0
    
    for i, test in enumerate(HARD_TESTS, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST #{i}: {test['name']}")
        print(f"{'=' * 70}")
        print(f"Prompt: {test['prompt'][:100]}...")
        
        # Base model
        base_resp = generate_response(base_model, tokenizer, test['prompt'])
        base_pass = test['check'](base_resp)
        print(f"\nBase:   {'[PASS]' if base_pass else '[FAIL]'} - {base_resp[:80]}...")
        if base_pass:
            base_passed += 1
        
        # Expert model
        expert_resp = generate_response(expert_model, tokenizer, test['prompt'])
        expert_pass = test['check'](expert_resp)
        print(f"Expert: {'[PASS]' if expert_pass else '[FAIL]'} - {expert_resp[:80]}...")
        if expert_pass:
            expert_passed += 1
        
        if expert_pass and not base_pass:
            print(">> EXPERT WINS!")
        elif not expert_pass and base_pass:
            print(">> BASE WINS (unexpected)")
        elif expert_pass and base_pass:
            print(">> TIE (both passed)")
        else:
            print(">> TIE (both failed)")
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Base Model:   {base_passed}/{len(HARD_TESTS)} passed ({base_passed/len(HARD_TESTS)*100:.0f}%)")
    print(f"Expert Model: {expert_passed}/{len(HARD_TESTS)} passed ({expert_passed/len(HARD_TESTS)*100:.0f}%)")
    
    improvement = expert_passed - base_passed
    if improvement > 0:
        print(f"\nCONCLUSION: Expert is BETTER by +{improvement} tests!")
        print("Training was SUCCESSFUL!")
    elif improvement == 0:
        print(f"\nCONCLUSION: Same performance")
        print("Need more training data or harder tasks to see improvement")
    else:
        print(f"\nCONCLUSION: Base is better (unexpected)")
        print("May indicate overfitting or poor training data")
    
    print("=" * 70)

