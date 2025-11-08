# 📚 Expert-JSON Documentation Index

Quick navigation guide for all dataset documentation and analysis files.

## 🎯 Start Here

New to the dataset? Read these in order:

1. **[README.md](README.md)** - Documentation overview and guide
2. **[DATASET_DISTRIBUTION.md](DATASET_DISTRIBUTION.md)** - Statistical analysis with charts
3. **[DATASET_QUALITY_REPORT.md](DATASET_QUALITY_REPORT.md)** - Validation and quality report

## 📄 File Guide

### README.md
- **What:** Documentation structure and usage guide
- **When to read:** First time exploring the docs
- **Contains:**
  - File overview
  - Quick stats summary
  - How to regenerate documentation
  - Key insights interpretation

### DATASET_DISTRIBUTION.md
- **What:** Complete statistical analysis with ASCII visualizations
- **When to read:** Understanding dataset composition
- **Contains:**
  - Task distribution (60.5% generation, 39.5% correction)
  - Format breakdown (7 formats)
  - Error types analysis (4 types)
  - Size statistics (min/median/max)
  - Quality metrics
  - Data sources overview

### DATASET_QUALITY_REPORT.md
- **What:** Validation results and quality assessment
- **When to read:** Verifying dataset is ready for training
- **Contains:**
  - Raw data validation (258,435 examples)
  - Processing results (37,937 final examples)
  - Quality assurance checks
  - Issue resolution documentation
  - Training approval status

### dataset_analysis.json
- **What:** Machine-readable statistics
- **When to use:** Automation, scripting, custom tools
- **Format:** JSON
- **Contains:**
  - All statistics in structured format
  - Distributions, percentages, counts
  - Size metrics and percentiles

## 📊 Visualizations

### ASCII Charts (Built-in)

All markdown files include **ASCII/Unicode visualizations** that work in any viewer:

```
Task Types
==================================================
generation  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    ] 22,937 (60.5%)
correction  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               ] 15,000 (39.5%)
```

### PNG Charts (Optional)

If matplotlib is installed, run `scripts/generate_charts.py` to create:
- `charts/overview_dashboard.png`
- `charts/task_distribution.png`
- `charts/format_distribution.png`
- `charts/size_distribution.png`
- `charts/error_types.png`

## 🔍 Quick Lookups

### Dataset Stats
```
Total: 37,937 examples (52.96 MB)
Tasks: 60.5% Gen, 39.5% Correction
Formats: 7 types (data_extraction 27.6%, cloudevents 20.2%, ...)
Errors: 4 types (balanced ~25% each)
```

### Quality Checks
```
✅ JSON Validity: 100%
✅ ChatML Format: 100%
✅ Deduplication: 162,557 removed
✅ Size Filter: Applied (<50 chars removed)
⚠️  Task Balance: 27.2% deviation from 50/50
```

### Size Stats
```
Min:       155 chars
Median:    859 chars  
Mean:    1,464 chars
P90:     3,392 chars
Max:   413,413 chars (outlier - large schema)
```

## 📖 Reading Guide by Use Case

### Planning Training

1. **DATASET_DISTRIBUTION.md** → Check task balance and format diversity
2. **DATASET_DISTRIBUTION.md** § Size Statistics → Choose context length
3. **DATASET_DISTRIBUTION.md** § Training Recommendations → Configure hyperparameters

### Evaluating Quality

1. **DATASET_QUALITY_REPORT.md** → Verify validation passed
2. **DATASET_QUALITY_REPORT.md** § Quality Assurance → Review all checks
3. **DATASET_DISTRIBUTION.md** § Quality Metrics → Confirm standards

### Designing Tests

1. **DATASET_DISTRIBUTION.md** § Format Distribution → Cover all formats
2. **DATASET_DISTRIBUTION.md** § Error Types → Include all error scenarios
3. **DATASET_DISTRIBUTION.md** § Use Cases → Test each capability

### Debugging Issues

1. **dataset_analysis.json** → Get exact numbers programmatically
2. **DATASET_QUALITY_REPORT.md** § Issues & Resolutions → Check known problems
3. **DATASET_DISTRIBUTION.md** → Identify distribution anomalies

### Reporting Results

1. **README.md** § Key Insights → Understand context
2. **DATASET_DISTRIBUTION.md** → Reference statistics
3. **DATASET_QUALITY_REPORT.md** → Cite quality metrics

## 🔄 Updating Documentation

When dataset changes:

```bash
# Step 1: Regenerate statistics
python3 scripts/analyze_dataset.py

# Step 2: Update markdown docs  
python3 scripts/generate_ascii_charts.py

# Step 3 (optional): Generate PNG charts
python3 scripts/generate_charts.py
```

All files automatically update with new data.

## 🗂️ Related Files

Outside `docs/`:
- `../README.md` - Main expert-json setup and usage
- `../preprocess.py` - Dataset creation script
- `../datasets/train.jsonl` - Actual training data
- `../datasets/preprocessing_stats.json` - Processing metadata
- `../scripts/` - Collection and analysis scripts

## 💡 Tips

### Viewing ASCII Charts

Works best in:
- Terminal with Unicode support
- GitHub/GitLab markdown viewers
- VS Code markdown preview
- Any modern text editor

### Searching Statistics

Use `dataset_analysis.json` for:
```bash
# Get total examples
jq '.summary.total_examples' dataset_analysis.json

# Get generation task count
jq '.task_distribution.generation' dataset_analysis.json

# Get median size
jq '.size_statistics.median' dataset_analysis.json
```

### Comparing Versions

```bash
# Save current stats
cp dataset_analysis.json dataset_analysis_v1.json

# After reprocessing
diff dataset_analysis_v1.json dataset_analysis.json
```

---

**Last Updated:** Check file timestamps  
**Generated By:** Expert-JSON Analysis Pipeline  
**Maintainer:** HiveLLM Team

