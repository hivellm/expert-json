#!/usr/bin/env python3
"""
APIs.guru OpenAPI Collector

Fetches OpenAPI specifications from APIs.guru and extracts:
- Schema definitions (components.schemas)
- Example request/response payloads
- Parameter examples

Target: 20-30k unique JSON examples
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Any
import time
from collections import defaultdict

OUTPUT_DIR = Path("../datasets/raw/apis_guru")
API_LIST_URL = "https://api.apis.guru/v2/list.json"

def fetch_api_list() -> Dict[str, Any]:
    """Fetch list of all APIs from APIs.guru"""
    print("Fetching API list from APIs.guru...")
    response = requests.get(API_LIST_URL, timeout=30)
    response.raise_for_status()
    return response.json()

def download_openapi_spec(url: str) -> Dict[str, Any]:
    """Download OpenAPI specification"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def extract_schemas(spec: Dict[str, Any], api_name: str) -> List[Dict[str, Any]]:
    """Extract schema definitions from OpenAPI spec
    
    FILTER: Only keep complete object examples (not individual properties)
    """
    examples = []
    
    # OpenAPI 3.x
    if "components" in spec and "schemas" in spec["components"]:
        for schema_name, schema_def in spec["components"]["schemas"].items():
            if "example" in schema_def:
                # Only keep if example is object/array (not simple types)
                example_val = schema_def["example"]
                if isinstance(example_val, (dict, list)):
                    example_str = json.dumps(example_val, ensure_ascii=False)
                    if len(example_str) > 50:  # Filter tiny objects
                        examples.append({
                            "source": f"apis.guru/{api_name}",
                            "format": "openapi_schema",
                            "schema_name": schema_name,
                            "schema": schema_def,
                            "example": example_val,
                            "task": "generate"
                        })
            
            # REMOVED: Individual property extraction (too simple)
    
    # OpenAPI 2.0 (Swagger)
    if "definitions" in spec:
        for schema_name, schema_def in spec["definitions"].items():
            if "example" in schema_def:
                example_val = schema_def["example"]
                if isinstance(example_val, (dict, list)):
                    example_str = json.dumps(example_val, ensure_ascii=False)
                    if len(example_str) > 50:
                        examples.append({
                            "source": f"apis.guru/{api_name}",
                            "format": "swagger_definition",
                            "schema_name": schema_name,
                            "schema": schema_def,
                            "example": example_val,
                            "task": "generate"
                        })
    
    return examples

def extract_request_examples(spec: Dict[str, Any], api_name: str) -> List[Dict[str, Any]]:
    """Extract request/response examples from paths
    
    FILTER: Only keep object/array examples (not simple values)
    """
    examples = []
    
    if "paths" not in spec:
        return examples
    
    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                continue
            
            # Request body examples (OpenAPI 3.x)
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})
                for media_type, media_def in content.items():
                    if "application/json" in media_type and "example" in media_def:
                        example_val = media_def["example"]
                        # Only keep complex examples
                        if isinstance(example_val, (dict, list)):
                            example_str = json.dumps(example_val, ensure_ascii=False)
                            if len(example_str) > 50:
                                examples.append({
                                    "source": f"apis.guru/{api_name}",
                                    "format": "openapi_request",
                                    "path": path,
                                    "method": method,
                                    "api_name": api_name,
                                    "example": example_val,
                                    "task": "generate"
                                })
            
            # Response examples
            if "responses" in operation:
                for status_code, response_def in operation["responses"].items():
                    content = response_def.get("content", {})
                    for media_type, media_def in content.items():
                        if "application/json" in media_type and "example" in media_def:
                            example_val = media_def["example"]
                            # Only keep complex examples
                            if isinstance(example_val, (dict, list)):
                                example_str = json.dumps(example_val, ensure_ascii=False)
                                if len(example_str) > 50:
                                    examples.append({
                                        "source": f"apis.guru/{api_name}",
                                        "format": "openapi_response",
                                        "path": path,
                                        "method": method,
                                        "status_code": status_code,
                                        "api_name": api_name,
                                        "example": example_val,
                                        "task": "generate"
                                    })
    
    return examples

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Fetch API list
    api_list = fetch_api_list()
    print(f"Found {len(api_list)} APIs")
    
    # Check for existing output and resume if found
    output_file = OUTPUT_DIR / "apis_guru_examples.jsonl"
    processed_apis = set()
    example_count = 0
    
    if output_file.exists():
        print(f"\nFound existing file, resuming...")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    ex = json.loads(line)
                    source = ex.get('source', '')
                    api_id = source.split('/')[1] if '/' in source else ''
                    if api_id:
                        processed_apis.add(api_id)
                    example_count += 1
                except:
                    continue
        print(f"Resuming from {example_count} examples ({len(processed_apis)} APIs already processed)")
    
    stats = defaultdict(int)
    stats['examples_extracted'] = example_count
    
    # Open output file in append mode
    output_f = open(output_file, 'a', encoding='utf-8')
    
    # Process each API
    for idx, (api_id, api_info) in enumerate(api_list.items()):
        try:
            # Skip if already processed
            if api_id in processed_apis:
                continue
            
            # Get preferred version
            preferred = api_info.get("preferred")
            if not preferred:
                stats["no_preferred"] += 1
                continue
            
            version_info = api_info["versions"].get(preferred)
            if not version_info:
                stats["no_version_info"] += 1
                continue
            
            spec_url = version_info.get("swaggerUrl")
            if not spec_url:
                stats["no_spec_url"] += 1
                continue
            
            print(f"\n[{idx+1}/{len(api_list)}] Processing: {api_id} (v{preferred})")
            
            # Download spec
            spec = download_openapi_spec(spec_url)
            stats["specs_downloaded"] += 1
            
            # Extract schemas
            schema_examples = extract_schemas(spec, api_id)
            request_examples = extract_request_examples(spec, api_id)
            
            api_examples = schema_examples + request_examples
            
            # Write immediately to file (incremental save)
            for example in api_examples:
                output_f.write(json.dumps(example, ensure_ascii=False) + '\n')
            output_f.flush()  # Ensure data is written
            
            stats["examples_extracted"] += len(api_examples)
            print(f"  Extracted: {len(api_examples)} examples (Total: {stats['examples_extracted']})")
            
            # Save stats every 50 APIs
            if (idx + 1) % 50 == 0:
                stats_file = OUTPUT_DIR / "collection_stats.json"
                stats_data = {
                    "processed_apis": idx + 1,
                    "total_apis": len(api_list),
                    "specs_downloaded": stats["specs_downloaded"],
                    "examples_extracted": stats["examples_extracted"],
                    "errors": stats["errors"],
                    "progress": f"{(idx + 1) / len(api_list) * 100:.1f}%"
                }
                with open(stats_file, 'w', encoding='utf-8') as sf:
                    json.dump(stats_data, sf, indent=2)
            
            # Rate limiting
            if idx % 10 == 0:
                time.sleep(1)
        
        except Exception as e:
            stats["errors"] += 1
            print(f"  Error: {e}")
            continue
    
    output_f.close()
    
    # Final statistics save
    print(f"\n\nCollection complete: {stats['examples_extracted']} examples")
    
    # Save final statistics
    stats_file = OUTPUT_DIR / "collection_stats.json"
    stats_data = {
        "total_apis": len(api_list),
        "processed_apis": len(api_list),
        "specs_downloaded": stats["specs_downloaded"],
        "examples_extracted": stats["examples_extracted"],
        "errors": stats["errors"],
        "progress": "100%",
        "skipped": {
            "no_preferred": stats["no_preferred"],
            "no_version_info": stats["no_version_info"],
            "no_spec_url": stats["no_spec_url"]
        }
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("APIS.GURU COLLECTION SUMMARY")
    print("="*60)
    print(f"Total APIs listed:      {len(api_list)}")
    print(f"Specs downloaded:       {stats['specs_downloaded']}")
    print(f"Examples extracted:     {stats['examples_extracted']}")
    print(f"Errors:                 {stats['errors']}")
    print(f"\nOutput: {output_file}")
    print(f"Stats:  {stats_file}")

if __name__ == "__main__":
    main()

