#!/usr/bin/env python3
"""
Expert-JSON Unified Preprocessing

Combines all data sources and formats into ChatML for training:
- APIs.guru (OpenAPI examples)
- SchemaStore (JSON Schema examples)
- CloudEvents (event examples)
- Negative examples (invalid JSON + corrections)

Output: datasets/train.jsonl
Target: 100k+ examples
"""

import json
import hashlib
import random
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

def canonicalize_json(obj: Any) -> str:
    """Canonicalize JSON for deduplication"""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)

def hash_json(obj: Any) -> str:
    """Hash JSON content for deduplication"""
    canonical = canonicalize_json(obj)
    return hashlib.sha256(canonical.encode()).hexdigest()

def format_chatml_generation(example: Dict[str, Any]) -> str:
    """Format positive example (generate valid JSON) with ChatML"""
    format_type = example.get("format", "generic")
    schema = example.get("schema")
    json_example = example.get("example", {})
    
    # Build system message
    system_content = f"Task: json_generation\nFormat: {format_type}"
    if schema:
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
        if len(schema_str) < 1000:  # Only include if schema is reasonable size
            system_content += f"\nSchema:\n{schema_str}"
    
    # Build user prompt based on format
    prompts = {
        "openapi_schema": f"Generate a valid JSON object for {example.get('schema_name', 'API')} schema",
        "openapi_request": f"Generate a valid request body for {example.get('method', 'POST')} {example.get('path', '/api')}",
        "openapi_response": f"Generate a valid {example.get('status_code', '200')} response for {example.get('path', '/api')}",
        "json_schema": f"Generate a valid JSON object matching the {example.get('schema_name', 'configuration')} schema",
        "cloudevents": f"Generate a valid CloudEvents {example.get('variant', 'standard')} event",
        "generic": "Generate a valid JSON object"
    }
    
    user_prompt = prompts.get(format_type, prompts["generic"])
    
    # Format output JSON (pretty print if small, compact if large)
    json_output = json.dumps(json_example, indent=2, ensure_ascii=False)
    if len(json_output) > 500:
        json_output = json.dumps(json_example, ensure_ascii=False)
    
    return (
        f"<|system|>\n{system_content}\n<|end|>\n"
        f"<|user|>\n{user_prompt}\n<|end|>\n"
        f"<|assistant|>\n{json_output}\n<|end|>"
    )

def format_chatml_correction(example: Dict[str, Any]) -> str:
    """Format negative example (fix invalid JSON) with ChatML"""
    format_type = example.get("format", "generic")
    corruption_type = example.get("corruption_type", "unknown")
    invalid_json = example.get("invalid_json", "")
    valid_json = example.get("valid_json", "{}")
    
    # Build system message
    system_content = f"Task: json_correction\nFormat: {format_type}\nError type: {corruption_type}"
    
    # User prompt
    user_prompt = f"Fix this invalid JSON:\n{invalid_json}"
    
    return (
        f"<|system|>\n{system_content}\n<|end|>\n"
        f"<|user|>\n{user_prompt}\n<|end|>\n"
        f"<|assistant|>\n{valid_json}\n<|end|>"
    )

def extract_format_from_chatml(text: str) -> str:
    """Extract format type from ChatML format"""
    if not text:
        return "generic"
    
    # Look for Format: in system message
    format_match = re.search(r'Format:\s*(\w+)', text)
    if format_match:
        return format_match.group(1).lower()
    
    return "generic"

def rebalance_dataset(examples: List[Dict[str, Any]], target_generic_ratio: float = 0.70, target_total: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Rebalance dataset by limiting generic format to target ratio and reducing total size.
    
    Args:
        examples: List of examples with 'text' field
        target_generic_ratio: Target max ratio for generic format (default: 0.70 = 70%)
        target_total: Target total examples (None = keep all non-generic, limit generic to ratio)
    
    Returns:
        Rebalanced list of examples
    """
    random.seed(42)  # For reproducibility
    
    # Categorize examples by format
    examples_by_format = defaultdict(list)
    
    for example in examples:
        text = example.get("text", "")
        if not text:
            continue
        
        format_type = extract_format_from_chatml(text)
        examples_by_format[format_type].append(example)
    
    generic_examples = examples_by_format.get("generic", [])
    other_examples = []
    
    for fmt, ex_list in examples_by_format.items():
        if fmt != "generic":
            other_examples.extend(ex_list)
    
    other_count = len(other_examples)
    
    print(f"\n[REBALANCING] Rebalancing dataset (target generic ratio: {target_generic_ratio*100:.1f}%)...")
    print(f"  Before: Generic={len(generic_examples):,}, Other={other_count:,}, Total={len(examples):,}")
    
    if target_total:
        # Strategy: Keep all other examples, limit generic to fit target_total and ratio
        # Priority: Keep all other examples, then add generic up to 70% ratio and target_total limit
        
        # Keep all other examples (they are valuable and diverse)
        selected_other = other_examples
        
        # Calculate max generic based on ratio: generic / (generic + other) <= target_generic_ratio
        # generic <= (generic + other_count) * target_generic_ratio
        # generic <= generic * target_generic_ratio + other_count * target_generic_ratio
        # generic - generic * target_generic_ratio <= other_count * target_generic_ratio
        # generic * (1 - target_generic_ratio) <= other_count * target_generic_ratio
        # generic <= other_count * target_generic_ratio / (1 - target_generic_ratio)
        max_generic_by_ratio = int(other_count * target_generic_ratio / (1 - target_generic_ratio))
        
        # Also respect target_total: generic + other <= target_total
        max_generic_by_total = target_total - other_count
        
        # Use the minimum of both constraints
        max_generic = min(max_generic_by_ratio, max_generic_by_total)
        
        # If other_count exceeds target_total, we need to reduce other examples
        if other_count > target_total:
            # Reduce other examples to fit target_total, maintaining ratio
            max_other = int(target_total * (1 - target_generic_ratio))
            selected_other = random.sample(other_examples, max_other)
            max_generic = target_total - len(selected_other)
        
        # Sample generic examples
        if len(generic_examples) > max_generic:
            selected_generic = random.sample(generic_examples, max_generic)
        else:
            selected_generic = generic_examples
        
        rebalanced = selected_generic + selected_other
    else:
        # No target_total: keep all other examples, limit generic to ratio
        if other_count > 0:
            # Calculate max generic based on other_count
            # generic / (generic + other) = target_generic_ratio
            # generic = other * target_generic_ratio / (1 - target_generic_ratio)
            max_generic = int(other_count * target_generic_ratio / (1 - target_generic_ratio))
        else:
            max_generic = len(generic_examples)
        
        # Sample generic examples
        if len(generic_examples) > max_generic:
            selected_generic = random.sample(generic_examples, max_generic)
        else:
            selected_generic = generic_examples
        
        rebalanced = selected_generic + other_examples
    
    # Shuffle to mix formats
    random.shuffle(rebalanced)
    
    # Count after rebalancing
    after_generic = sum(1 for ex in rebalanced if extract_format_from_chatml(ex.get("text", "")) == "generic")
    after_other = len(rebalanced) - after_generic
    
    if len(rebalanced) > 0:
        generic_pct = after_generic / len(rebalanced) * 100
        print(f"  After:  Generic={after_generic:,} ({generic_pct:.1f}%), Other={after_other:,}, Total={len(rebalanced):,}")
        print(f"  Reduction: {len(examples):,} -> {len(rebalanced):,} examples ({len(rebalanced)/len(examples)*100:.1f}% kept)")
    else:
        print(f"  After:  Total={len(rebalanced):,}")
    
    return rebalanced

def load_source_file(file_path: Path, limit: Optional[int] = None, random_sample: bool = False) -> List[Dict[str, Any]]:
    """Load examples from JSONL file
    
    Args:
        file_path: Path to JSONL file
        limit: Maximum number of examples to return (None = all)
        random_sample: If True and limit is set, randomly sample instead of taking first N
    """
    if not file_path.exists():
        return []
    
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                examples.append(json.loads(line))
            except:
                continue
    
    # Apply limit with optional random sampling
    if limit and len(examples) > limit:
        if random_sample:
            examples = random.sample(examples, limit)
        else:
            examples = examples[:limit]
    
    return examples

def main():
    # Paths
    raw_dir = Path("datasets/raw")
    output_dir = Path("datasets")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load all sources
    print("Loading source data...")
    
    sources = {
        "apis_guru": load_source_file(raw_dir / "apis_guru" / "apis_guru_examples.jsonl"),
        "schemastore": load_source_file(raw_dir / "schemastore" / "schemastore_examples.jsonl"),
        "cloudevents": load_source_file(raw_dir / "cloudevents" / "cloudevents_examples.jsonl"),
        "paraloq": load_source_file(raw_dir / "paraloq" / "paraloq_examples.jsonl"),
        "mastercontrol": load_source_file(raw_dir / "mastercontrol" / "mastercontrol_examples.jsonl"),
        "negatives": load_source_file(raw_dir / "negatives" / "negative_examples.jsonl"),
        # NEW SOURCES v0.2.0
        "microsoft_schemas": load_source_file(Path("datasets/microsoft_text_to_schema/train_chatml.jsonl")),
        "microsoft_schemas_val": load_source_file(Path("datasets/microsoft_text_to_schema/valid_chatml.jsonl")),
        "microsoft_schemas_test": load_source_file(Path("datasets/microsoft_text_to_schema/test_chatml.jsonl")),
        "synthetic_schemas": load_source_file(Path("datasets/text_to_schema/train_chatml.jsonl")),
        "synthetic_schemas_val": load_source_file(Path("datasets/text_to_schema/valid_chatml.jsonl")),
        "synthetic_schemas_test": load_source_file(Path("datasets/text_to_schema/test_chatml.jsonl")),
        "repair_enhanced": load_source_file(Path("datasets/json_repair_enhanced/train_chatml.jsonl")),
        "repair_enhanced_val": load_source_file(Path("datasets/json_repair_enhanced/valid_chatml.jsonl")),
        "repair_enhanced_test": load_source_file(Path("datasets/json_repair_enhanced/test_chatml.jsonl")),
        # NEW SOURCE v0.3.0 - The Stack (increased limit to get more generic examples for 70% ratio)
        "the_stack": load_source_file(raw_dir / "the_stack_json" / "the_stack_json.jsonl", limit=50000, random_sample=True),
    }
    
    print("\nSource statistics:")
    for source_name, examples in sources.items():
        print(f"  {source_name:20s}: {len(examples):,} examples")
    
    # Process all examples
    processed = []
    seen_hashes = set()
    stats = defaultdict(int)
    
    print("\nProcessing and deduplicating...")
    
    # Process positive examples (generation task)
    for source_name in ["apis_guru", "schemastore", "cloudevents", "paraloq", "mastercontrol"]:
        examples = sources[source_name]
        
        for idx, example in enumerate(examples):
            try:
                # Hash for deduplication
                json_example = example.get("example", {})
                
                # QUALITY FILTER: Skip tiny/simple examples
                ex_str = json.dumps(json_example, ensure_ascii=False)
                if len(ex_str) < 50:  # Skip very small
                    stats["filtered_small"] += 1
                    continue
                
                # Skip simple strings/numbers (not objects/arrays)
                if not isinstance(json_example, (dict, list)):
                    stats["filtered_simple_type"] += 1
                    continue
                
                content_hash = hash_json(json_example)
                
                if content_hash in seen_hashes:
                    stats["duplicates"] += 1
                    continue
                seen_hashes.add(content_hash)
                
                # Format with ChatML
                text = format_chatml_generation(example)
                processed.append({"text": text})
                stats[f"{source_name}_processed"] += 1
                
                if len(processed) % 5000 == 0:
                    print(f"  Processed {len(processed):,} examples...")
            
            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] < 10:
                    print(f"  Error in {source_name}[{idx}]: {e}")
    
    # Add new sources (already in ChatML format, just append)
    print("\nAdding enhanced sources (already in ChatML)...")
    new_sources = [
        "microsoft_schemas", "microsoft_schemas_val", "microsoft_schemas_test",
        "synthetic_schemas", "synthetic_schemas_val", "synthetic_schemas_test",
        "repair_enhanced", "repair_enhanced_val", "repair_enhanced_test",
        "the_stack"  # The Stack JSON examples
    ]
    for source_name in new_sources:
        for example in sources.get(source_name, []):
            processed.append(example)  # Already has "text" field
            stats[f"{source_name}_processed"] += 1
    
    print(f"  Added {sum(stats.get(f'{s}_processed', 0) for s in new_sources):,} enhanced examples")
    
    # Calculate target for balanced dataset
    # We want roughly equal distribution: 33% generation, 33% extraction, 33% correction
    generation_count = stats["apis_guru_processed"] + stats["schemastore_processed"] + stats["cloudevents_processed"]
    extraction_count = stats["paraloq_processed"] + stats["mastercontrol_processed"]
    
    # Target: use the average of generation+extraction for correction
    # This ensures we don't overwhelm with corrections
    target_correction = int((generation_count + extraction_count) / 2 * 1.2)  # 20% bonus for corrections
    max_corrections = max(target_correction, 20000)  # Ensure strong correction coverage
    
    print(f"\nBalancing correction examples:")
    print(f"  Generation tasks: {generation_count:,}")
    print(f"  Extraction tasks: {extraction_count:,}")
    print(f"  Target corrections: {max_corrections:,} (limited from {len(sources['negatives']):,})")
    
    # Process negative examples (correction task) with limit
    correction_collected = 0
    for idx, example in enumerate(sources["negatives"]):
        if correction_collected >= max_corrections:
            stats["corrections_skipped"] = len(sources["negatives"]) - idx
            break
            
        try:
            # Hash based on valid JSON (avoid duplicate corrections)
            valid_json_str = example.get("valid_json", "{}")
            invalid_json_str = example.get("invalid_json", "")
            hash_input = valid_json_str + "\n<ERR>\n" + invalid_json_str
            content_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            if content_hash in seen_hashes:
                stats["duplicates"] += 1
                continue
            seen_hashes.add(content_hash)
            
            # Format with ChatML
            text = format_chatml_correction(example)
            processed.append({"text": text})
            stats["negatives_processed"] += 1
            correction_collected += 1
            
            if len(processed) % 5000 == 0:
                print(f"  Processed {len(processed):,} examples...")
        
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] < 10:
                print(f"  Error in negatives[{idx}]: {e}")
    
    # Shuffle to mix positive and negative examples
    random_seed = 42
    random.seed(random_seed)
    random.shuffle(processed)
    
    # Rebalance dataset: limit to 40k and focus on addressing known issues from v0.4.0
    print(f"\n[REBALANCING] Starting rebalancing...")
    print(f"  Current total: {len(processed):,} examples")
    print(f"  Target: 40,000 examples (focusing on schema generation, transformations, array handling)")
    
    # Target: 40k examples total, generic <= 70%
    target_total = 40000
    
    # Prioritize examples that address known issues:
    # 1. Schema vs Example confusion - prioritize schema generation examples
    # 2. JSON transformation - prioritize transformation examples
    # 3. Array handling - prioritize array examples
    # 4. Type conversion - prioritize type-aware examples
    
    # Separate examples by format to prioritize non-generic
    examples_by_format = defaultdict(list)
    for example in processed:
        text = example.get("text", "")
        if not text:
            continue
        format_type = extract_format_from_chatml(text)
        examples_by_format[format_type].append(example)
    
    # Prioritize formats that help with known issues
    priority_formats = [
        "json_schema",      # Schema generation (addresses schema vs example confusion)
        "openapi_schema",   # Schema generation
        "data_extraction",  # Transformations (addresses flat to nested transformation)
        "cloudevents",      # Structured formats
        "openapi_property", # Structured formats
        "openapi_response", # Array handling
        "openapi_request",  # Type conversion
    ]
    
    # Collect priority examples first
    priority_examples = []
    for fmt in priority_formats:
        if fmt in examples_by_format:
            priority_examples.extend(examples_by_format[fmt])
            print(f"  Priority format '{fmt}': {len(examples_by_format[fmt]):,} examples")
    
    # Get other non-generic examples
    other_examples = []
    generic_examples = examples_by_format.get("generic", [])
    
    for fmt, ex_list in examples_by_format.items():
        if fmt != "generic" and fmt not in priority_formats:
            other_examples.extend(ex_list)
    
    print(f"\n  Priority examples: {len(priority_examples):,}")
    print(f"  Other non-generic: {len(other_examples):,}")
    print(f"  Generic: {len(generic_examples):,}")
    
    # Strategy: Generic should be 70%, so reduce others to fit 40k total
    # Target: generic = 70% of 40k = 28,000, others = 30% of 40k = 12,000
    
    target_generic_count = int(target_total * 0.70)  # 28,000
    target_other_count = target_total - target_generic_count  # 12,000
    
    # Sample generic examples (up to target)
    if len(generic_examples) > target_generic_count:
        random.seed(42)
        selected_generic = random.sample(generic_examples, target_generic_count)
    else:
        selected_generic = generic_examples
        # If we don't have enough generic, adjust target_other_count
        target_other_count = target_total - len(selected_generic)
    
    # Reduce priority + other examples to fit target_other_count
    all_non_generic = priority_examples + other_examples
    total_non_generic = len(all_non_generic)
    
    if total_non_generic > target_other_count:
        # Sample non-generic examples, prioritizing priority formats
        # First, try to keep all priority if possible
        if len(priority_examples) <= target_other_count:
            selected_priority = priority_examples
            remaining_slots = target_other_count - len(selected_priority)
            if remaining_slots > 0 and len(other_examples) > 0:
                random.seed(42)
                selected_other = random.sample(other_examples, min(remaining_slots, len(other_examples)))
            else:
                selected_other = []
        else:
            # Need to reduce priority examples too
            random.seed(42)
            selected_priority = random.sample(priority_examples, target_other_count)
            selected_other = []
    else:
        # Keep all non-generic examples
        selected_priority = priority_examples
        selected_other = other_examples
    
    # Combine and shuffle
    processed = selected_priority + selected_other + selected_generic
    random.seed(42)
    random.shuffle(processed)
    
    # Final count
    final_generic = sum(1 for ex in processed if extract_format_from_chatml(ex.get("text", "")) == "generic")
    final_other = len(processed) - final_generic
    
    print(f"\n[REBALANCING] Rebalancing complete:")
    print(f"  Priority formats: {len(selected_priority):,}")
    print(f"  Other formats: {len(selected_other):,}")
    print(f"  Generic: {final_generic:,} ({final_generic/len(processed)*100:.1f}%)")
    print(f"  Total: {len(processed):,} examples")
    print(f"  Reduction: {len(examples_by_format) and sum(len(v) for v in examples_by_format.values()) or len(processed):,} -> {len(processed):,} examples")
    
    # Save processed dataset
    output_file = output_dir / "train.jsonl"
    print(f"\n\nSaving {len(processed):,} examples to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in processed:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats_file = output_dir / "preprocessing_stats.json"
    
    # Calculate Microsoft + synthetic totals
    ms_total = (stats.get("microsoft_schemas_processed", 0) + 
                stats.get("microsoft_schemas_val_processed", 0) + 
                stats.get("microsoft_schemas_test_processed", 0))
    synth_total = (stats.get("synthetic_schemas_processed", 0) + 
                   stats.get("synthetic_schemas_val_processed", 0) + 
                   stats.get("synthetic_schemas_test_processed", 0))
    repair_total = (stats.get("repair_enhanced_processed", 0) + 
                    stats.get("repair_enhanced_val_processed", 0) + 
                    stats.get("repair_enhanced_test_processed", 0))
    
    stats_data = {
        "total_input": sum(len(ex) for ex in sources.values()),
        "processed": len(processed),
        "duplicates": stats["duplicates"],
        "errors": stats["errors"],
        "by_source": {
            "apis_guru": stats["apis_guru_processed"],
            "schemastore": stats["schemastore_processed"],
            "cloudevents": stats["cloudevents_processed"],
            "paraloq": stats["paraloq_processed"],
            "mastercontrol": stats["mastercontrol_processed"],
            "negatives": stats["negatives_processed"],
            "microsoft_schemas": ms_total,
            "synthetic_schemas": synth_total,
            "repair_enhanced": repair_total
        },
        "format_distribution": {
            "generation_tasks": stats["apis_guru_processed"] + stats["schemastore_processed"] + stats["cloudevents_processed"],
            "extraction_tasks": stats["paraloq_processed"] + stats["mastercontrol_processed"],
            "correction_tasks": stats["negatives_processed"]
        }
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("PREPROCESSING SUMMARY")
    print("="*60)
    print(f"Total input:            {stats_data['total_input']:,}")
    print(f"Processed:              {len(processed):,}")
    print(f"Duplicates removed:     {stats['duplicates']:,}")
    if 'corrections_skipped' in stats:
        print(f"Corrections skipped:    {stats['corrections_skipped']:,} (for balance)")
    print(f"Errors:                 {stats['errors']}")
    print(f"\nBy source:")
    for source, count in stats_data["by_source"].items():
        print(f"  {source:15s}: {count:,}")
    print(f"\nTask distribution (balanced):")
    gen_pct = stats_data['format_distribution']['generation_tasks'] / len(processed) * 100
    ext_pct = stats_data['format_distribution']['extraction_tasks'] / len(processed) * 100
    cor_pct = stats_data['format_distribution']['correction_tasks'] / len(processed) * 100
    print(f"  Generation tasks:   {stats_data['format_distribution']['generation_tasks']:,} ({gen_pct:.1f}%)")
    print(f"  Extraction tasks:   {stats_data['format_distribution']['extraction_tasks']:,} ({ext_pct:.1f}%)")
    print(f"  Correction tasks:   {stats_data['format_distribution']['correction_tasks']:,} ({cor_pct:.1f}%)")
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")

if __name__ == "__main__":
    main()

