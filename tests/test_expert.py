#!/usr/bin/env python3
"""
Test trained expert to validate learning
Compares base model vs fine-tuned expert
"""

import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from pathlib import Path

def test_expert(base_model_path: str, adapter_path: str, test_cases: list[dict]):
    """
    Test expert performance on JSON parsing tasks
    
    Args:
        base_model_path: Path to base model
        adapter_path: Path to trained adapter
        test_cases: List of test prompts and expected behaviors
    """
    
    print("=" * 70)
    print("Expert Validation Test")
    print("=" * 70)
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    
    # Load expert (base + adapter)
    print("Loading expert adapter...")
    expert_model = PeftModel.from_pretrained(base_model, adapter_path)
    expert_model.eval()
    
    print("\n" + "=" * 70)
    print("Running Tests")
    print("=" * 70)
    
    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 70}")
        print(f"Test #{i}: {test_case['name']}")
        print(f"{'-' * 70}")
        
        prompt = test_case['prompt']
        print(f"Prompt:\n{prompt}\n")
        
        # Generate with expert
        inputs = tokenizer(prompt, return_tensors="pt").to(expert_model.device)
        
        with torch.no_grad():
            outputs = expert_model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        print(f"Expert Response:\n{response}\n")
        
        # Check if response matches expected behavior
        passed = test_case['check'](response)
        
        if passed:
            print("[PASSED]")
            results["passed"] += 1
        else:
            print("[FAILED]")
            results["failed"] += 1
        
        results["details"].append({
            "test": test_case['name'],
            "passed": passed,
            "prompt": prompt,
            "response": response
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Passed: {results['passed']}/{len(test_cases)}")
    print(f"Failed: {results['failed']}/{len(test_cases)}")
    print(f"Success Rate: {results['passed']/len(test_cases)*100:.1f}%")
    print("=" * 70)
    
    return results


# Test cases for JSON parsing expert
TEST_CASES = [
    {
        "name": "Simple JSON Parsing",
        "prompt": """### Instruction:
Parse this JSON and extract the 'name' field.

### Input:
{"name": "John Doe", "age": 30}

### Response:
""",
        "check": lambda r: "John" in r or "name" in r.lower()
    },
    {
        "name": "Nested JSON Extraction",
        "prompt": """### Instruction:
Extract the city from this nested JSON.

### Input:
{"user": {"address": {"city": "New York", "zip": "10001"}}}

### Response:
""",
        "check": lambda r: "New York" in r or "city" in r.lower()
    },
    {
        "name": "JSON Validation",
        "prompt": """### Instruction:
Is this valid JSON? Answer yes or no.

### Input:
{"valid": true, "test": 123}

### Response:
""",
        "check": lambda r: "yes" in r.lower() or "valid" in r.lower()
    },
    {
        "name": "Invalid JSON Detection",
        "prompt": """### Instruction:
Is this valid JSON? Answer yes or no.

### Input:
{invalid: missing quotes}

### Response:
""",
        "check": lambda r: "no" in r.lower() or "invalid" in r.lower()
    },
    {
        "name": "Array Handling",
        "prompt": """### Instruction:
How many items are in this JSON array?

### Input:
{"items": [1, 2, 3, 4, 5]}

### Response:
""",
        "check": lambda r: "5" in r or "five" in r.lower()
    }
]


if __name__ == "__main__":
    import sys
    
    # Paths (relative to expert directory)
    base_model_path = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
    expert_dir = Path(__file__).parent.parent
    adapter_path = str(expert_dir / "weights" / "adapter")
    
    # Check if paths exist
    if not Path(base_model_path).exists():
        print(f"ERROR: Base model not found: {base_model_path}")
        sys.exit(1)
    
    if not Path(adapter_path).exists():
        print(f"ERROR: Adapter not found: {adapter_path}")
        sys.exit(1)
    
    # Run tests
    results = test_expert(base_model_path, adapter_path, TEST_CASES)
    
    # Exit code based on results
    sys.exit(0 if results["failed"] == 0 else 1)

