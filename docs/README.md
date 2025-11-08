# Expert-JSON Documentation

Comprehensive documentation for the Expert-JSON dataset, including statistical analysis, distribution charts, and quality metrics.

## 📁 Files Overview

| File | Description | Format |
|------|-------------|--------|
| **DATASET_DISTRIBUTION.md** | Complete dataset analysis with ASCII charts | Markdown |
| **dataset_analysis.json** | Raw statistical data (machine-readable) | JSON |
| **charts/** | Visual charts and graphs *(if matplotlib installed)* | PNG |

## 📊 Quick Stats

```
Total Examples: 37,937
Total Size:     52.96 MB
Tasks:          60.5% Generation, 39.5% Correction
Top Format:     Data Extraction (27.6%)
Quality:        100% Valid JSON, 100% ChatML Format
```

## 📖 Documentation Structure

### 1. DATASET_DISTRIBUTION.md

**Main documentation file** with comprehensive analysis:

- **Overview**: Total examples, size, averages
- **Task Distribution**: Generation vs Correction breakdown
- **Format Distribution**: OpenAPI, JSON Schema, CloudEvents, etc.
- **Error Types**: Correction task categories
- **Size Statistics**: Min, median, mean, max with percentiles
- **Quality Metrics**: Validation status, balance metrics
- **Data Sources**: 6 sources with quality ratings
- **Use Cases**: Supported scenarios
- **Training Recommendations**: Hyperparameters and configuration

**Contains ASCII charts** for all distributions - no external dependencies required!

### 2. dataset_analysis.json

**Machine-readable statistics** for integration with other tools:

```json
{
  "summary": {
    "total_examples": 37937,
    "total_size_bytes": 55539154
  },
  "task_distribution": {
    "generation": 22937,
    "correction": 15000
  },
  "format_distribution": { ... },
  "error_types": { ... },
  "size_statistics": { ... },
  "json_size_statistics": { ... }
}
```

**Use cases:**
- Automated quality checks
- CI/CD pipeline integration
- Custom visualization tools
- Experiment tracking (MLflow, W&B)

### 3. charts/ *(optional)*

If matplotlib is installed, run `python3 scripts/generate_charts.py` to generate:

- `overview_dashboard.png` - Comprehensive dashboard with all metrics
- `task_distribution.png` - Pie chart of task types
- `format_distribution.png` - Bar chart of formats
- `size_distribution.png` - Box plot and statistics
- `error_types.png` - Bar chart of correction error types

## 🚀 Generating Documentation

### Analyze Dataset

```bash
cd expert/experts/expert-json
python3 scripts/analyze_dataset.py
```

**Outputs:**
- `docs/dataset_analysis.json` - Statistical data
- Console summary with all metrics

### Generate Markdown Documentation

```bash
python3 scripts/generate_ascii_charts.py
```

**Outputs:**
- `docs/DATASET_DISTRIBUTION.md` - Comprehensive markdown report with ASCII charts

### Generate Visual Charts *(requires matplotlib)*

```bash
# Install dependencies (optional)
pip install matplotlib numpy

# Generate charts
python3 scripts/generate_charts.py
```

**Outputs:**
- `docs/charts/*.png` - 5 high-resolution charts (300 DPI)

## 📈 Key Insights

### Task Balance

Current distribution is **60.5% Generation / 39.5% Correction** with a **27.2% deviation** from the ideal 50/50 balance.

**Why this balance?**
- Generation tasks teach JSON structure and schema compliance
- Correction tasks teach error handling and validation
- 60/40 split emphasizes creation over repair (intentional design)

### Format Diversity

7 distinct formats ensure the model handles diverse JSON scenarios:

1. **Data Extraction** (27.6%) - Complex document parsing
2. **CloudEvents** (20.2%) - Event-driven architectures
3. **OpenAPI Property** (19.3%) - API field definitions
4. **JSON Schema** (17.2%) - Configuration files
5. **OpenAPI Schema** (10.2%) - Complete API specs
6. **OpenAPI Response** (3.2%) - API responses
7. **OpenAPI Request** (1.3%) - API requests

### Error Coverage

All major JSON error types are equally represented:

- **Extra Field** (25.6%) - Unknown properties
- **Type Mismatch** (25.2%) - Wrong data types
- **Syntax Error** (24.7%) - Invalid JSON syntax
- **Missing Field** (24.5%) - Required fields absent

This **balanced error distribution** ensures robust correction capabilities.

### Size Distribution

- **Median:** 859 characters (compact examples)
- **Mean:** 1,464 characters (some large schemas)
- **P90:** 3,392 characters (manageable for training)
- **Max:** 413,413 characters (edge case - single large schema)

Most examples (75%) are under 2,216 characters, keeping training efficient.

## 🔍 Quality Assurance

All metrics validate **production-ready** quality:

| Metric | Status | Details |
|--------|--------|---------|
| **JSON Validity** | ✅ 100% | All examples parse successfully |
| **ChatML Format** | ✅ 100% | Proper system/user/assistant structure |
| **Deduplication** | ✅ Applied | SHA-256 hashing removes 162,557 duplicates |
| **Size Filtering** | ✅ Applied | Min 50 chars, object/array types only |
| **Source Diversity** | ✅ 6 sources | APIs.guru, SchemaStore, CloudEvents, Paraloq, MasterControl, Negatives |
| **Error Balance** | ✅ ~25% each | All 4 error types equally represented |

## 📚 Additional Resources

- **Main README**: `../README.md` - Setup and training instructions
- **Quality Report**: `../DATASET_QUALITY_REPORT.md` - Detailed validation report
- **Collection Scripts**: `../scripts/` - Data collection automation
- **Preprocessing**: `../preprocess.py` - Dataset creation pipeline

## 🔄 Updating Documentation

When the dataset changes:

```bash
# 1. Reprocess dataset (if raw data changed)
python3 preprocess.py

# 2. Regenerate analysis
python3 scripts/analyze_dataset.py

# 3. Update markdown docs
python3 scripts/generate_ascii_charts.py

# 4. (Optional) Regenerate charts
python3 scripts/generate_charts.py
```

All documentation files will be automatically updated with new statistics.

## 💡 Use Cases for This Documentation

### For Training

- Verify dataset quality before training
- Choose appropriate hyperparameters based on size stats
- Understand task distribution for evaluation design

### For Evaluation

- Design test sets covering all formats
- Create balanced evaluation scenarios
- Benchmark against error type distribution

### For Production

- Document model capabilities (formats, tasks)
- Set user expectations for supported use cases
- Monitor drift between training and inference data

### For Research

- Reproduce experiments with exact statistics
- Compare dataset versions
- Analyze performance by format/task type

---

**Generated by:** Expert-JSON Dataset Analysis Pipeline  
**Last Updated:** Check file timestamps  
**Maintainer:** HiveLLM Team

