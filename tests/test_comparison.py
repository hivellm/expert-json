#!/usr/bin/env python3
"""
A/B Test: Base Model vs Expert
Compares performance to validate training impact
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from pathlib import Path


def generate_response(model, tokenizer, prompt: str, max_tokens: int = 150) -> str:
    """Generate response from model"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    )
    return response.strip()


def run_comparison(base_model_path: str, adapter_path: str, test_cases: list[dict]):
    """
    Compare base model vs expert on same tasks
    """
    
    print("=" * 70)
    print("A/B TEST: Base Model vs Expert")
    print("=" * 70)
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    print("Loading base model (Qwen3-0.6B)...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.bfloat16,
    )
    base_model.eval()
    
    # Load expert
    print("Loading expert (Base + LoRA adapter)...")
    expert_model = PeftModel.from_pretrained(base_model, adapter_path)
    expert_model.eval()
    
    print("\n" + "=" * 70)
    print("Running Comparative Tests")
    print("=" * 70)
    
    base_scores = {"passed": 0, "failed": 0}
    expert_scores = {"passed": 0, "failed": 0}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST #{i}: {test_case['name']}")
        print(f"{'=' * 70}")
        
        prompt = test_case['prompt']
        print(f"\nPrompt:\n{'-' * 70}\n{prompt}\n{'-' * 70}")
        
        # Test BASE MODEL
        print("\n[BASE MODEL]")
        base_response = generate_response(base_model, tokenizer, prompt, max_tokens=100)
        print(f"Response:\n{base_response[:200]}...")  # Limit output
        base_passed = test_case['check'](base_response)
        print(f"Result: {'[PASS]' if base_passed else '[FAIL]'}")
        
        if base_passed:
            base_scores["passed"] += 1
        else:
            base_scores["failed"] += 1
        
        # Test EXPERT MODEL
        print("\n[EXPERT MODEL]")
        expert_response = generate_response(expert_model, tokenizer, prompt, max_tokens=100)
        print(f"Response:\n{expert_response[:200]}...")  # Limit output
        expert_passed = test_case['check'](expert_response)
        print(f"Result: {'[PASS]' if expert_passed else '[FAIL]'}")
        
        if expert_passed:
            expert_scores["passed"] += 1
        else:
            expert_scores["failed"] += 1
        
        # Comparison
        if expert_passed and not base_passed:
            print("\n>> EXPERT IMPROVED! Expert passed where base failed.")
        elif base_passed and not expert_passed:
            print("\n>> EXPERT REGRESSED! Base passed but expert failed.")
        elif base_passed and expert_passed:
            print("\n>> BOTH PASSED")
        else:
            print("\n>> BOTH FAILED")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)
    print(f"\nBase Model:   {base_scores['passed']}/{len(test_cases)} passed ({base_scores['passed']/len(test_cases)*100:.0f}%)")
    print(f"Expert Model: {expert_scores['passed']}/{len(test_cases)} passed ({expert_scores['passed']/len(test_cases)*100:.0f}%)")
    
    improvement = expert_scores['passed'] - base_scores['passed']
    if improvement > 0:
        print(f"\n>> IMPROVEMENT: +{improvement} tests! Expert is BETTER!")
    elif improvement < 0:
        print(f"\n>> REGRESSION: {improvement} tests. Expert is WORSE!")
    else:
        print(f"\n>> NO CHANGE: Same performance")
    
    print("=" * 70)
    
    return {
        "base": base_scores,
        "expert": expert_scores,
        "improvement": improvement
    }


# Test cases
TEST_CASES = [
    {
        "name": "Extract Name Field",
        "prompt": """### Instruction:
Parse this JSON and extract the 'name' field.

### Input:
{"name": "Alice Smith", "age": 25}

### Response:
""",
        "check": lambda r: "Alice" in r or "Smith" in r
    },
    {
        "name": "Extract Nested Field",
        "prompt": """### Instruction:
Extract the email from this nested JSON.

### Input:
{"user": {"profile": {"email": "test@example.com"}}}

### Response:
""",
        "check": lambda r: "test@example.com" in r or "email" in r.lower()
    },
    {
        "name": "Count Array Items",
        "prompt": """### Instruction:
How many items are in the 'tags' array?

### Input:
{"tags": ["python", "rust", "javascript"]}

### Response:
""",
        "check": lambda r: "3" in r or "three" in r.lower()
    },
]


if __name__ == "__main__":
    import sys
    
    # Paths (relative to expert directory)
    base_model_path = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
    expert_dir = Path(__file__).parent.parent
    adapter_path = str(expert_dir / "weights" / "adapter")
    
    # Check paths
    if not Path(base_model_path).exists():
        print(f"ERROR: Base model not found: {base_model_path}")
        sys.exit(1)
    
    if not Path(adapter_path).exists():
        print(f"ERROR: Adapter not found: {adapter_path}")
        print("Train the expert first: .\\train_windows.ps1")
        sys.exit(1)
    
    # Run comparison
    results = run_comparison(base_model_path, adapter_path, TEST_CASES)
    
    # Exit with success if expert improved
    sys.exit(0 if results["improvement"] >= 0 else 1)

