#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test checkpoint-250 v0.2.0 enhanced"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MODEL = "F:/Node/hivellm/expert/models/Qwen3-0.6B"

TESTS = [
    ('Simple JSON', 'Create JSON: person with name "Alice", age 25, city "Paris"'),
    ('Repair Missing Comma', 'Fix JSON: {"name":"John" "age":30}'),
    ('Schema Generation', 'Create JSON schema for: product with id (number), name (string), price (number)'),
    ('Nested Object', 'Create JSON: user with profile object containing name and email'),
    ('Array', 'Create JSON array with 3 products (id, name, price)'),
]

def test(name, adapter=None):
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    mod = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda", trust_remote_code=True)
    
    if adapter:
        from peft import PeftModel
        mod = PeftModel.from_pretrained(mod, f"../{adapter}")
        print(f"Loaded adapter: {adapter}")
    
    for test_name, p in TESTS:
        prompt = f"<|system|>\nYou are a JSON expert. Output only valid JSON.\n<|end|>\n<|user|>\n{p}\n<|end|>\n<|assistant|>\n"
        inp = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = mod.generate(**inp, max_new_tokens=150, temperature=0.1, do_sample=True, pad_token_id=tok.eos_token_id)
        res = tok.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()
        
        # Remove ChatML artifacts
        if "<|end|>" in res:
            res = res.split("<|end|>")[0].strip()
        
        print(f"\n[{test_name}]")
        print(f"Prompt: {p}")
        print(f"Output: {res[:250]}")
        
        # Quick quality check
        is_json = res.startswith("{") or res.startswith("[")
        has_schema_keywords = "type" in res and "properties" in res
        
        if test_name == "Schema Generation":
            quality = "GOOD" if has_schema_keywords else "BAD (still generating example)"
            print(f"Quality: {quality}")
        elif test_name == "Repair Missing Comma":
            # Check if comma was added (flexible with spaces)
            original_broken = '"John" "age"'  # Missing comma pattern
            has_comma = original_broken not in res and '"age"' in res and '30' in res
            # Also check if it's valid JSON now
            import json
            try:
                json.loads(res)
                quality = "GOOD (fixed comma, valid JSON)"
            except:
                quality = "BAD (still invalid)"
            print(f"Quality: {quality}")
        else:
            quality = "GOOD" if is_json else "BAD"
            print(f"Quality: {quality}")
    
    del mod, tok
    torch.cuda.empty_cache()

print("\n" + "="*60)
print("CHECKPOINT-250 v0.2.0 QUALITY TEST")
print("="*60)

test("CHECKPOINT-250 (v0.2.0 Enhanced)", "weights/qwen3-06b/checkpoint-250")

print("\n" + "="*60)
print("DONE!")
print("="*60)

