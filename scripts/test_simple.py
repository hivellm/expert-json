#!/usr/bin/env python3
"""Teste qualitativo simples - Base vs Final"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL = "F:/Node/hivellm/expert/models/Qwen3-0.6B"

TESTS = [
    'Create JSON: person with name "Alice", age 25',
    'Fix JSON: {"name":"John" "age":30}',
    'JSON schema for: product with id, name, price',
]

def test(name, adapter=None):
    print(f"\n{'='*50}\n{name}\n{'='*50}")
    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    mod = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda", trust_remote_code=True)
    
    if adapter:
        from peft import PeftModel
        mod = PeftModel.from_pretrained(mod, f"../{adapter}")
    
    for i, p in enumerate(TESTS, 1):
        prompt = f"<|system|>\nYou are a JSON expert. Output only valid JSON.\n<|end|>\n<|user|>\n{p}\n<|end|>\n<|assistant|>\n"
        inp = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = mod.generate(**inp, max_new_tokens=100, temperature=0.1, do_sample=True, pad_token_id=tok.eos_token_id)
        res = tok.decode(out[0][inp['input_ids'].shape[1]:], skip_special_tokens=True)
        print(f"\n{i}. {p}")
        print(f"Output: {res[:200]}")
    
    del mod, tok
    torch.cuda.empty_cache()

test("BASE MODEL", None)
test("FINAL CHECKPOINT", "weights/qwen3-06b/final")
print("\n✅ Done!")

