#!/usr/bin/env bash

set -euo pipefail

CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/cli"
EXPERT_CMD="$CLI_DIR/target/release/expert-cli.exe"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

run_test() {
  local title="$1"
  local prompt="$2"
  echo "===== ${title} ====="
  "$EXPERT_CMD" chat \
    --project-root "$PROJECT_ROOT" \
    --experts expert-json \
    --max-tokens 400 \
    --prompt "$prompt" || true
  echo
}

run_test "Schema generation (draft-07)" \
"Generate a JSON Schema (draft-07) for an object with fields \"productId\" (string), \"price\" (number, minimum 0), and optional \"tags\" (array of strings). Respond only with the JSON schema."

run_test "Flat to nested transform" \
"Transform the flat JSON {\"user_id\": \"123\", \"profile_name\": \"Alice\", \"profile_age\": 34} into the nested structure {\"user\": {\"id\": \"...\", \"profile\": {\"name\": \"...\", \"age\": ...}}}. Respond only with the transformed JSON."

run_test "Array handling (todos)" \
"Return an array of exactly three todo objects sorted by priority descending. Each object must have \"title\" (string) and \"priority\" (integer). Respond only with the JSON array."

run_test "Item count accuracy (hex strings)" \
"Produce a JSON array with exactly 3 random hex strings of length 6. No additional fields. Respond only with the JSON array."

run_test "Numeric aggregation" \
"Given the order totals [120.5, 50, 30], return {\"total\": <sum>, \"average\": <mean>} with numeric values only (no expressions). Respond only with the JSON object."


