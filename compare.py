"""
Qualitative Checkpoint Comparison - Expert JSON

This script compares the base model, the latest training checkpoint,
and the previous production package (v0.3.0) for the expert-json project.
It mirrors the qualitative analysis workflow used by other experts.
"""

import json
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


# ============================================================================
# PATHS AND CONFIGURATION
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERT_DIR = Path(__file__).resolve().parent

BASE_MODEL_PATH = REPO_ROOT / "models" / "Qwen3-0.6B"
CHECKPOINT_DIR = EXPERT_DIR / "weights" / "qwen3-06b"
PACKAGE_PATH = EXPERT_DIR / "expert-json-qwen3-06b.v0.3.0.expert"
OUTPUT_PATH = EXPERT_DIR / "checkpoint_comparison_results.json"

GEN_CONFIG = {
    "max_new_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "do_sample": True,
}

SYSTEM_PROMPT = (
    "Dialect: json\n"
    "Task: Return strictly valid minified JSON.\n"
    "Constraints: No explanations, markdown, or trailing comments."
)

TEST_CASES: List[Dict[str, str]] = [
    {
        "id": "extract_name",
        "category": "field_extraction",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Given the payload:\n"
            "{\n  \"name\": \"Alice Smith\",\n  \"age\": 25,\n  \"city\": \"Seattle\"\n}\n"
            "Return only the name as {\"name\": <value>}."
        ),
        "expected_type": "json",
    },
    {
        "id": "extract_nested_email",
        "category": "nested_field",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Input JSON:\n"
            "{\n  \"user\": {\n    \"profile\": {\n      \"email\": \"test@example.com\",\n"
            "      \"role\": \"admin\"\n    }\n  }\n}\n"
            "Return the email field as {\"email\": \"...\"}. If missing, return {\"email\": null}."
        ),
        "expected_type": "json",
    },
    {
        "id": "count_tags",
        "category": "aggregation",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "How many elements are in the array under \"tags\"?\n"
            "{\n  \"tags\": [\"python\", \"rust\", \"javascript\", \"sql\"]\n}\n"
            "Respond as {\"count\": <number>}."
        ),
        "expected_type": "json",
    },
    {
        "id": "schema_generation",
        "category": "schema",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Generate a JSON Schema (draft-07) for an object with keys \"title\" (string), "
            "\"pages\" (integer, minimum 1), and optional \"tags\" (array of strings)."
        ),
        "expected_type": "json",
    },
    {
        "id": "repair_json",
        "category": "repair",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Fix the following invalid JSON and return the corrected version:\n"
            "{\"id\": 10, \"items\": [\"a\", \"b\",], \"status\": \"ok\", }"
        ),
        "expected_type": "json",
    },
    {
        "id": "group_totals",
        "category": "grouping",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Aggregate order totals by customer id.\n"
            "[\n  {\"customer_id\": 1, \"total\": 120.5},\n"
            "  {\"customer_id\": 2, \"total\": 50},\n"
            "  {\"customer_id\": 1, \"total\": 30}\n]\n"
            "Return {\"customers\": [{\"customer_id\": <id>, \"total\": <sum>}, ...]} sorted by customer_id."
        ),
        "expected_type": "json",
    },
    {
        "id": "date_span",
        "category": "temporal_reasoning",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Given events with ISO dates, return earliest and latest dates.\n"
            "[\n  {\"event\": \"launch\", \"date\": \"2024-02-10\"},\n"
            "  {\"event\": \"beta\", \"date\": \"2024-01-15\"},\n"
            "  {\"event\": \"ga\", \"date\": \"2024-03-01\"}\n]\n"
            "Respond as {\"earliest\": \"YYYY-MM-DD\", \"latest\": \"YYYY-MM-DD\"}."
        ),
        "expected_type": "json",
    },
    {
        "id": "validation_summary",
        "category": "validation",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": (
            "Validate the object {\"email\": \"not-an-email\", \"age\": 16} against rules:\n"
            "- email must contain \"@\"\n"
            "- age must be >= 18\n"
            "Return {\"valid\": <bool>, \"errors\": [<messages>]}."
        ),
        "expected_type": "json",
    },
]


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def detect_device() -> str:
    """Detect the best available device."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def print_separator(char: str = "=", width: int = 100) -> None:
    """Print a visual separator."""
    print(char * width)


def print_test_header(test_case: Dict[str, str], index: int, total: int) -> None:
    """Print a formatted test header."""
    print_separator()
    print(f"\nTEST {index}/{total}: {test_case['id']}")
    print(f"Category: {test_case.get('category', 'N/A')}")
    print(f"Expected type: {test_case.get('expected_type', 'N/A')}")
    print_separator("-")
    print("\n[SYSTEM PROMPT]")
    print(test_case["system_prompt"])
    print("\n[USER PROMPT]")
    print(test_case["user_prompt"])
    print_separator("-")


def print_output(label: str, output: str, max_length: int = 800) -> None:
    """Print model output with optional truncation."""
    print(f"\n[{label}]")
    if len(output) > max_length:
        print(output[:max_length])
        print(f"\n... (truncated, total: {len(output)} characters)")
    else:
        print(output)


def load_base_model(base_model_path: Path, device: str) -> AutoModelForCausalLM:
    """Load the base Qwen model onto the desired device."""
    kwargs = {
        "trust_remote_code": True,
        "torch_dtype": torch.bfloat16 if device == "cuda" else torch.float32,
    }
    if device == "cuda":
        kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(str(base_model_path), **kwargs)
    if device == "cpu":
        model = model.to(device)
    model.eval()
    return model


def generate_output(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    system_prompt: str,
    user_prompt: str,
    device: str,
) -> str:
    """Generate a response for the supplied prompts."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    chat_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer([chat_text], return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    gen_params = GEN_CONFIG.copy()
    gen_params["pad_token_id"] = tokenizer.eos_token_id
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_params)
    generated = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    return generated.strip()


def is_valid_json(text: str) -> bool:
    """Return True if text parses as JSON."""
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def extract_package(package_path: Path) -> Path:
    """Extract an .expert package into a temporary directory."""
    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")
    temp_dir = Path(tempfile.mkdtemp(prefix="expert_json_pkg_"))
    with tarfile.open(package_path, "r:gz") as tar:
        tar.extractall(temp_dir)
    return temp_dir


def find_adapter_dir(extracted_dir: Path) -> Path:
    """Locate adapter files inside an extracted package."""
    candidates = [
        extracted_dir,
        extracted_dir / "weights" / "adapter",
        extracted_dir / "adapter",
    ]
    for candidate in candidates:
        if (candidate / "adapter_model.safetensors").exists() and (
            candidate / "adapter_config.json"
        ).exists():
            return candidate
    raise FileNotFoundError("Adapter files not found in extracted package.")


def load_adapter_model(base_model_path: Path, adapter_dir: Path, device: str) -> AutoModelForCausalLM:
    """Load a PEFT adapter on top of a fresh base model."""
    model = load_base_model(base_model_path, device)
    model = PeftModel.from_pretrained(model, str(adapter_dir))
    model.eval()
    return model


# ============================================================================
# MAIN ROUTINE
# ============================================================================

def main() -> None:
    """Entry point."""
    if not BASE_MODEL_PATH.exists():
        raise FileNotFoundError(f"Base model not found: {BASE_MODEL_PATH}")
    if not CHECKPOINT_DIR.exists():
        raise FileNotFoundError(f"Checkpoint directory not found: {CHECKPOINT_DIR}")

    checkpoint_dirs = [
        path
        for path in CHECKPOINT_DIR.iterdir()
        if path.is_dir()
        and (
            path.name.startswith("checkpoint-")
            or path.name == "final"
        )
    ]
    if not checkpoint_dirs:
        raise RuntimeError(f"No checkpoints found under {CHECKPOINT_DIR}")

    device = detect_device()

    print_separator()
    print("QUALITATIVE CHECKPOINT COMPARISON - EXPERT JSON")
    print("Base vs All Checkpoints vs v0.3.0 Package")
    print_separator()
    print(f"Device: {device}")
    print(f"Base model: {BASE_MODEL_PATH}")
    print(f"Checkpoints discovered: {[path.name for path in checkpoint_dirs]}")
    print(f"Previous package: {PACKAGE_PATH}")
    print(f"Total tests: {len(TEST_CASES)}")
    print_separator()

    print("[1/4] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(str(BASE_MODEL_PATH), trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("[OK] Tokenizer loaded")

    print("[2/4] Loading base model...")
    base_model = load_base_model(BASE_MODEL_PATH, device)
    print("[OK] Base model ready")

    print("[3/4] Loading previous package (v0.3.0)...")
    package_tmp = extract_package(PACKAGE_PATH)
    try:
        adapter_dir = find_adapter_dir(package_tmp)
        previous_model = load_adapter_model(BASE_MODEL_PATH, adapter_dir, device)
        print("[OK] Previous package adapter ready")
    except Exception:
        shutil.rmtree(package_tmp, ignore_errors=True)
        raise

    total_tests = len(TEST_CASES)

    comparison_payload: Dict[str, object] = {
        "expert": "expert-json",
        "device": device,
        "base_model": str(BASE_MODEL_PATH),
        "previous_package": str(PACKAGE_PATH),
        "generation_config": GEN_CONFIG,
        "tests": [],
        "checkpoints_evaluated": [],
    }

    checkpoint_summaries: List[Dict[str, object]] = []

    def parse_step(name: str) -> int:
        if name == "final":
            return 999999
        return int(name.split("-")[1])

    checkpoint_dirs.sort(key=lambda path: parse_step(path.name))

    for checkpoint_dir in checkpoint_dirs:
        step = parse_step(checkpoint_dir.name)
        print_separator()
        print(f"Evaluating {checkpoint_dir.name} (step {step})")
        print_separator()

        checkpoint_model = load_adapter_model(BASE_MODEL_PATH, checkpoint_dir, device)

        checkpoint_results: List[Dict[str, object]] = []
        success_counts = {"base": 0, "checkpoint": 0, "previous": 0}

        for index, test_case in enumerate(TEST_CASES, start=1):
            print_test_header(test_case, index, total_tests)

            base_output = generate_output(
                base_model,
                tokenizer,
                test_case["system_prompt"],
                test_case["user_prompt"],
                device,
            )
            base_valid = is_valid_json(base_output)
            print_output("BASE MODEL", base_output)
            print(f"[BASE MODEL] valid_json={base_valid}")
            if base_valid:
                success_counts["base"] += 1

            checkpoint_output = generate_output(
                checkpoint_model,
                tokenizer,
                test_case["system_prompt"],
                test_case["user_prompt"],
                device,
            )
            checkpoint_valid = is_valid_json(checkpoint_output)
            print_output(checkpoint_dir.name.upper(), checkpoint_output)
            print(f"[{checkpoint_dir.name.upper()}] valid_json={checkpoint_valid}")
            if checkpoint_valid:
                success_counts["checkpoint"] += 1

            previous_output = generate_output(
                previous_model,
                tokenizer,
                test_case["system_prompt"],
                test_case["user_prompt"],
                device,
            )
            previous_valid = is_valid_json(previous_output)
            print_output("VERSION 0.3.0", previous_output)
            print(f"[VERSION 0.3.0] valid_json={previous_valid}")
            if previous_valid:
                success_counts["previous"] += 1

            checkpoint_results.append(
                {
                    "test_id": test_case.get("id", f"test_{index}"),
                    "category": test_case.get("category", "N/A"),
                    "expected_type": test_case.get("expected_type", "json"),
                    "outputs": {
                        "base": {"text": base_output, "valid_json": base_valid},
                        checkpoint_dir.name: {
                            "text": checkpoint_output,
                            "valid_json": checkpoint_valid,
                        },
                        "v0_3_0": {
                            "text": previous_output,
                            "valid_json": previous_valid,
                        },
                    },
                }
            )

            print_separator()

        checkpoint_summary = {
            "checkpoint": checkpoint_dir.name,
            "step": step,
            "valid_json": success_counts["checkpoint"],
            "total_tests": total_tests,
            "base_valid_json": success_counts["base"],
            "previous_valid_json": success_counts["previous"],
        }
        checkpoint_summaries.append(checkpoint_summary)
        comparison_payload["checkpoints_evaluated"].append(
            {
                "checkpoint": checkpoint_dir.name,
                "step": step,
                "results": checkpoint_results,
            }
        )

        print(
            f"Checkpoint {checkpoint_dir.name}: {success_counts['checkpoint']}/{total_tests} valid JSON outputs"
        )
        if torch.cuda.is_available():
            del checkpoint_model
            torch.cuda.empty_cache()

    best_checkpoint = (
        max(checkpoint_summaries, key=lambda entry: entry["valid_json"])
        if checkpoint_summaries
        else None
    )
    comparison_payload["summary"] = {
        "checkpoints": checkpoint_summaries,
        "best_checkpoint": best_checkpoint,
    }

    print_separator()
    print("\nEXECUTION SUMMARY")
    print_separator()
    print(f"Total tests executed per checkpoint: {total_tests}")
    print("Previous package: v0.3.0")
    for summary in checkpoint_summaries:
        ratio = summary["valid_json"] / summary["total_tests"]
        print(
            f"  - {summary['checkpoint']}: {summary['valid_json']}/{summary['total_tests']} valid JSON ({ratio:.0%})"
        )
    if best_checkpoint:
        print_separator()
        print(
            f"Best checkpoint: {best_checkpoint['checkpoint']} "
            f"({best_checkpoint['valid_json']}/{best_checkpoint['total_tests']} valid JSON)"
        )
        print_separator()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(comparison_payload, handle, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUTPUT_PATH}")

    shutil.rmtree(package_tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

