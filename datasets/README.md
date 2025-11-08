# Expert JSON - Dataset Documentation

This directory contains the training datasets for the Expert JSON model, combining 9 high-quality sources into a unified ChatML-formatted dataset.

## Dataset Overview

**Total: 40,000 examples** (v0.5.0)

**Splits:**
- **Training**: 36,002 examples (90%)
- **Validation**: 1,999 examples (5%)
- **Test**: 1,999 examples (5%)

**Format**: ChatML (Qwen3 native format)  
**Quality**: 100% valid JSON after preprocessing and deduplication  
**Preprocessing**: JSON syntax validation, SHA256 deduplication, stratified splits

> **Note:** The detailed per-source breakdown below is being refreshed. The overall totals above reflect the current v0.5.0 dataset (40,000 examples).

## Dataset Structure

```
datasets/
├── raw/                          # Raw collected data (before preprocessing)
│   ├── apis_guru/               # OpenAPI specifications
│   ├── schemastore/             # JSON Schema catalog
│   ├── cloudevents/             # CloudEvents examples
│   ├── paraloq/                 # Text-to-JSON extraction
│   ├── mastercontrol/           # Document extraction
│   ├── negatives/               # Invalid JSON + corrections
│   └── microsoft_schemas/       # Microsoft production schemas
├── microsoft_text_to_schema/    # Processed Microsoft schemas (ChatML)
├── text_to_schema/              # Synthetic schema templates (ChatML)
├── json_repair_enhanced/       # Enhanced repair patterns (ChatML)
├── final/                       # Final processed dataset
│   ├── train.jsonl             # 36,002 examples
│   ├── validation.jsonl         # 1,999 examples
│   └── test.jsonl               # 1,999 examples
├── train.jsonl                  # Main training file (symlink to final/)
├── validation.jsonl             # Main validation file (symlink to final/)
├── test.jsonl                   # Main test file (symlink to final/)
└── preprocessing_stats.json     # Preprocessing statistics
```

## Data Sources (9 Sources)

### Primary Sources (37,937 examples)

**1. APIs.guru** (4,240 examples - 11.1%)
- **Source**: https://api.apis.guru/v2/list.json
- **Content**: OpenAPI 2.0/3.x specifications from real APIs
- **Extraction**: Schema definitions, request/response examples
- **Focus**: REST API payloads
- **Quality filter**: Only objects/arrays >50 chars

**2. SchemaStore** (3,213 examples - 8.4%)
- **Source**: https://www.schemastore.org/api/json/catalog.json
- **Content**: JSON Schemas for common tools (ESLint, Prettier, tsconfig, package.json, etc.)
- **Generation**: Valid examples from schemas (50% complete, 50% minimal)
- **Focus**: Configuration files
- **Quality filter**: Exclude objects <30 chars

**3. CloudEvents** (5,000 examples - 13.1%)
- **Source**: CNCF CloudEvents specification
- **Content**: Event format variants with 18 diverse payload types
- **Generation**: Synthetic events (user, e-commerce, file, infrastructure, code, data events)
- **Focus**: Event-driven architectures

**4. Paraloq Data Extraction** (484 examples - 1.3%)
- **Source**: https://huggingface.co/datasets/paraloq/json_data_extraction
- **Content**: High-quality text → JSON extraction (Gemini-Pro generated)
- **Domains**: Medical, Manufacturing, Travel, Business, E-commerce, Media, Technology, Simple
- **Focus**: Data extraction from unstructured text
- **Quality**: Curated, validated, diverse scenarios

**5. MasterControl Structured Extraction** (10,000 examples - 26.1%)
- **Source**: https://huggingface.co/datasets/MasterControlAIML/JSON-Unstructured-Structured
- **Content**: Complex document → JSON extraction (100% valid JSON, 97% valid schemas)
- **Domains**: Financial statements, Quality assurance, Risk assessment, Manufacturing, Compliance
- **Focus**: Complex data extraction (avg 3,066 chars per JSON)
- **Quality**: Excellent - All examples >1k chars, highly structured

**6. Negative Examples** (15,000 examples - 39.2%)
- **Source**: Generated from positive examples
- **Content**: Invalid JSON + corrections
- **Corruption types**:
  - Missing required fields
  - Type mismatches (string ↔ number)
  - Extra/unknown fields
  - Syntax errors (trailing commas, unquoted keys)
- **Focus**: Autocorrection training

### Enhancement Sources (v0.2.0: +303 examples)

**7. Microsoft JSON Schemas** (183 examples - 0.5%) ✨
- **Source**: https://github.com/microsoft/json-schemas (MIT License)
- **Content**: Production JSON Schemas from Microsoft products
- **Products**: Fabric, Office-JS, Teams Toolkit, Copilot, Rush, API-Extractor
- **Task**: Text description → JSON Schema (fixes critical weakness)
- **Quality**: **Real production schemas** (not synthetic)
- **Impact**: **Schema generation 3/10 → 8+/10 target**

**8. Synthetic Text-to-Schema** (48 examples - 0.1%)
- **Content**: Template-based schema generation
- **Types**: Simple objects, nested, arrays, API responses, pagination
- **Focus**: Covers common schema patterns

**9. Enhanced JSON Repair** (72 examples - 0.2%)
- **Content**: Explicit syntax error → fix patterns
- **Errors**: Missing commas (32), trailing commas (12), unquoted keys (12), quotes (8), multiple (8)
- **Focus**: **Fixes missing comma problem** (current: 7/10 → target: 9+/10)

## Task Distribution

**By Task Type:**
- **Generation**: 12,453 examples (32.6%) - Generate JSON from schema/description
- **Extraction**: 10,484 examples (27.4%) - Extract JSON from text/documents
- **Correction**: 15,000 examples (39.2%) - Fix invalid JSON
- **Schema Generation**: 231 examples (0.6%) - Generate JSON Schema from description

**By Format:**
- **Data Extraction**: 10,484 (27.4%)
- **CloudEvents**: 7,669 (20.0%)
- **OpenAPI Property**: 7,320 (19.1%)
- **JSON Schema**: 6,531 (17.1%)
- **OpenAPI Schema**: 3,876 (10.1%)
- **OpenAPI Response**: 1,213 (3.2%)
- **OpenAPI Request**: 494 (1.3%)

## Preprocessing Pipeline

### Steps Applied

1. **Load Raw Sources**
   - Load from `datasets/raw/` directories
   - Load enhanced sources (Microsoft, synthetic, repair)

2. **Format Conversion**
   - Convert all examples to ChatML format
   - System message: Task type, format, schema (if available)
   - User message: Natural language prompt or broken JSON
   - Assistant message: Valid JSON output

3. **Validation**
   - JSON syntax validation (all outputs must be valid JSON)
   - Schema validation (where applicable)
   - Size filtering (min 50 chars for most sources)

4. **Deduplication**
   - SHA256 content hash deduplication
   - Removed 162,557 duplicate examples
   - Preserves unique examples only

5. **Stratified Splitting**
   - 80/10/10 split (train/validation/test)
   - Maintains task distribution across splits
   - Ensures balanced representation

### Preprocessing Statistics

**Input**: 258,435 raw examples  
**Processed**: 38,240 examples  
**Duplicates Removed**: 162,557 examples  
**Errors**: 0 (100% valid JSON)

**By Source (Processed):**
- APIs.guru: 4,240
- SchemaStore: 3,213
- CloudEvents: 5,000
- Paraloq: 484
- MasterControl: 10,000
- Negatives: 15,000
- Microsoft schemas: 183
- Synthetic schemas: 48
- Repair enhanced: 72

## ChatML Format

Each example follows ChatML format for Qwen3:

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
  }
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

**Task Types:**
- `json_generation`: Generate JSON from schema/description
- `json_correction`: Fix invalid JSON
- `data_extraction`: Extract JSON from text/document
- `schema_generation`: Generate JSON Schema from description

**Format Types:**
- `openapi_request`, `openapi_response`, `openapi_schema`, `openapi_property`
- `json_schema`
- `cloudevents`
- `generic`

## Usage

### Preprocessing

```bash
# Run preprocessing (combines all sources)
cd F:/Node/hivellm/expert/experts/expert-json
python preprocess.py

# Output:
# - datasets/train.jsonl (30,592 examples)
# - datasets/validation.jsonl (3,824 examples)
# - datasets/test.jsonl (3,824 examples)
# - datasets/preprocessing_stats.json
```

### Training

```bash
# Train with preprocessed dataset
../../cli/target/release/expert-cli train --manifest manifest.json

# The manifest.json points to datasets/train.jsonl
```

### Validation

```bash
# Validate dataset quality
python scripts/validate_dataset.py

# Check preprocessing statistics
cat datasets/preprocessing_stats.json | python -m json.tool
```

## Dataset Quality

**Strengths:**
- ✅ **100% valid JSON** - All outputs validated
- ✅ **Diverse sources** - 9 different high-quality sources
- ✅ **Real-world data** - Production APIs, Microsoft schemas, business documents
- ✅ **Balanced tasks** - Generation, extraction, correction balanced
- ✅ **Stratified splits** - Maintains distribution across train/val/test

**Quality Metrics:**
- **Deduplication rate**: 62.9% (162,557 duplicates removed)
- **Validation pass rate**: 100% (all JSON valid)
- **Average JSON size**: ~859 chars (median), ~3,066 chars (P90 for MasterControl)
- **Schema coverage**: OpenAPI, JSON Schema, CloudEvents, generic

## Collection Scripts

**Raw Data Collection:**
- `scripts/collect_apis_guru.py` - Download OpenAPI specs
- `scripts/collect_schemastore.py` - Download schema catalog
- `scripts/collect_cloudevents.py` - Generate CloudEvents examples
- `scripts/collect_paraloq.py` - Download from HuggingFace
- `scripts/collect_mastercontrol.py` - Download from HuggingFace
- `scripts/generate_negatives.py` - Generate invalid JSON examples

**Enhanced Sources:**
- `scripts/extract_microsoft_schemas.py` - Extract from Microsoft repo
- `scripts/generate_schema_dataset.py` - Generate synthetic schemas
- `scripts/generate_repair_dataset.py` - Generate repair patterns

**Preprocessing:**
- `preprocess.py` - Main preprocessing script (combines all sources)
- `scripts/normalize_to_chatml.py` - Convert to ChatML format
- `scripts/create_enhanced_dataset.py` - Combine enhanced sources

## Version History

### v0.3.0 (Current)
- **Total**: 38,240 examples
- **Checkpoint**: checkpoint-500 selected (best performance)
- **Status**: Production-ready for JSON repair and simple schema generation

### v0.2.0 (Enhanced)
- **Added**: +303 examples (Microsoft schemas, synthetic schemas, repair enhanced)
- **Total**: 37,937 → 38,240 examples
- **Focus**: Schema generation and advanced repair

### v0.1.0 (Initial)
- **Total**: 37,937 examples
- **Sources**: 6 primary sources
- **Focus**: Basic JSON generation and correction

## References

- **APIs.guru**: https://api.apis.guru/v2/list.json
- **SchemaStore**: https://www.schemastore.org/api/json/catalog.json
- **CloudEvents**: https://cloudevents.io/
- **Paraloq**: https://huggingface.co/datasets/paraloq/json_data_extraction
- **MasterControl**: https://huggingface.co/datasets/MasterControlAIML/JSON-Unstructured-Structured
- **Microsoft Schemas**: https://github.com/microsoft/json-schemas

## License

- **APIs.guru**: CC-BY-4.0
- **SchemaStore**: Various (see catalog)
- **CloudEvents**: Apache 2.0
- **Paraloq**: Apache 2.0
- **MasterControl**: Apache 2.0
- **Microsoft Schemas**: MIT
- **Expert JSON**: CC-BY-4.0
