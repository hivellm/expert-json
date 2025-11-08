# Expert-JSON Collection Scripts

Data collection scripts for building the expert-json training dataset.

## Scripts

### 1. `collect_apis_guru.py`
**Source:** https://api.apis.guru/v2/list.json  
**Content:** OpenAPI 2.0/3.x specifications from ~3000 real APIs  
**Time:** 2-4 hours (network-dependent)  
**Output:** ~20-30k examples  

**What it extracts:**
- `components.schemas` definitions with examples
- Request/response body examples from paths
- Property examples from schema definitions

### 2. `collect_schemastore.py`
**Source:** https://www.schemastore.org/api/json/catalog.json  
**Content:** JSON Schemas for common tools and configurations  
**Time:** 1-2 hours  
**Output:** ~15-20k examples  

**What it generates:**
- Valid JSON objects from schemas using faker/hypothesis
- 3-8 variants per schema for diversity
- Covers: ESLint, Prettier, package.json, tsconfig, etc.

### 3. `collect_cloudevents.py`
**Source:** CNCF CloudEvents specification  
**Content:** Synthetic event examples  
**Time:** 5 minutes  
**Output:** ~5k examples  

**Variants:**
- Minimal: Only required fields (specversion, type, source, id)
- Standard: Required + time
- Full: All optional fields (datacontenttype, dataschema, subject)
- Extensions: Custom extension fields

### 4. `generate_negatives.py`
**Source:** Generated from collected positive examples  
**Content:** Invalid JSON + corrections  
**Time:** 30 minutes  
**Output:** ~30-40k examples  

**Corruption types:**
- `missing_field`: Remove required field
- `type_mismatch`: Change field type (string ↔ number)
- `extra_field`: Add unknown field
- `syntax_error`: Trailing commas, unquoted keys, etc.

### 5. `run_collection.py`
**Purpose:** Automated runner for all collection scripts  
**Time:** 3-7 hours total  

Runs all scripts in sequence with progress tracking.

### 6. `validate_dataset.py`
**Purpose:** Validate preprocessed dataset quality  
**Time:** 1-2 minutes  

Checks:
- Sample 100 random examples
- Format distribution (OpenAPI 40%, SchemaStore 30%, etc.)
- JSON parseability
- Task distribution (generation 60-80%, correction 20-40%)

## Requirements

```bash
pip install requests faker hypothesis jsonschema
```

## Usage

### Option 1: Automated (Recommended)

```bash
python run_collection.py
```

### Option 2: Manual (Step by Step)

```bash
# Slowest first (can run overnight)
python collect_apis_guru.py

# Moderate speed
python collect_schemastore.py

# Fast
python collect_cloudevents.py
python generate_negatives.py
```

## Output Structure

```
datasets/raw/
├── apis_guru/
│   ├── apis_guru_examples.jsonl        (~20-30k examples)
│   └── collection_stats.json
├── schemastore/
│   ├── schemastore_examples.jsonl      (~15-20k examples)
│   └── collection_stats.json
├── cloudevents/
│   ├── cloudevents_examples.jsonl      (~5k examples)
│   └── collection_stats.json
└── negatives/
    ├── negative_examples.jsonl         (~30-40k examples)
    └── generation_stats.json

Total: ~70-95k raw examples
After deduplication: ~100k+ unique examples
```

## Next Steps

After collection:
1. Run `../preprocess.py` to create unified `datasets/train.jsonl`
2. Run `validate_dataset.py` to check quality
3. Start training with expert-cli

## Notes

- **Rate Limiting**: Scripts include delays to avoid overwhelming APIs
- **Error Handling**: Continues on errors, logs failures
- **Deduplication**: Handled in preprocessing step
- **Caching**: Raw data saved for reprocessing without re-downloading

