# Expert-JSON Dataset Analysis

**Generated:** `dataset_analysis.json`  
**Total Examples:** 40,000  
**Total Size:** 76.68 MB  

## 📊 Overview

| Metric | Value |
|--------|-------|
| Total Examples | 40,000 |
| Total Size | 76.68 MB |
| Average Size | 2010 chars |
| Median Size | 982 chars |

## 🎯 Task Distribution

```

Task Types
==================================================
generation           [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                        ] 21,407 ( 53.8%)
correction           [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                           ] 18,372 ( 46.2%)
==================================================
TOTAL                                                                   39,779 (100.0%)
```

### Task Breakdown

| Task Type | Count | Percentage |
|-----------|-------|------------|
| **Generation** | 21,407 | 53.5% |
| **Correction** | 18,372 | 45.9% |

## 📋 Format Distribution

```
json_schema               ████████████████████████████████████████   10,919 ( 27.3%)
data_extraction           ████████████████████████████████████    9,938 ( 24.9%)
openapi_schema            ███████████████████████████████████    9,705 ( 24.3%)
cloudevents               █████████████████    4,741 ( 11.9%)
openapi_response          ██████████    2,915 (  7.3%)
openapi_request           ██████    1,710 (  4.3%)
```

### Format Breakdown

| Format | Count | Percentage | Description |
|--------|-------|------------|-------------|
| `json_schema` | 10,919 | 27.3% | JSON Schema compliant objects |
| `data_extraction` | 9,938 | 24.8% | Complex structured data extraction from documents |
| `openapi_schema` | 9,705 | 24.3% | Complete OpenAPI schema definitions |
| `cloudevents` | 4,741 | 11.9% | CNCF CloudEvents specification format |
| `openapi_response` | 2,915 | 7.3% | API response body examples |
| `openapi_request` | 1,710 | 4.3% | API request body examples |

## 🔧 Error Types (Correction Tasks)

```
type_mismatch        ██████████████████████████████    4,784 ( 26.0%)
extra_field          █████████████████████████████    4,762 ( 25.9%)
syntax_error         ███████████████████████████    4,438 ( 24.2%)
missing_field        ███████████████████████████    4,316 ( 23.5%)
missing_comma_array         16 (  0.1%)
missing_comma_properties        16 (  0.1%)
trailing_comma              12 (  0.1%)
unquoted_keys               12 (  0.1%)
multiple_errors              8 (  0.0%)
single_quotes                8 (  0.0%)
```

### Error Type Details

| Error Type | Count | Description |
|------------|-------|-------------|
| `type_mismatch` | 4,784 | Value type doesn't match schema |
| `extra_field` | 4,762 | Unknown/unexpected fields in JSON |
| `syntax_error` | 4,438 | Invalid JSON syntax (commas, quotes, etc) |
| `missing_field` | 4,316 | Required field is absent |
| `missing_comma_array` | 16 | - |
| `missing_comma_properties` | 16 | - |
| `trailing_comma` | 12 | - |
| `unquoted_keys` | 12 | - |
| `multiple_errors` | 8 | - |
| `single_quotes` | 8 | - |

## 📏 Size Statistics

### Example Size Distribution (characters)

| Percentile | Size | Visualization |
|------------|------|---------------|
| **Min** |      166 | `` |
| **P25** |      460 | `` |
| **Median** |      982 | `` |
| **Mean** |    2,010 | `` |
| **P75** |    2,284 | `` |
| **P90** |    3,482 | `` |
| **P95** |    4,296 | `` |
| **Max** | 4,030,131 | `▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓` |

### JSON Output Size (characters)

| Metric | Size |
|--------|------|
| Min | 17 |
| Median | 373 |
| Mean | 1,222 |
| Max | 109,126 |

## 🔍 Schema Presence

| Type | Count | Percentage | Bar |
|------|-------|------------|-----|
| With Schema | 6,043 | 15.1% | `███████` |
| Without Schema | 33,957 | 84.9% | `██████████████████████████████████████████` |

## ✅ Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| JSON Validity | 100% | ✅ All examples valid |
| ChatML Format | 100% | ✅ All properly formatted |
| Deduplication | Applied | ✅ SHA-256 hashing |
| Size Filtering | Applied | ✅ Min 50 chars |
| Task Balance | 20.2% deviation | ⚠️ From 33/33/33 target |

## 📚 Data Sources

| Source | Type | Examples | Quality |
|--------|------|----------|---------|
| **APIs.guru** | OpenAPI specifications | Real-world API schemas | ⭐⭐⭐⭐ |
| **SchemaStore** | JSON Schemas | Configuration files | ⭐⭐⭐⭐⭐ |
| **CloudEvents** | Event format | CNCF standard events | ⭐⭐⭐⭐⭐ |
| **Paraloq** | Text→JSON extraction | Medical, business docs | ⭐⭐⭐⭐⭐ |
| **MasterControl** | Document extraction | Complex structured data | ⭐⭐⭐⭐⭐ |
| **Generated Negatives** | Invalid JSON | Error correction training | ⭐⭐⭐⭐ |

## 🎯 Supported Use Cases

1. **JSON Generation** (60.5%)
   - OpenAPI request/response generation
   - JSON Schema compliant object creation
   - CloudEvents event formatting
   - Configuration file generation

2. **JSON Correction** (39.5%)
   - Fix missing required fields
   - Correct type mismatches
   - Repair syntax errors
   - Remove extra/unknown fields

## 💡 Training Recommendations

- **Batch Size:** 2 (memory constrained)
- **Gradient Accumulation:** 45 (effective batch: 90)
- **Learning Rate:** 5e-5
- **Epochs:** 1.5
- **Adapter:** DoRA r=14
- **Temperature:** 0.7 (inference)
- **Grammar:** JSON GBNF enabled
