#!/usr/bin/env python3
"""
Collect JSON examples from bigcode/the-stack dataset.

This script:
1. Loads files from the-stack that contain JSON
2. Extracts valid JSON objects/arrays
3. Extracts invalid JSON (for correction training)
4. Formats examples in ChatML format

Requires HuggingFace token:
- Get token from https://huggingface.co/settings/tokens
- Accept dataset terms at https://huggingface.co/datasets/bigcode/the-stack
- Set HF_TOKEN environment variable or use huggingface-cli login
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from tqdm import tqdm
import argparse


def is_valid_json(text: str) -> bool:
    """Check if text is valid JSON."""
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def extract_json_objects(content: str) -> List[Dict[str, Any]]:
    """Extract JSON objects and arrays from content."""
    examples = []
    
    # Pattern 1: Complete JSON objects/arrays (starts with { or [)
    json_pattern = r'(?:\{[\s\S]*?\}|\[[\s\S]*?\])'
    
    matches = re.finditer(json_pattern, content)
    
    for match in matches:
        json_text = match.group(0).strip()
        
        # Skip if too short
        if len(json_text) < 20:
            continue
        
        # Validate JSON
        try:
            json_obj = json.loads(json_text)
            
            # Only keep objects or arrays (not primitives)
            if not isinstance(json_obj, (dict, list)):
                continue
            
            # Skip empty
            if (isinstance(json_obj, dict) and len(json_obj) == 0) or \
               (isinstance(json_obj, list) and len(json_obj) == 0):
                continue
            
            # Skip if too large (keep reasonable size)
            json_str = json.dumps(json_obj, ensure_ascii=False)
            if len(json_str) > 10000:  # Skip very large JSON
                continue
            
            examples.append({
                "json": json_obj,
                "json_text": json_str,
                "type": "object" if isinstance(json_obj, dict) else "array",
                "valid": True
            })
        except json.JSONDecodeError:
            # Invalid JSON - keep for correction training
            if len(json_text) > 20 and len(json_text) < 5000:
                # Try to fix common issues
                fixed = try_fix_json(json_text)
                if fixed and is_valid_json(fixed):
                    examples.append({
                        "json": json.loads(fixed),
                        "json_text": fixed,
                        "invalid_json": json_text,
                        "type": "object" if fixed.strip().startswith('{') else "array",
                        "valid": True,
                        "was_invalid": True
                    })
                else:
                    # Keep invalid for correction examples
                    examples.append({
                        "invalid_json": json_text,
                        "type": "object" if json_text.strip().startswith('{') else "array",
                        "valid": False
                    })
    
    return examples


def try_fix_json(text: str) -> Optional[str]:
    """Try to fix common JSON issues."""
    # Remove trailing commas
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # Fix single quotes to double quotes (simple cases)
    # Only fix if it looks like JSON structure
    if text.strip().startswith(('{', '[')):
        # Very basic fix - only if safe
        text = re.sub(r"'([^']*)':", r'"\1":', text)
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)
    
    return text


def format_to_chatml_generation(json_obj: Any, json_type: str = "object") -> str:
    """Format valid JSON example for generation task."""
    json_text = json.dumps(json_obj, indent=2, ensure_ascii=False)
    
    # Compact if too large
    if len(json_text) > 500:
        json_text = json.dumps(json_obj, ensure_ascii=False)
    
    system_content = f"Task: json_generation\nFormat: generic"
    
    user_prompt = f"Generate a valid JSON {json_type}"
    
    return (
        f"<|system|>\n{system_content}\n<|end|>\n"
        f"<|user|>\n{user_prompt}\n<|end|>\n"
        f"<|assistant|>\n{json_text}\n<|end|>"
    )


def format_to_chatml_correction(invalid_json: str, valid_json: str) -> str:
    """Format invalid JSON example for correction task."""
    system_content = "Task: json_correction\nFormat: generic\nError type: syntax"
    
    user_prompt = f"Fix this invalid JSON:\n{invalid_json}"
    
    return (
        f"<|system|>\n{system_content}\n<|end|>\n"
        f"<|user|>\n{user_prompt}\n<|end|>\n"
        f"<|assistant|>\n{valid_json}\n<|end|>"
    )


def load_the_stack_json(
    limit: Optional[int] = None,
    token: Optional[str] = None,
    languages: List[str] = None,
    max_check: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Load JSON files from the-stack dataset."""
    try:
        from datasets import load_dataset
        
        print("="*80)
        print("Loading JSON subset from bigcode/the-stack")
        print("="*80)
        
        # Check for token
        if not token:
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        
        # Try to get token from HuggingFace cache
        if not token:
            try:
                from huggingface_hub import HfFolder
                token = HfFolder.get_token()
            except Exception:
                pass
        
        if not token:
            print("\n[WARNING] No HuggingFace token found. Set HF_TOKEN environment variable.")
            print("\n" + "="*80)
            print("ACTION REQUIRED: Accept dataset terms")
            print("="*80)
            print("\n1. Visit: https://huggingface.co/datasets/bigcode/the-stack")
            print("2. Click 'Agree and access repository'")
            print("3. Accept the terms and conditions")
            print("4. Get token from: https://huggingface.co/settings/tokens")
            print("5. Set environment variable: export HF_TOKEN=your_token_here")
            print("\n" + "="*80)
            return []
        
        if token:
            print(f"\n[INFO] Using token: {token[:10]}...")
            try:
                from huggingface_hub import whoami
                user = whoami(token=token)
                print(f"[INFO] Authenticated as: {user.get('name', 'unknown')}")
            except:
                pass
        
        if languages is None:
            languages = ["json", "javascript", "typescript", "python"]
        
        # Try to load JSON files directly
        print("\n[INFO] Attempting to load JSON files from the-stack...")
        
        try:
            dataset = load_dataset(
                "bigcode/the-stack",
                data_dir="data/json",
                split="train",
                streaming=True,
                token=token
            )
            print("[OK] Dataset loaded (streaming mode) - JSON directory")
        except Exception:
            # If JSON directory doesn't exist, try filtering by extension
            try:
                print("[INFO] JSON directory not found, trying to filter by extension...")
                dataset = load_dataset(
                    "bigcode/the-stack",
                    split="train",
                    streaming=True,
                    token=token
                )
                # Filter for JSON files
                def is_json_file(example):
                    ext = example.get("ext", "").lower()
                    path = example.get("path", "").lower()
                    return ext == "json" or "json" in path or ".json" in path
                
                dataset = dataset.filter(is_json_file)
                print("[OK] Dataset loaded and filtered for JSON files")
            except Exception as e:
                error_msg = str(e)
                if "gated dataset" in error_msg.lower() or "ask for access" in error_msg.lower():
                    print(f"\n[ERROR] Dataset access required!")
                    print("\n" + "="*80)
                    print("ACTION REQUIRED: Accept dataset terms")
                    print("="*80)
                    print("\n1. Visit: https://huggingface.co/datasets/bigcode/the-stack")
                    print("2. Click 'Agree and access repository'")
                    print("3. Accept the terms and conditions")
                    print("4. Run this script again")
                    print("\n" + "="*80)
                else:
                    print(f"[ERROR] Failed to load dataset: {e}")
                return []
        
        all_examples = []
        valid_count = 0
        invalid_count = 0
        seen_hashes = set()
        files_checked = 0
        files_with_json = 0
        
        # Calculate max files to check (20x limit to find JSON files)
        max_files_to_check = max_check if max_check else (limit * 20 if limit else None)
        
        print(f"\nProcessing JSON files...")
        print(f"  Limit: {limit or 'unlimited'} files WITH JSON code")
        print(f"  Max files to check: {max_files_to_check or 'unlimited'}")
        print(f"  Languages: {', '.join(languages)}")
        print("")
        
        for example in tqdm(dataset, desc="Checking files"):
            files_checked += 1
            
            # Stop if we've checked enough files
            if max_files_to_check and files_checked >= max_files_to_check:
                print(f"\n[INFO] Reached max files to check ({max_files_to_check:,}). Stopping.")
                break
            
            # Stop if we've found enough files with JSON
            if limit and files_with_json >= limit:
                print(f"\n[INFO] Found {files_with_json} files with JSON code. Stopping.")
                break
            
            content = example.get("content", "").strip()
            
            if not content or len(content) < 20:
                invalid_count += 1
                continue
            
            # Extract JSON objects/arrays
            json_examples = extract_json_objects(content)
            
            if not json_examples:
                invalid_count += 1
                continue
            
            # File has JSON, count it
            files_with_json += 1
            
            for json_example in json_examples:
                try:
                    # Skip duplicates
                    json_text = json_example.get("json_text", json_example.get("invalid_json", ""))
                    if not json_text:
                        continue
                    
                    content_hash = hash(json_text[:500])  # Hash first 500 chars
                    if content_hash in seen_hashes:
                        continue
                    seen_hashes.add(content_hash)
                    
                    if json_example.get("valid", False):
                        # Valid JSON - generation task
                        json_obj = json_example["json"]
                        json_type = json_example.get("type", "object")
                        
                        chatml_text = format_to_chatml_generation(json_obj, json_type)
                        all_examples.append({"text": chatml_text})
                        valid_count += 1
                        
                        # If it was invalid before, also add correction example
                        if json_example.get("was_invalid", False):
                            invalid_json = json_example.get("invalid_json", "")
                            if invalid_json:
                                chatml_correction = format_to_chatml_correction(
                                    invalid_json, json_text
                                )
                                all_examples.append({"text": chatml_correction})
                                invalid_count += 1
                    else:
                        # Invalid JSON - skip for now (we'll generate corrections separately)
                        # Or try to find a valid version nearby
                        invalid_count += 1
                        continue
                        
                except Exception as e:
                    # Skip this JSON example if anything goes wrong
                    invalid_count += 1
                    continue
        
        print(f"\n{'='*80}")
        print(f"Collection Summary:")
        print(f"  Files checked: {files_checked:,}")
        print(f"  Files with JSON: {files_with_json}")
        print(f"  Files without JSON: {files_checked - files_with_json:,}")
        print(f"  Valid JSON examples: {valid_count:,}")
        print(f"  Invalid/duplicate: {invalid_count:,}")
        print(f"  Success rate: {(files_with_json/files_checked*100):.2f}%" if files_checked > 0 else "  Success rate: 0%")
        print(f"{'='*80}")
        
        return all_examples
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download JSON from the-stack (requires auth)")
    parser.add_argument(
        "--limit",
        type=int,
        default=50000,
        help="Limit number of files WITH JSON code to process (default: 50000). Script will check up to 20x this limit to find matches."
    )
    parser.add_argument(
        "--max-check",
        type=int,
        default=None,
        help="Maximum number of files to check (default: 20x limit). Use to prevent checking too many files."
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="HuggingFace token (or use HF_TOKEN env var)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    output_file = Path(args.output) if args.output else base_dir / "datasets" / "raw" / "the_stack_json" / "the_stack_json.jsonl"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load examples
    examples = load_the_stack_json(limit=args.limit, token=args.token, max_check=args.max_check)
    
    if not examples:
        print("[ERROR] No examples to save")
        return
    
    # Format and save
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in tqdm(examples, desc="Writing"):
            json_line = json.dumps(example, ensure_ascii=False)
            f.write(json_line + '\n')
    
    print(f"\n[OK] Saved {len(examples):,} examples to {output_file}")
    print(f"     File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()

