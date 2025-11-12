# Expert JSON

[![Version](https://img.shields.io/badge/version-0.4.1-blue.svg)](https://github.com/hivellm/expert-json/releases/tag/v0.4.1)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-investigative-yellow.svg)](README.md#at-a-glance)
[![Checkpoint](https://img.shields.io/badge/checkpoint-250-blue.svg)](README.md#checkpoint-analysis--selection-v030)

[![Base Model](https://img.shields.io/badge/base%20model-Qwen3--0.6B-orange.svg)](README.md#at-a-glance)
[![Adapter](https://img.shields.io/badge/adapter-DoRA%20r%3D14-blue.svg)](README.md#training--configuration)
[![Dataset](https://img.shields.io/badge/dataset-40k%20examples-brightgreen.svg)](README.md#dataset)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20CUDA-0078d4.svg)](README.md#training--configuration)

JSON generation and correction expert. Trained on 40,000 curated examples rebalance towards schema-heavy and data-extraction formats while keeping a deep correction set (≈54% generation, ≈46% correction). Dataset includes examples from APIs.guru, SchemaStore, CloudEvents, Paraloq, MasterControl, Microsoft schemas, and enhanced repair patterns.

**Version:** 0.4.1 (Rebalanced Dataset) | **Checkpoint:** checkpoint-250 (investigative build) | **Dataset:** 40,000 examples (70 % generic, 30 % issue-focused)

**Release intent:** showcase structural/arithmetical gains from the rebalanced corpus while we plan another training pass to address schema/array gaps. Keep using 0.4.0 for production workloads that require robust schema generation.

---

## At-a-glance

**What improved in 0.4.1 (vs 0.3.x):**
- ✅ Flat → nested rewrites now succeed on the evaluated prompts (`user_id` → `user.id`).
- ✅ Numeric aggregation returns plain numbers (`{"total": 200.5, "average": 66.8333}`) instead of symbolic expressions.
- ✅ Dataset is 40k curated examples with 30 % dedicated to historically weak patterns (schema, transformations, arrays, type conversion).

**What still needs work:**
- ❌ JSON Schema draft-07 responses remain illustrative or wrapped in `{"schema": {...}}` instead of full schemas with `$schema`/`type`.
- ⚠️ Array-only outputs occasionally return objects or narrations (todos, hex strings).
- ⚠️ Model still speaks aloud (“think” narration) in some prompts; post-processing or further fine-tuning required.
- ⚠️ Deep/complex transformations were not retested and should be considered unsupported.

**Smoke tests (PowerShell `scripts/run_cli_tests.ps1`):**

| Test prompt | 0.4.1 response |
|-------------|----------------|
| Schema draft-07 | ❌ `{"schema": {...}}` (missing `$schema`, extra wrapper) |
| Flat → nested | ✅ `{"user": {"id": "123", "profile": {"name": "Alice", "age": 34}}}` |
| Todos array | ⚠️ returns `{ "todo1": {...}, ... }` (object, not array) |
| Hex strings (3 × 6) | ⚠️ narrates reasoning, no pure JSON array |
| Total/average | ⚠️ narrates reasoning, no `{ "total": ..., "average": ... }` |

## Checkpoint Analysis & Selection (v0.3.0)

### Checkpoint Comparison (v0.3.x dataset)

| Checkpoint | Score (15 legacy tests) | Strengths | Critical issues |
|------------|------------------------|-----------|-----------------|
| Base       | 3/15 (20%)             | Basic JSON repair | Repetition, truncation |
| **250** (packaged in v0.4.1) | **5/15 (33%)** | Flat→nested transforms, numeric consistency | Schema vs example confusion, inconsistent arrays |
| 500 (previous release) | 6/15 (40%) | Syntax fixes, stable outputs | Still confuses complex schemas |
| 638       | 6/15 (40%)             | Similar to 500 | Trailing comma issues |
| Final     | 5/15 (33%)             | General corrections | Loop/regression risk |

**Why ship checkpoint-250?** To provide a focused build demonstrating structural transforms and arithmetic stability while the rebalanced dataset is under exploration—useful where those guarantees matter, with the caveat that schema generation remains problematic.

**Detailed Analysis:** See `logs/checkpoint_analysis.md`

### Known Limitations (v0.3.0)

**Current Issues:**
- ⚠️ Returns examples instead of schemas in some cases (tests 3, 7, 10, 12, 15)
- ⚠️ Cannot transform flat JSON to nested structure (test 8)
- ⚠️ Returns object instead of array in one case (test 5)
- ⚠️ Returns 5 items when 3 requested (test 14)
- ⚠️ Inserts math expressions in JSON values (test 12)

**Best Use Cases:**
- ✅ JSON Schema generation (nested structures, validation rules)
- ✅ JSON repair (trailing commas, quotes, unquoted keys)
- ✅ OpenAPI schema generation
- ✅ Complex nested object creation

## Qualitative Analysis (v0.1.0 → v0.2.0)

### Initial Results (v0.1.0 - Before Enhancement)

**Test Results:**

| Test | Base Model | Final v0.1.0 | Score | Status |
|------|------------|--------------|-------|---------|
| Simple JSON Creation | Loop infinito ♾️ | `{"name":"Alice", "age":25}` | 10/10 | ✅ Perfect |
| JSON Repair (missing comma) | Verbose, artifacts | Output clean but no fix | 7/10 | ⚠️ Conservative |
| Schema Generation | Wrong example | Wrong example | 3/10 | ❌ Critical issue |
| **Overall** | **1.5/10** | **7.25/10** | **+383%** | Good but incomplete |

### Problems Identified

**1. Schema Generation (CRITICAL)** ❌
- Prompt: "Create JSON schema for: product with id, name, price"
- Expected: `{"type": "object", "properties": {...}}`
- Got: `{"id": "123", "name": "Laptop", "price": 999.99}` (example, not schema!)
- **Root cause**: Dataset had "schema → example" but not "text → schema"

**2. JSON Repair - Missing Commas (MEDIUM)** ⚠️
- Prompt: `Fix JSON: {"name":"John" "age":30}`
- Expected: `{"name":"John", "age":30}` (add comma)
- Got: `{"name":"John", "age":30}` (no change)
- **Root cause**: No explicit missing comma error patterns in dataset

### Enhancement Solution (v0.2.0)

**Added 303 targeted examples:**

1. **Microsoft Production Schemas (183 REAL)** ✨
   - Source: https://github.com/microsoft/json-schemas
   - Products: Microsoft Fabric, Office-JS, Teams, Copilot, Rush, API-Extractor
   - Real production-quality JSON Schemas (not synthetic!)
   
2. **Synthetic Schema Templates (48)**
   - Simple objects, nested structures, arrays
   - API responses, pagination, e-commerce
   
3. **Enhanced JSON Repair (72)**
   - Missing commas (properties + arrays): 32 examples
   - Trailing commas, unquoted keys, single quotes: 40 examples

**Expected Improvements (v0.2.0):**
- Schema generation: 3/10 → 8+/10 (with 183 real examples)
- JSON repair: 7/10 → 9+/10 (explicit comma fix patterns)
- **Overall target: 9.0+/10**

**Actual Results (v0.3.0 - Checkpoint-500):**
- Schema generation: ✅ Nested schemas correct, validation rules correct
- JSON repair: ✅ Most cases fixed correctly
- **Overall: 40% (6/15 tests)** - Selected as best performing checkpoint

### Improvement Snapshot: 0.3 → 0.4

| Aspect | v0.3.0 (Checkpoint-500) | v0.4.1 (Checkpoint-250 investigative) | Change |
| --- | --- | --- | --- |
| Dataset | 38,240 examples (broad mix) | 40,000 rebalanced (70% generic + 30% issue-focused) | Rebalanced dataset targeting known gaps |
| JSON Schema generation | ✅ Works on straightforward cases, fails complex prompts | ❌ Still returns examples/incomplete schemas | Pending next training cycle |
| Flat → nested transforms | ⚠️ Frequently failed (legacy test #8) | ✅ Stable on simple structures | Improved via dataset focus |
| Numeric aggregation | ⚠️ Sometimes returned expressions (legacy test #12) | ✅ Pure numeric totals/averages | Improved via prompt/sample curation |
| Array formatting | ⚠️ Returned objects instead of arrays in legacy test | ⚠️ Still inconsistent (needs post-processing) | No change |
| Packaging | Production-ready release | Investigative package for targeted behavior | Different release goal |

> **Key takeaway:** the 0.4 rebalanced dataset plus stricter evaluation scripts delivered reliable structural transforms and numeric outputs, but the core schema-generation weakness remains on the roadmap for a follow-up training run.

**Practical Testing Results (CLI):**
- ✅ Simple schema generation: Perfect (e.g., `{"type": "object", "properties": {...}}`)
- ✅ JSON repair (missing comma): Perfect (e.g., `{"name": "John" "age": 30}` → `{"name": "John", "age": 30}`)
- ✅ JSON repair (trailing comma): Perfect (e.g., `{"id": 123,}` → `{"id": 123}`)
- ⚠️ Nested object requests: Returns example JSON instead of schema
- ⚠️ Type conversion: May convert numbers to strings in some cases

## Quick Start

### Using the Package

```bash
# 1. Install the expert (if you have the .expert package)
expert-cli install expert-json-qwen3-06b.v0.4.0.expert

# 2. Use in chat
expert-cli chat --experts json --prompt "Create JSON schema for a user with name and email"

# 3. Or fix broken JSON
expert-cli chat --experts json --prompt 'Fix JSON: {"name": "John" "age": 30}'
```

### Training from Scratch

```bash
# 1. Preprocess enhanced dataset
cd F:/Node/hivellm/expert/experts/expert-json
python preprocess.py  # Includes 183 Microsoft schemas automatically

# 2. Train the expert
../../cli/target/release/expert-cli train --manifest manifest.json

# 3. Test checkpoints
python scripts/test_complex.py

# 4. Package the best checkpoint
../../cli/target/release/expert-cli package --manifest manifest.json --weights weights
```

**Works best for:** JSON Schema generation, API development, syntax repair, configuration generation, event formatting  
**Enhanced capabilities:** Real Microsoft production schemas, advanced syntax correction  
**Package:** `expert-json-qwen3-06b.v0.4.0.expert` (TBD) - Checkpoint-500 included

## Features

- ✅ **Multi-format JSON** generation (OpenAPI, JSON Schema, CloudEvents, generic)
- ✅ **Autocorrection** - Fix invalid JSON (missing fields, type errors, syntax issues)
- ✅ **Schema-aware** generation with ChatML format
- ✅ **DoRA adapter (r=14)** for complex JSON structures
- ✅ **Grammar validation** (GBNF) for syntax enforcement
- ✅ **Unsloth integration** - 2x faster training, 70% less VRAM
- ✅ **Windows optimized** with memory safety and CUDA support
- ✅ **100k+ examples target** from curated sources

## What It Can Do ✅

**Expected Support (based on dataset sources):**
- ✅ OpenAPI request/response generation
- ✅ JSON Schema compliant object generation
- ✅ CloudEvents standard event formatting
- ✅ Configuration file generation (ESLint, package.json, tsconfig, etc.)
- ✅ **Data extraction from unstructured text** (NEW - Paraloq dataset)
  - Medical documents → Patient records
  - Business reports → Invoices, contracts
  - Technical docs → API responses, error logs
  - E-commerce → Product listings, orders
- ✅ Nested object and array structures
- ✅ Autocorrection of common JSON errors:
  - Missing required fields
  - Type mismatches
  - Extra/unknown fields
  - Syntax errors (trailing commas, unquoted keys)

## Known Limitations ⚠️

- **Schema fidelity** – still returns illustrative examples or wrapped responses; treat draft-07 outputs with caution.
- **Array-only responses** – may emit objects or narrated text (todos, hex strings); post-process before consumption.
- **“Think-aloud” narratives** – some prompts produce explanatory text instead of pure JSON.
- **Unretested deep transforms** – dataset improvements were focused on shallow flat→nested rewrites; broader transformations remain unsupported.

**Recommended usage:** keep 0.4.1 for exploratory work on structural transformations or numeric consistency, and continue to rely on 0.4.0 where schema generation and strict output formatting are required.

## Dataset (v0.5.0 Rebalanced)

**Total: 40,000 examples** (rebalanced from 737,228 to focus on quality and known issues)

### Primary Sources (Base: 37,937)

**1. APIs.guru** (4,240 processed):
- Source: https://api.apis.guru/v2/list.json
- Content: OpenAPI 2.0/3.x specifications from real APIs
- Extraction: Schema definitions, request/response examples
- Focus: REST API payloads
- Quality filter: Only objects/arrays >50 chars

**2. SchemaStore** (3,213 processed):
- Source: https://www.schemastore.org/api/json/catalog.json
- Content: JSON Schemas for common tools (ESLint, Prettier, tsconfig, package.json, etc.)
- Generation: Valid examples from schemas (50% complete, 50% minimal)
- Focus: Configuration files
- Quality filter: Exclude objects <30 chars

**3. CloudEvents** (5,000 examples):
- Source: CNCF CloudEvents specification
- Content: Event format variants with 18 diverse payload types
- Generation: Synthetic events (user, e-commerce, file, infrastructure, code, data events)
- Focus: Event-driven architectures

**4. Paraloq Data Extraction** (484 examples):
- Source: https://huggingface.co/datasets/paraloq/json_data_extraction
- Content: High-quality text → JSON extraction (Gemini-Pro generated)
- Domains: Medical, Manufacturing, Travel, Business, E-commerce, Media, Technology, Simple
- Focus: Data extraction from unstructured text
- Quality: Curated, validated, diverse scenarios

**5. MasterControl Structured Extraction** (10,000 examples):
- Source: https://huggingface.co/datasets/MasterControlAIML/JSON-Unstructured-Structured
- Content: Complex document → JSON extraction (100% valid JSON, 97% valid schemas)
- Domains: Financial statements, Quality assurance, Risk assessment, Manufacturing, Compliance
- Focus: Complex data extraction (avg 3,066 chars per JSON)
- Quality: Excellent - All examples >1k chars, highly structured

**6. Negative Examples** (15,000 balanced):
- Source: Generated from positive examples
- Content: Invalid JSON + corrections
- Corruption types:
  - Missing required fields
  - Type mismatches (string ↔ number)
  - Extra/unknown fields
  - Syntax errors (trailing commas, unquoted keys)
- Focus: Autocorrection training

### Enhancement Sources (v0.2.0: +303 examples)

**7. The Stack Dataset** (optional, gated JSON examples from codebase via HuggingFace) ✨
- Source: https://huggingface.co/datasets/bigcode/the-stack (BigCode OpenRAIL-M License)
- Content: JSON objects/arrays extracted from permissively licensed source code
- Collection: Valid JSON for generation, invalid JSON for correction training
- Focus: Real-world JSON patterns from production codebases
- Quality: Diverse examples from various programming languages and projects
- Collection script: `scripts/collect_the_stack_json.py` (requires HuggingFace token)

**8. Microsoft JSON Schemas** (183 REAL production schemas) ✨
- Source: https://github.com/microsoft/json-schemas (MIT License)
- Content: Production JSON Schemas from Microsoft products
- Products: Fabric, Office-JS, Teams Toolkit, Copilot, Rush, API-Extractor
- Task: Text description → JSON Schema (fixes critical weakness)
- Quality: **Real production schemas** (not synthetic)
- Impact: **Schema generation 3/10 → 8+/10 target**

**9. Synthetic Text-to-Schema** (48 examples):
- Content: Template-based schema generation
- Types: Simple objects, nested, arrays, API responses, pagination
- Focus: Covers common schema patterns

**10. Enhanced JSON Repair** (72 examples):
- Content: Explicit syntax error → fix patterns
- Errors: Missing commas (32), trailing commas (12), unquoted keys (12), quotes (8), multiple (8)
- Focus: **Fixes missing comma problem** (current: 7/10 → target: 9+/10)

### Key Dataset Strengths (v0.4.0)

- **Diversity**: 10 sources covering APIs, configs, events, extraction, schemas, repair, codebase examples
- **Quality**: 100% valid JSON after filtering + deduplication
- **Complexity**: Avg 3,066 chars/JSON (MasterControl), balanced with simpler examples
- **Real-world**: APIs.guru (production APIs), MasterControl (business docs), **Microsoft (production schemas)**
- **Tasks**: Generation (32.6%), Extraction (27.4%), Correction (39.2%) - Balanced
- **Production Quality**: 183 Microsoft schemas from real products (Fabric, Teams, Office, Copilot)

### Dataset Statistics (v0.5.0)

**Total: 40,000 examples** (rebalanced to focus on quality and known issues)

**Format Distribution:**
- JSON schema: 10,919 (27.3%) – Schema generation (SchemaStore + Microsoft)
- Data extraction: 9,938 (24.8%) – MasterControl + Paraloq transformations
- OpenAPI schema: 9,705 (24.3%) – APIs.guru schema coverage
- CloudEvents: 4,741 (11.9%) – Structured event formats
- OpenAPI response: 2,915 (7.3%) – Response payload shaping
- OpenAPI request: 1,710 (4.3%) – Type-specific request payloads
- Generic / other: 72 (0.2%) – Legacy prompts & misc.

**Task Distribution:**
- JSON generation: 21,407 (53.5%)
- Schema generation: 221 (0.6%)
- JSON correction: 18,372 (45.9%)

**Complexity Distribution:**
- Very complex: 14,975 (37.4%)
- Medium: 12,008 (30.0%)
- Simple: 7,939 (19.8%)
- Complex: 5,078 (12.7%)

**Quality Improvements v0.5.0:**
- ✅ Dataset rebalanced to 40k examples (quality over quantity)
- ✅ Schema + data extraction formats exceed 75% of the corpus
- ✅ Priority formats focus on known issues:
  - Schema generation coverage (json_schema + openapi_schema)
  - Transformations (data_extraction)
  - Array handling (openapi_response)
  - Type conversion (openapi_request)
- ✅ Distribution charts generated (`docs/dataset_distribution.png`, `docs/task_distribution.png`, `docs/complexity_distribution.png`)

### Preprocessing Applied

- ✅ JSON syntax validation
- ✅ Content hash deduplication
- ✅ ChatML formatted for Qwen3 native support
- ✅ Schema inclusion (where applicable)
- ✅ Mixed generation and correction tasks

### Example Entry (Preprocessed)

**Generation Task:**
```
<|system|>
Task: json_generation
Format: openapi_response
Schema:
{
  "type": "object",
  "properties": {
    "userId": {"type": "string"},
    "name": {"type": "string"}
  },
  "required": ["userId", "name"]
}
<|end|>
<|user|>
Generate a valid 200 response for GET /api/users/{id}
<|end|>
<|assistant|>
{
  "userId": "123",
  "name": "John Doe",
  "email": "john@example.com"
}
<|end|>
```

**Correction Task:**
```
<|system|>
Task: json_correction
Format: openapi
Error type: missing_field
<|end|>
<|user|>
Fix this invalid JSON:
{"name": "John Doe"}
<|end|>
<|assistant|>
{"userId": "123", "name": "John Doe"}
<|end|>
```

## Configuration

### Adapter: DoRA r=14

```json
{
  "type": "dora",
  "rank": 14,
  "alpha": 28,
  "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj"]
}
```

- **Why DoRA?** Better quality than LoRA for structured output
- **Why r=14?** Balanced between SQL (r=12) and Neo4j (r=16) - JSON is moderately complex
- **Why full modules?** MLP (up/down) crucial for JSON structure understanding

### Decoding: Optimized (Unsloth/Qwen Recommended)

```json
{
  "temperature": 0.7,
  "top_p": 0.8,
  "top_k": 20,
  "grammar_type": "json",
  "validation": "parser-strict",
  "stop_sequences": ["\n\n"]
}
```

- **Temperature 0.7**: Qwen3 recommended (prevents repetition collapse)
- **Top-P 0.8**: Unsloth recommended (better diversity)
- **Top-K 20**: Focused sampling
- **Grammar**: Enforces valid JSON syntax (RFC 8259)
- **Stop sequences**: Prevents over-generation

### Training: Windows Optimized + Unsloth

```json
{
  "use_unsloth": true,
  "batch_size": 2,
  "gradient_accumulation_steps": 45,
  "learning_rate": 5e-5,
  "warmup_ratio": 0.1,
  "dropout": 0.1,
  "epochs": 1.5,
  "lr_scheduler": "cosine",
  "use_sdpa": true,
  "bf16": true,
  "torch_compile": false
}
```

**Performance**:
- **Effective batch**: 90 (2 × 45) - compensates for small batch
- **VRAM usage**: ~0.6-1.0GB / 24GB (2.5-4%) - 70% reduction with Unsloth
- **Training speed**: ~2x faster with Unsloth vs standard PyTorch
- **Windows safe**: Small batch prevents memory issues

## Data Collection

### Run All Collection Scripts

```powershell
# Automated collection (recommended)
cd F:/Node/hivellm/expert/experts/expert-json
python scripts/run_collection.py

# This will:
# 1. CloudEvents (~5 minutes, ~5k examples)
# 2. SchemaStore (~1-2 hours, ~10-15k examples)
# 3. APIs.guru (~2-4 hours, ~30-40k examples)
# 4. Paraloq (~5 minutes, ~500 examples from HuggingFace)
# 5. MasterControl (~2 minutes, 10k examples from HuggingFace)
# 6. Generate negative examples (~30 minutes, ~25-35k examples)
# Total: ~3-7 hours depending on network speed
```

### Manual Collection (Step by Step)

```powershell
# 1. CloudEvents (fast - generates synthetic events)
python scripts/collect_cloudevents.py

# 2. SchemaStore (moderate - downloads schemas + generates examples)
python scripts/collect_schemastore.py

# 3. APIs.guru (slowest - downloads many specs)
python scripts/collect_apis_guru.py

# 4. Paraloq (fast - downloads from HuggingFace)
python scripts/collect_paraloq.py

# 5. MasterControl (fast - downloads from HuggingFace)
python scripts/collect_mastercontrol.py

# 6. The Stack (optional – requires HuggingFace token to collect JSON from codebase)
$env:HF_TOKEN = "your_token_here"
powershell -ExecutionPolicy Bypass -File scripts/run_the_stack_collection.ps1
# Or directly:
python scripts/collect_the_stack_json.py --limit 50000 --max-check 1000000

# 7. Negative examples (fast - corrupts existing examples)
python scripts/generate_negatives.py
```

### Data Directory Structure

```
datasets/
├── raw/
│   ├── apis_guru/
│   │   ├── apis_guru_examples.jsonl
│   │   └── collection_stats.json
│   ├── schemastore/
│   │   ├── schemastore_examples.jsonl
│   │   └── collection_stats.json
│   ├── cloudevents/
│   │   ├── cloudevents_examples.jsonl
│   │   └── collection_stats.json
│   ├── paraloq/
│   │   ├── paraloq_examples.jsonl
│   │   └── collection_stats.json
│   ├── mastercontrol/
│   │   ├── mastercontrol_examples.jsonl
│   │   └── collection_stats.json
│   ├── the_stack_json/
│   │   └── the_stack_json.jsonl
│   └── negatives/
│       ├── negative_examples.jsonl
│       └── generation_stats.json
├── train.jsonl  (final preprocessed dataset)
└── preprocessing_stats.json
```

## Training

### After Dataset Collection

```bash
# From expert-json directory
cd F:/Node/hivellm/expert/experts/expert-json

# Preprocess all sources into unified format
python preprocess.py

# Validate dataset quality
python scripts/validate_dataset.py

# Start training
../../cli/target/release/expert-cli train
```

### Actual Training Stats (v0.5.0)

**Dataset**: 40,000 examples (rebalanced)  
**Effective Batch Size**: 90 (2 × 45 gradient accumulation)  
**Total Steps**: ~445 steps (estimated, checkpoint-500 selected)  
**Training Time**: ~1-2 hours (RTX 4090 + Unsloth, faster with smaller dataset)  
**VRAM Usage**: ~0.6-1.0GB during training (70% reduction with Unsloth)

## Performance

### Training Checkpoints (v0.5.0)

**Checkpoints Tested:**
- `checkpoint-250` - Score: 5/15 (33%) - Loops, schema confusion
- `checkpoint-500` ⭐ - Score: 6/15 (40%) - **SELECTED** - Best balance
- `checkpoint-638` - Score: 6/15 (40%) - Similar to 500, trailing comma issues
- `final` - Score: 5/15 (33%) - Loops, regression

**Selected: Checkpoint-500** - Best overall performance with no infinite loops

### Actual Results (Checkpoint-500)

**Quality Metrics:**
- **Benchmark Score**: 40% (6/15 complex tests)
- **Simple Schema Generation**: ✅ 10/10 (perfect)
- **JSON Repair**: ✅ 9/10 (excellent)
- **Nested Structures**: ✅ 8/10 (good)
- **Transformations**: ⚠️ 3/10 (limited)

**Practical Testing (CLI):**
- ✅ Simple schemas: Perfect generation
- ✅ JSON repair: Perfect for syntax errors
- ⚠️ Complex nested: Returns examples instead of schemas
- ⚠️ Transformations: Not supported

**Inference Performance:**
- Adapter size: ~29.54 MB (package size)
- Load time: <200ms (cold start)
- Generation speed: ~100-150ms per response (RTX 4090)
- Trainable parameters: ~9.9M of 604.5M (1.64% trained)

## Usage

### Using the Package (v0.4.0)

**Package Information:**
- **File**: `expert-json-qwen3-06b.v0.5.0.expert` (to be generated)
- **Checkpoint**: checkpoint-500 (best performing from v0.4.0)
- **Dataset**: 40,000 rebalanced examples (schema/data-heavy generation + broad correction coverage)

**Installation:**
```bash
# Install the package
expert-cli install expert-json-qwen3-06b.v0.4.0.expert
```

### Interactive Chat

```bash
# Start interactive JSON generation
expert-cli chat --experts json

# Example prompts:
> Create JSON schema for a user with name and email
> Fix this JSON: {"name": "John" "age": 30}
> Generate JSON schema for a product with id, name, price
```

### One-Shot Mode (CLI)

```bash
# Generate schema
expert-cli chat --experts json --prompt "Create JSON schema for a user with name (string), age (number), email (string)" --max-tokens 200

# Fix JSON
expert-cli chat --experts json --prompt 'Fix JSON: {"id": 123, "active": true,}' --max-tokens 100

# Expected outputs:
# Schema: {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "number"}, "email": {"type": "string"}}}
# Repair: {"id": 123, "active": true}
```

### Python Integration

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model_path = "F:/Node/hivellm/expert/models/Qwen3-0.6B"
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)

# Load expert adapter
adapter_path = "weights/qwen3-06b/checkpoint-500"  # Best performing checkpoint (v0.4.0)
model = PeftModel.from_pretrained(base_model, adapter_path)

# Generate JSON
schema = {
    "type": "object",
    "properties": {
        "userId": {"type": "string"},
        "name": {"type": "string"}
    },
    "required": ["userId", "name"]
}

question = "Generate a valid user profile object"

messages = [
    {"role": "system", "content": f"Task: json_generation\nFormat: openapi\nSchema:\n{json.dumps(schema, indent=2)}"},
    {"role": "user", "content": question}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.8,
        top_k=20
    )

result = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(result)
```

## Credits

- **Base Model**: Qwen/Qwen3-0.6B
- **Datasets (v0.5.0 Rebalanced)**: 
  - APIs.guru (OpenAPI specifications) – ~14k schema/request/response examples
  - SchemaStore.org + Microsoft/json-schemas – ~11k production-grade JSON schemas ✨
  - CloudEvents (CNCF) – 4,741 event payloads
  - Paraloq (Data extraction) – 484 curated text→JSON transformations
  - MasterControlAIML (Structured extraction) – 9,000+ complex document conversions
  - Generated negatives – 18,372 curated correction examples (syntax + semantic)
  - Synthetic text-to-schema – 48 edge-case schemas
  - Enhanced JSON repair – 72 high-value corruption patterns
  - **Total final dataset**: 40,000 examples (schema/data-heavy generation + broad corrections)
- **Training**: Unsloth (2x speedup, 70% less VRAM)
- **Framework**: HuggingFace Transformers + PEFT + TRL + Candle (Rust inference)

## License

CC-BY-4.0

## Tags

json, openapi, swagger, json-schema, cloudevents, api-development, configuration, data-validation, autocorrection, qwen3, dora, unsloth, windows
