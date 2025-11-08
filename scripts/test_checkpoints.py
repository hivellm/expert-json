#!/usr/bin/env python3
"""
Qualitative analysis of JSON expert checkpoints
Tests various JSON operations across different checkpoints
"""

import sys
import os
# Running from expert-json directory

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json

# Ensure we're in Windows venv for CUDA
MODEL_PATH = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
# Paths relative to expert-json root (parent of scripts/)
CHECKPOINTS = [
    ("Base", None),
    ("checkpoint-64", "../weights/qwen3-06b/checkpoint-64"),
    ("checkpoint-96", "../weights/qwen3-06b/checkpoint-96"),
    ("checkpoint-250", "../weights/qwen3-06b/checkpoint-250"),
    ("final", "../weights/qwen3-06b/final"),
]

# Test cases covering different JSON capabilities
TEST_CASES = [
    {
        "id": 1,
        "name": "Simple Object Creation",
        "prompt": 'Create a JSON object for a person with name "John", age 30, and city "NYC"',
        "capability": "basic_object",
    },
    {
        "id": 2,
        "name": "Nested Object",
        "prompt": "Create a JSON object with user info (name, email) and address (street, city, zip)",
        "capability": "nested_structure",
    },
    {
        "id": 3,
        "name": "Array of Objects",
        "prompt": "Create a JSON array with 3 products, each having id, name, and price",
        "capability": "array_handling",
    },
    {
        "id": 4,
        "name": "Schema from Description",
        "prompt": "Generate JSON schema for a blog post with title (string), content (string), tags (array), and metadata (object)",
        "capability": "schema_generation",
    },
    {
        "id": 5,
        "name": "JSON Repair - Missing Comma",
        "prompt": 'Fix this JSON: {"name": "John" "age": 30}',
        "capability": "syntax_repair",
    },
    {
        "id": 6,
        "name": "JSON Repair - Trailing Comma",
        "prompt": 'Fix this JSON: {"items": [1, 2, 3,]}',
        "capability": "syntax_repair",
    },
    {
        "id": 7,
        "name": "JSON Transform - Flatten",
        "prompt": 'Transform this nested JSON to flat: {"user": {"name": "Alice", "age": 25}}',
        "capability": "transformation",
    },
    {
        "id": 8,
        "name": "Complex API Response",
        "prompt": "Create a JSON API response for user authentication with token, expires_in, refresh_token, and user object",
        "capability": "api_structure",
    },
    {
        "id": 9,
        "name": "JSON with Special Characters",
        "prompt": 'Create JSON for a message with text: "Hello\\nWorld" and emoji: "👋"',
        "capability": "special_chars",
    },
    {
        "id": 10,
        "name": "JSON Schema Validation",
        "prompt": 'Create JSON schema that validates: {"temperature": 23.5, "unit": "celsius", "timestamp": "2024-01-01T10:00:00Z"}',
        "capability": "schema_validation",
    },
    {
        "id": 11,
        "name": "Error Message Format",
        "prompt": "Create a JSON error response with code 404, message, and details array",
        "capability": "error_handling",
    },
    {
        "id": 12,
        "name": "Pagination Structure",
        "prompt": "Create a JSON pagination response with data array, total, page, per_page, and has_more",
        "capability": "pagination",
    },
    {
        "id": 13,
        "name": "Deeply Nested Object",
        "prompt": "Create a JSON with user.profile.settings.preferences.theme.colors object structure",
        "capability": "deep_nesting",
    },
    {
        "id": 14,
        "name": "Mixed Types Array",
        "prompt": "Create a JSON array with mixed types: string, number, boolean, object, null",
        "capability": "type_handling",
    },
    {
        "id": 15,
        "name": "Date/Time Formats",
        "prompt": 'Create JSON with various date formats: ISO8601, Unix timestamp, and readable format',
        "capability": "datetime_handling",
    },
]

def load_model(checkpoint_path=None):
    """Load model with optional adapter"""
    print(f"Loading model from {MODEL_PATH}...")
    
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        dtype=torch.bfloat16,
        device_map="cuda",
        trust_remote_code=True
    )
    
    if checkpoint_path:
        print(f"Loading adapter from {checkpoint_path}...")
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, checkpoint_path)
    
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_tokens=200):
    """Generate response for a prompt"""
    # Format with ChatML
    formatted_prompt = f"<|system|>\nYou are a JSON expert. Output only valid JSON, no explanations.\n<|end|>\n<|user|>\n{prompt}\n<|end|>\n<|assistant|>\n"
    
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.1,  # Low for consistency
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return response.strip()

def is_valid_json(text):
    """Check if text is valid JSON"""
    try:
        json.loads(text)
        return True
    except:
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                try:
                    json.loads(text[start:end].strip())
                    return True
                except:
                    pass
        return False

def score_response(prompt_info, response):
    """Score response based on quality (0-10)"""
    score = 0.0
    
    # Basic validity (5 points)
    if is_valid_json(response):
        score += 5.0
    elif "```json" in response:
        score += 2.0  # At least tried to format
    
    # Relevance to capability (3 points)
    capability = prompt_info["capability"]
    response_lower = response.lower()
    
    if capability == "basic_object" and "{" in response and "}" in response:
        score += 3.0
    elif capability == "nested_structure" and response.count("{") >= 2:
        score += 3.0
    elif capability == "array_handling" and "[" in response and "]" in response:
        score += 3.0
    elif capability == "schema_generation" and ("type" in response_lower or "properties" in response_lower):
        score += 3.0
    elif capability == "syntax_repair" and is_valid_json(response):
        score += 3.0
    elif capability == "transformation" and is_valid_json(response):
        score += 3.0
    else:
        score += 1.0  # Partial credit
    
    # Conciseness (2 points) - penalize too verbose responses
    if len(response) < 500:
        score += 2.0
    elif len(response) < 1000:
        score += 1.0
    
    return min(score, 10.0)

def analyze_checkpoint(name, checkpoint_path):
    """Analyze a single checkpoint"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {name}")
    print(f"{'='*80}\n")
    
    model, tokenizer = load_model(checkpoint_path)
    
    results = []
    total_score = 0.0
    
    for test in TEST_CASES:
        print(f"\n--- Test {test['id']}: {test['name']} ---")
        print(f"Prompt: {test['prompt'][:80]}...")
        
        response = generate_response(model, tokenizer, test['prompt'])
        score = score_response(test, response)
        
        print(f"Score: {score:.1f}/10")
        print(f"Response: {response[:150]}...")
        if len(response) > 150:
            print("  ...")
        
        results.append({
            "test_id": test["id"],
            "name": test["name"],
            "capability": test["capability"],
            "score": score,
            "response": response[:200],  # Truncate for storage
        })
        
        total_score += score
    
    avg_score = total_score / len(TEST_CASES)
    
    print(f"\n{'='*80}")
    print(f"CHECKPOINT: {name}")
    print(f"AVERAGE SCORE: {avg_score:.2f}/10")
    print(f"{'='*80}\n")
    
    # Cleanup
    del model
    del tokenizer
    torch.cuda.empty_cache()
    
    return {
        "checkpoint": name,
        "avg_score": avg_score,
        "results": results,
    }

def main():
    """Run analysis on all checkpoints"""
    all_results = []
    
    for name, path in CHECKPOINTS:
        result = analyze_checkpoint(name, path)
        all_results.append(result)
    
    # Save results to parent directory (expert-json root)
    output_file = "../checkpoint_analysis_json.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    for result in all_results:
        print(f"{result['checkpoint']:20s}: {result['avg_score']:.2f}/10")
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Find best checkpoint
    best = max(all_results, key=lambda x: x["avg_score"])
    print(f"\n🏆 BEST CHECKPOINT: {best['checkpoint']} ({best['avg_score']:.2f}/10)")

if __name__ == "__main__":
    main()

