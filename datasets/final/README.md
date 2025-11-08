# Expert-JSON Final Dataset

**Version:** 1.0  
**Created:** 2025-11-06  
**Total Examples:** 37,937  
**Format:** ChatML (JSONL)

## 📊 Dataset Splits

| Split | Examples | Percentage | File |
|-------|----------|------------|------|
| **Train** | 34,145 | 90.0% | `train.jsonl` |
| **Validation** | 1,896 | 5.0% | `validation.jsonl` |
| **Test** | 1,896 | 5.0% | `test.jsonl` |

### Task Distribution (Consistent Across Splits)

All splits maintain the same task distribution through stratified sampling:

- **Generation Tasks:** ~60.5%
- **Correction Tasks:** ~39.5%

## 📁 Files

### train.jsonl
**34,145 examples** for training the model.

**Stats:**
- Avg size: 1,471 characters
- Median: 861 characters
- Task balance: 60.5% generation, 39.5% correction

**Usage:**
```python
# Load training data
with open('train.jsonl', 'r') as f:
    for line in f:
        example = json.loads(line)
        text = example['text']  # ChatML formatted
```

### validation.jsonl
**1,896 examples** for hyperparameter tuning and early stopping.

**Stats:**
- Avg size: 1,351 characters
- Median: 820 characters
- Task balance: 60.4% generation, 39.6% correction

**Usage:**
- Monitor validation loss during training
- Tune learning rate, batch size, epochs
- Select best checkpoint

### test.jsonl
**1,896 examples** for final evaluation (DO NOT USE DURING TRAINING).

**Stats:**
- Avg size: 1,451 characters
- Median: 872 characters
- Task balance: 60.4% generation, 39.6% correction

**Usage:**
- Final model evaluation only
- Report metrics on test set
- Compare model versions

### metadata.json
Contains dataset split information and statistics.

```json
{
  "total_examples": 37937,
  "splits": {
    "train": { "count": 34145, "percentage": 90.0 },
    "validation": { "count": 1896, "percentage": 5.0 },
    "test": { "count": 1896, "percentage": 5.0 }
  },
  "split_strategy": "stratified by task type",
  "random_seed": 42
}
```

## 🎯 Task Types

### Generation Tasks (~60.5%)

Generate valid JSON from prompts, schemas, or descriptions.

**Formats:**
- **OpenAPI** (33%): API schemas, requests, responses
- **JSON Schema** (17%): Configuration files
- **CloudEvents** (20%): Event-driven architecture
- **Data Extraction** (28%): Document → JSON

**Example:**
```
<|system|>
Task: json_generation
Format: json_schema
<|end|>
<|user|>
Generate a valid JSON object matching the package.json schema
<|end|>
<|assistant|>
{"name": "my-package", "version": "1.0.0", ...}
<|end|>
```

### Correction Tasks (~39.5%)

Fix invalid JSON with various error types.

**Error Types (balanced ~25% each):**
- **Extra Field:** Unknown/unexpected properties
- **Type Mismatch:** Wrong data types
- **Syntax Error:** Invalid JSON syntax
- **Missing Field:** Required fields absent

**Example:**
```
<|system|>
Task: json_correction
Format: cloudevents
Error type: extra_field
<|end|>
<|user|>
Fix this invalid JSON:
{"id": "123", "unknownField": "value", ...}
<|end|>
<|assistant|>
{"id": "123", ...}
<|end|>
```

## 🔧 Data Format

All examples use **ChatML** format:

```
<|system|>
[System prompt with task info and schema]
<|end|>
<|user|>
[User request]
<|end|>
<|assistant|>
[JSON output]
<|end|>
```

### Field Structure

```json
{
  "text": "<|system|>\n...\n<|end|>\n<|user|>\n...\n<|end|>\n<|assistant|>\n...\n<|end|>"
}
```

## 📏 Size Statistics

| Metric | Train | Validation | Test |
|--------|-------|------------|------|
| **Avg Size** | 1,471 | 1,351 | 1,451 |
| **Median** | 861 | 820 | 872 |

Most examples are compact (median ~850 chars), suitable for efficient training.

## ✅ Quality Metrics

- ✅ **JSON Validity:** 100% - All examples contain valid JSON
- ✅ **ChatML Format:** 100% - All properly formatted
- ✅ **Deduplication:** SHA-256 hashing applied (162,557 duplicates removed)
- ✅ **Size Filtering:** Minimum 50 characters
- ✅ **Task Balance:** Stratified splits maintain distribution
- ✅ **Reproducible:** Random seed 42 for consistent splits

## 🚀 Training Configuration

### Recommended Hyperparameters

```python
{
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "adapter": "dora",
    "r": 14,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj"],
    "batch_size": 2,
    "gradient_accumulation_steps": 45,  # effective batch: 90
    "learning_rate": 5e-5,
    "warmup_ratio": 0.1,
    "epochs": 1.5,
    "lr_scheduler": "cosine",
    "bf16": true,
    "max_length": 2048
}
```

### Expected Training Time

- **Hardware:** RTX 4090 (24GB VRAM)
- **Time:** ~3-4 hours for 1.5 epochs
- **VRAM:** ~6-8GB with Unsloth optimization

## 📚 Data Sources

Dataset compiled from 6 high-quality sources:

| Source | Examples | Quality | Description |
|--------|----------|---------|-------------|
| **MasterControl** | 10,000 | ⭐⭐⭐⭐⭐ | Complex document extraction |
| **Paraloq** | 484 | ⭐⭐⭐⭐⭐ | Medical/business text→JSON |
| **CloudEvents** | 5,000 | ⭐⭐⭐⭐⭐ | CNCF event format |
| **SchemaStore** | 3,213 | ⭐⭐⭐⭐⭐ | Configuration schemas |
| **APIs.guru** | 4,240 | ⭐⭐⭐⭐ | OpenAPI specifications |
| **Generated Negatives** | 15,000 | ⭐⭐⭐⭐ | Error correction examples |

## 🎯 Use Cases

### Supported Scenarios

1. **API Development**
   - Generate OpenAPI request/response bodies
   - Create API schema definitions
   - Validate API payloads

2. **Configuration Management**
   - Generate package.json, tsconfig.json
   - Create ESLint, Prettier configs
   - Validate configuration files

3. **Event-Driven Systems**
   - Generate CloudEvents format
   - Create event payloads
   - Validate event schemas

4. **Data Extraction**
   - Extract structured data from documents
   - Parse medical records, invoices, contracts
   - Transform unstructured text to JSON

5. **JSON Correction**
   - Fix syntax errors
   - Add missing fields
   - Remove invalid fields
   - Correct type mismatches

## 📖 Loading the Dataset

### Python (with Hugging Face datasets)

```python
from datasets import load_dataset

# Load from local files
dataset = load_dataset('json', data_files={
    'train': 'train.jsonl',
    'validation': 'validation.jsonl',
    'test': 'test.jsonl'
})

# Access splits
train_data = dataset['train']
val_data = dataset['validation']
test_data = dataset['test']
```

### Python (manual loading)

```python
import json

def load_jsonl(path):
    examples = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))
    return examples

train = load_jsonl('train.jsonl')
val = load_jsonl('validation.jsonl')
test = load_jsonl('test.jsonl')
```

### With Unsloth

```python
from unsloth import FastLanguageModel
from datasets import load_dataset

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-0.5B-Instruct",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=False,
)

# Load dataset
dataset = load_dataset('json', data_files={
    'train': 'datasets/final/train.jsonl',
    'validation': 'datasets/final/validation.jsonl'
})

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation'],
    dataset_text_field='text',
    max_seq_length=2048,
    ...
)
```

## 🔍 Dataset Validation

### Quick Checks

```bash
# Count examples
wc -l *.jsonl

# Check first example
head -n 1 train.jsonl | jq -r '.text'

# Validate JSON format
jq empty train.jsonl
jq empty validation.jsonl
jq empty test.jsonl
```

### Python Validation

```python
import json

def validate_split(path):
    with open(path, 'r') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            assert 'text' in data, f"Line {i}: missing 'text'"
            assert '<|system|>' in data['text'], f"Line {i}: invalid ChatML"
            assert '<|user|>' in data['text'], f"Line {i}: invalid ChatML"
            assert '<|assistant|>' in data['text'], f"Line {i}: invalid ChatML"
    print(f"✓ {path} validated")

validate_split('train.jsonl')
validate_split('validation.jsonl')
validate_split('test.jsonl')
```

## 📊 Additional Documentation

- **[../docs/DATASET_DISTRIBUTION.md](../docs/DATASET_DISTRIBUTION.md)** - Statistical analysis
- **[../docs/DATASET_QUALITY_REPORT.md](../docs/DATASET_QUALITY_REPORT.md)** - Quality validation
- **[../docs/README.md](../docs/README.md)** - Documentation overview
- **[../README.md](../README.md)** - Main expert-json guide

## 🐛 Known Issues

None. Dataset has been validated and is production-ready.

## 📝 License

Same as parent project (see [../LICENSE](../LICENSE)).

## 🤝 Contributing

To update the dataset:

1. Modify raw data sources in `../datasets/raw/`
2. Run `python3 ../preprocess.py`
3. Run `python3 ../create_final_dataset.py`
4. Update documentation with `python3 ../scripts/analyze_dataset.py`

## 📧 Support

For issues or questions:
- Open an issue in the repository
- Check documentation in `../docs/`
- Review training examples in `../README.md`

---

**Dataset Version:** 1.0  
**Last Updated:** 2025-11-06  
**Maintainer:** HiveLLM Team  
**Ready for Training:** ✅ YES

