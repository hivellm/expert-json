# Changelog - Expert JSON

## [0.4.1] - 2025-11-08 (Investigative checkpoint-250 package)

### Changed

- Updated manifest to ship `weights/qwen3-06b/checkpoint-250` (version 0.4.1) for focused transformation/arithmetic testing.
- Refreshed README with the investigative scope, targeted findings (flat→nested rewrites and numeric stability), and remaining schema/array limitations.
- Enhanced `scripts/eval_checkpoint_250_tests.py`:
  - stricter prompts (`$schema`, JSON-only answers);
  - higher token allowance and removal of deprecated `torch_dtype` usage.

### Notes

- Targeted probes (6 cases) confirmed successes in `transform_flat_to_nested` and numeric aggregation (`math_expression`), while schema outputs still return examples and array formatting may omit brackets.
- Release 0.4.1 is an investigative snapshot around checkpoint-250; it does not replace the production-focused 0.4.0 package.

## [0.4.0] - 2025-01-XX (Dataset Rebalancing & Focus on Known Issues)

### Changed

**Dataset Rebalancing**
- Reduced dataset from 737,228 to 40,000 examples (94.6% reduction)
- Generic format limited to 70% (28,000 examples)
- Other formats reduced to 30% (12,000 examples) focusing on known issues
- Increased The Stack collection limit from 10k to 50k to support generic ratio

**Focus on Known Issues**
- Prioritized formats addressing v0.4.0 limitations:
  - Schema generation (json_schema, openapi_schema): 3,374 examples (8.4%)
  - Transformations (data_extraction): 3,299 examples (8.2%)
  - Array handling (openapi_response): 392 examples (1.0%)
  - Type conversion (openapi_request): 161 examples (0.4%)
- Maintained diverse format coverage while reducing total size

**Distribution Charts**
- Added `scripts/generate_distribution_charts.py` for dataset visualization
- Generated distribution charts (format, task, complexity) saved to `docs/`
- Charts available in PNG (300 DPI) and PDF formats

**Dataset Statistics (v0.5.0)**
- Total: 40,000 examples
- Generic: 28,000 (70.0%)
- Priority formats: 12,000 (30.0%)
- Generation tasks: 35,222 (88.1%)
- Correction tasks: 4,778 (11.9%)

**Manifest Updated**
- Version: 0.4.0 → 0.5.0
- Description updated to reflect rebalanced dataset
- Dataset size updated in metadata

### Notes

- Dataset significantly reduced to focus training on quality over quantity
- Generic format maintained at 70% to ensure general JSON generation capability
- Priority formats selected to address specific weaknesses from v0.4.0
- Ready for retraining with focused dataset

### Status

**Dataset**: Ready for training (40,000 examples, 70% generic)  
**Focus**: Addressing schema vs example confusion, transformations, array handling  
**Next Steps**: Retrain model with rebalanced dataset

## [0.4.0] - 2025-11-07 (The Stack Massive Expansion)

### Added

**The Stack Dataset Integration Complete**
- Successfully collected and integrated 698,988 JSON examples from The Stack
- Dataset expanded from 38,240 to 737,228 examples (19x increase)
- Real-world JSON patterns from production codebases

### Changed

**Massive Dataset Expansion**
- Total examples: 38,240 → 737,228 (+698,988 from The Stack)
- The Stack now represents ~95% of training dataset
- Enhanced diversity with real-world codebase examples
- Preprocessing completed successfully with deduplication

**Dataset Statistics (v0.4.0)**
- Total processed: 737,228 examples
- Duplicates removed: 159,026
- The Stack: 698,988 examples (94.8% of dataset)
- All other sources: 38,240 examples (5.2% of dataset)

**Manifest Updated**
- Version: 0.3.0 → 0.4.0
- Description updated to reflect The Stack integration
- Dataset size updated in metadata

### Notes

- The Stack collection completed successfully
- Preprocessing integrated all examples with ChatML formatting
- Dataset ready for training with expanded coverage
- Expected improvements in handling diverse JSON patterns from real codebases

### Status

**Dataset**: Ready for training (737,228 examples)  
**The Stack**: Fully integrated (698,988 examples)  
**Next Steps**: Train new model with expanded dataset

## [0.3.1] - 2025-11-07 (The Stack Dataset Integration)

### Added

**The Stack Dataset Collection**
- Added `scripts/collect_the_stack_json.py` to collect JSON examples from bigcode/the-stack
- Extracts valid JSON objects/arrays from The Stack codebase
- Includes both generation and correction examples
- Integrated into `preprocess.py` for automatic inclusion

**Collection Scripts**
- `scripts/collect_the_stack_json.py` - Main collection script with HuggingFace authentication
- `scripts/run_the_stack_collection.ps1` - PowerShell wrapper for easy execution
- Supports `--limit` and `--max-check` parameters to control collection scope

### Changed

**Dataset Expansion**
- Added The Stack as new data source in `preprocess.py`
- Output path: `datasets/raw/the_stack_json/the_stack_json.jsonl`
- Examples formatted in ChatML for consistency with existing dataset

**Collection Process**
- Script checks up to 20x limit to find JSON files (prevents checking millions of files)
- Extracts both valid JSON (for generation) and invalid JSON (for correction training)
- Deduplication based on content hash to avoid duplicates

### Notes

- Requires HuggingFace token (set via `HF_TOKEN` environment variable)
- Dataset terms must be accepted at https://huggingface.co/datasets/bigcode/the-stack
- Collection can be time-consuming depending on limit (default: 50k files with JSON)

## [0.3.0] - 2025-11-07 (Checkpoint Selection & Package Release)

### Added

**Comprehensive Checkpoint Analysis**
- Tested 5 checkpoints (base, 250, 500, 638, final) with 15 complex test cases
- Identified Checkpoint-500 as best performing (40% score)
- Analysis documented in `logs/checkpoint_analysis.md`

**Checkpoint Comparison Results:**
- Base: 3/15 (20%) - Repetitions, truncations, wrong outputs
- Checkpoint-250: 5/15 (33%) - Loops, schema confusion
- **Checkpoint-500: 6/15 (40%)** - Best balance, selected for package
- Checkpoint-638: 6/15 (40%) - Similar to 500 but trailing comma issues
- Final: 5/15 (33%) - Loops, regression issues

**Package Generation**
- Updated manifest.json to use checkpoint-500
- Package ready for distribution

### Changed

**Manifest Updated**
- Adapter path: `weights/qwen3-06b/final` → `weights/qwen3-06b/checkpoint-500`
- Added checkpoint selection rationale in adapter comment

**Performance Metrics (Checkpoint-500)**
- Schema generation: ✅ Nested schemas correct, validation rules correct
- JSON repair: ✅ Trailing commas, single quotes, unquoted keys fixed correctly
- Output control: ✅ No infinite loops, consistent outputs
- Limitations: ⚠️ Still returns examples instead of schemas in some cases, cannot transform flat to nested JSON

### Known Limitations (v0.3.0)

**Identified Issues:**
1. Schema vs Example confusion: Returns examples when schemas requested (tests 3, 7, 10, 12, 15)
2. JSON transformation: Cannot transform flat JSON to nested structure (test 8)
3. Array repair: Returns object instead of array in one case (test 5)
4. Item count: Returns 5 items when 3 requested (test 14)
5. Math expressions: Inserts math expressions in JSON values (test 12)

**Recommendations for Future Versions:**
- Add post-processing validation to detect schema vs example
- Enhance transformation capabilities
- Improve array handling
- Remove math expressions from JSON values

### Status

**Package**: Ready for release (checkpoint-500)  
**Quality Score**: 40% (6/15 tests passed)  
**Best Use Cases**: JSON schema generation, JSON repair, nested structures  
**Next Steps**: Consider additional training or post-processing to address limitations

## [0.2.0] - 2025-11-06 (Enhanced Dataset)

### Added

**Qualitative Analysis Completed**
- Tested Base Model vs Final Checkpoint v0.1.0
- Identified critical weaknesses:
  - Schema generation: 3/10 (generates examples instead of schemas)
  - JSON repair: 7/10 (doesn't fix missing commas)
- Overall score: 7.25/10 (+383% vs base 1.5/10)

**Microsoft Production Schemas (183 REAL schemas)**
- Source: https://github.com/microsoft/json-schemas (MIT License)
- Products: Microsoft Fabric, Office-JS, Teams Toolkit, Copilot, Rush, API-Extractor
- Extracted 183 valid schemas from 403 files
- Quality: Real production JSON Schemas (not synthetic)
- Impact: Fixes critical schema generation weakness

**Synthetic Schema Templates (48 examples)**
- Simple objects, nested structures, arrays
- API responses, pagination, e-commerce entities
- 12 base templates × 4 prompt variations
- Comprehensive coverage of common patterns

**Enhanced JSON Repair Dataset (72 examples)**
- Missing commas between properties: 16 examples
- Missing commas in arrays: 16 examples
- Trailing commas: 12 examples
- Unquoted keys: 12 examples
- Single quotes instead of double: 8 examples
- Multiple errors combined: 8 examples
- Impact: Fixes JSON repair conservatism

**Data Generation Scripts**
- `scripts/extract_microsoft_schemas.py` - Extract real schemas from Microsoft repo
- `scripts/generate_schema_dataset.py` - Generate synthetic schema templates
- `scripts/generate_repair_dataset.py` - Generate syntax error patterns
- `scripts/normalize_to_chatml.py` - Convert to HuggingFace ChatML format
- `scripts/create_enhanced_dataset.py` - Combine all sources

**Testing Scripts**
- `scripts/test_simple.py` - Quick Base vs Final comparison (3 tests)
- `scripts/test_checkpoints.py` - Comprehensive analysis (15 tests × 5 checkpoints)
- `tests/ENHANCEMENT_REPORT.md` - Detailed analysis documentation

### Changed

**Dataset Enhanced (37,937 → 38,240 examples)**
- Base dataset: 37,937 examples (APIs.guru, SchemaStore, CloudEvents, Paraloq, MasterControl, negatives)
- Microsoft schemas: +183 (real production quality)
- Synthetic schemas: +48
- JSON repair: +72
- **Total: 38,240 examples (+303, +0.8%)**

**Dataset Distribution:**
- APIs.guru: 4,240 (11.1%)
- SchemaStore: 3,213 (8.4%)
- CloudEvents: 5,000 (13.1%)
- Paraloq: 484 (1.3%)
- MasterControl: 10,000 (26.1%)
- Corrections: 15,000 (39.2%)
- Microsoft schemas: 183 (0.5%)
- Synthetic schemas: 48 (0.1%)
- Repair enhanced: 72 (0.2%)

**Task Balance:**
- Generation: 12,453 (32.6%)
- Extraction: 10,484 (27.4%)
- Correction: 15,000 (39.2%)
- Schema generation: 231 (0.6%) - critical enhancement

**preprocess.py Updated**
- Integrated Microsoft schemas automatically
- Integrated synthetic schemas
- Integrated repair enhanced patterns
- Updated statistics tracking
- All new sources processed with existing workflow

**Manifest v0.2.0**
- Version: 0.1.0 → 0.2.0
- Dataset: 37,937 → 38,240 examples
- Source: Added microsoft/json-schemas
- Description: Updated with schema generation and advanced repair capabilities

**README.md Enhanced**
- Added Qualitative Analysis section (v0.1.0 test results)
- Added Problems Identified section (schema + repair weaknesses)
- Added Enhancement Solution section (303 targeted examples)
- Updated Dataset section (9 sources, detailed breakdown)
- Updated Credits with all data sources

**LICENSE Updated**
- Added Microsoft JSON Schemas citation
- Source, license, and usage documented
- MIT license compatible with CC-BY-4.0

### Expected Improvements (v0.2.0 target)

| Capability | v0.1.0 | Target v0.2.0 | Enhancement |
|------------|--------|---------------|-------------|
| Simple JSON | 10/10 ✅ | 10/10 | Maintained |
| **Schema Generation** | 3/10 ❌ | **8+/10** | +183 REAL Microsoft schemas |
| **JSON Repair** | 7/10 ⚠️ | **9+/10** | +72 explicit fix patterns |
| **Overall** | **7.25/10** | **9.0+/10** | **+24% improvement target** |

### Status

**Training**: In progress with enhanced dataset (38,240 examples)  
**Validation**: Using separate validation.jsonl (3,824 examples)  
**Test**: Using separate test.jsonl (3,824 examples)  
**Expected completion**: 2-3 hours

## [0.1.0] - 2025-11-05 (Initial Training)

### Added

- Initial expert structure created
- Dataset collection from 6 sources (APIs.guru, SchemaStore, CloudEvents, Paraloq, MasterControl, negatives)
- DoRA r=14 adapter configuration
- Unsloth integration for 2x faster training
- Windows optimization with memory safety
- ChatML formatting for Qwen3 native support

### Training Configuration

- Base Model: Qwen3-0.6B (INT4 quantized)
- Adapter: DoRA r=14, alpha=28
- Target modules: q_proj, k_proj, v_proj, o_proj, up_proj, down_proj
- Batch size: 2 × 45 gradient accumulation = 90 effective
- Learning rate: 5e-5 with cosine scheduler
- Epochs: 1.5
- Dataset: 37,937 examples

### Results (v0.1.0)

**Checkpoint final:**
- Overall quality: 7.25/10 (+383% vs base 1.5/10)
- Strengths: Simple JSON generation (10/10)
- Weaknesses: Schema generation (3/10), JSON repair (7/10)
- Identified need for enhancement with targeted datasets

---

## References

- Microsoft JSON Schemas: https://github.com/microsoft/json-schemas
- APIs.guru: https://api.apis.guru/
- SchemaStore: https://www.schemastore.org/
- CloudEvents: https://cloudevents.io/
- Paraloq: https://huggingface.co/datasets/paraloq/json_data_extraction
- MasterControl: https://huggingface.co/datasets/MasterControlAIML/JSON-Unstructured-Structured

