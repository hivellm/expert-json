#!/usr/bin/env python3
"""Quick manual test of JSON expert checkpoints"""

import sys
import os
# No need to append path, running from expert-json dir

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_PATH = "F:/Node/hivellm/expert/models/Qwen3-0.6B"

# Test just 3 key checkpoints
TESTS = [
    'Create a JSON object for a person with name "Alice", age 25, and city "Paris"',
    'Fix this JSON: {"name": "John" "age": 30}',
    'Create JSON schema for a product with id, name, price, and tags array',
]

def test_checkpoint(name, adapter_path=None):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.bfloat16,
        device_map="cuda",
        trust_remote_code=True
    )
    
    if adapter_path:
        from peft import PeftModel
        # Adjust path since we're in scripts/ directory
        full_path = os.path.join("..", adapter_path)
        model = PeftModel.from_pretrained(model, full_path)
    
    for i, prompt in enumerate(TESTS, 1):
        formatted = f"<|system|>\nYou are a JSON expert. Output only valid JSON.\n<|end|>\n<|user|>\n{prompt}\n<|end|>\n<|assistant|>\n"
        
        inputs = tokenizer(formatted, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        print(f"\nTest {i}: {prompt[:60]}...")
        print(f"Output: {response[:200]}")
    
    del model
    del tokenizer
    torch.cuda.empty_cache()

# Test base and final only for quick comparison
print("Starting quick comparison test...")
test_checkpoint("Base Model", None)
test_checkpoint("Final Checkpoint", "weights/qwen3-06b/final")
print("\n✅ Quick test complete!")

