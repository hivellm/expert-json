# Expert-JSON Setup Complete ✅

**Date:** 2025-11-06  
**Version:** 0.1.0  
**Status:** Ready for data collection

---

## What Was Created

### 📁 Project Structure

```
expert-json/
├── manifest.json              ✅ Training configuration (DoRA r=14)
├── grammar.gbnf               ✅ JSON grammar (RFC 8259)
├── preprocess.py              ✅ Unified preprocessing pipeline
├── README.md                  ✅ Documentation
├── LICENSE                    ✅ CC-BY-4.0 with dataset citations
├── .gitignore                 ✅ Ignore patterns
├── scripts/
│   ├── collect_apis_guru.py        ✅ APIs.guru collector (~20-30k)
│   ├── collect_schemastore.py      ✅ SchemaStore collector (~15-20k)
│   ├── collect_cloudevents.py      ✅ CloudEvents generator (~5k)
│   ├── generate_negatives.py       ✅ Invalid JSON + corrections (~30-40k)
│   ├── run_collection.py           ✅ Automated runner
│   ├── validate_dataset.py         ✅ Dataset quality validation
│   └── README.md                   ✅ Scripts documentation
└── datasets/                   (created, empty - awaiting collection)
    └── raw/                    (subdirs created)
```

---

## Configuration Summary

### Dataset Target
- **Total**: 100k+ examples
- **Sources**:
  - APIs.guru: ~20-30k (OpenAPI specs)
  - SchemaStore: ~15-20k (JSON Schemas)
  - CloudEvents: ~5k (event format)
  - Negatives: ~30-40k (autocorrection)

### Format Distribution
- **Generation tasks**: 60-70% (create valid JSON)
- **Correction tasks**: 30-40% (fix invalid JSON)

### Supported Formats
1. **OpenAPI** (Swagger 2.0/3.x) - Request/response schemas
2. **JSON Schema** (Draft 2020-12) - Configuration files
3. **CloudEvents** (v1.0) - Event data format
4. **Generic JSON** - Any valid JSON structure

### Training Config
- **Adapter**: DoRA rank=14, alpha=28
- **Batch**: 2 + gradient_accumulation=45 (effective=90)
- **Learning rate**: 5e-5
- **Epochs**: 1.5
- **Checkpoints**: Every 250 steps, keep all
- **Unsloth**: Enabled (2x faster)

---

## Next Steps

### Step 1: Collect Data (3-7 hours)

```bash
cd F:/Node/hivellm/expert/experts/expert-json

# Option A: Automated (recommended)
python scripts/run_collection.py

# Option B: Manual
python scripts/collect_apis_guru.py      # 2-4 hours
python scripts/collect_schemastore.py    # 1-2 hours
python scripts/collect_cloudevents.py    # 5 minutes
python scripts/generate_negatives.py     # 30 minutes
```

### Step 2: Preprocess (5-10 minutes)

```bash
python preprocess.py
# Output: datasets/train.jsonl (~100k examples)
```

### Step 3: Validate (1 minute)

```bash
python scripts/validate_dataset.py
# Checks format distribution, JSON validity, sample quality
```

### Step 4: Train (4-5 hours estimated)

```bash
../../cli/target/release/expert-cli train
# Checkpoints: 250, 500, 750, 1000, 1250, 1500, ~1667
```

### Step 5: Evaluate (after training)

Create benchmark similar to SQL expert:
- 20-30 JSON generation scenarios
- 10-15 autocorrection scenarios
- Test each checkpoint
- Select best checkpoint based on quality

---

## Expected Outcomes

### Training Metrics (Estimated)
- **Training time**: ~4-5 hours (RTX 4090 + Unsloth)
- **VRAM usage**: ~0.7-1.0GB (2.9-4.2% of 24GB)
- **Adapter size**: ~44MB (DoRA r=14)
- **Checkpoints**: 7-8 checkpoints saved

### Quality Targets (Aspirational)
- **JSON syntax**: 100% valid (enforced by grammar)
- **Schema compliance**: 90%+ (for OpenAPI/JSON Schema)
- **Autocorrection**: 80%+ success (fix common errors)
- **Format awareness**: 95%+ (recognize OpenAPI vs CloudEvents vs generic)

---

## Differences from SQL Expert

| Aspect | SQL Expert | JSON Expert |
|--------|-----------|-------------|
| **Dataset size** | 99,935 | ~100k+ (target) |
| **Sources** | Single (gretelai) | Multiple (3 sources) |
| **Tasks** | Generation only | Generation + Correction |
| **DoRA rank** | 12 | 14 (more complex) |
| **Formats** | 1 (PostgreSQL) | 3+ (OpenAPI, JSON Schema, CloudEvents) |
| **Validation** | sqlglot | JSON parsers |

---

## Dependencies

```bash
# Collection phase
pip install requests faker hypothesis jsonschema

# Already installed (from SQL/Neo4j)
pip install datasets transformers peft torch trl unsloth
```

---

## Notes

- ✅ All scripts tested for syntax (not executed yet)
- ✅ Configuration matches SQL expert best practices
- ✅ DoRA r=14 chosen (between SQL r=12 and Neo4j r=16)
- ✅ Supports autocorrection (unique to JSON expert)
- ✅ Multi-source dataset for better generalization
- ⚠️ Data collection required before training
- ⚠️ Estimated 3-7 hours for complete data collection
- ⚠️ Network-dependent (APIs.guru downloads many files)

---

**Status:** Expert-JSON is configured and ready for data collection! 🚀

