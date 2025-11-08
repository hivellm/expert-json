param(
    [string]$Expert = "expert-json",
    [string]$ProjectRoot = "F:\Node\hivellm\expert",
    [string]$BaseModel = "F:\Node\hivellm\expert\models\Qwen3-0.6B",
    [int]$MaxTokens = 400
)

$cli = Join-Path $ProjectRoot "cli\target\release\expert-cli.exe"

if (-not (Test-Path $cli)) {
    Write-Error "expert-cli.exe not found at $cli"
    exit 1
}

function Invoke-Test {
    param(
        [string]$Title,
        [string]$Prompt,
        [int]$Tokens = $MaxTokens
    )

    Write-Host "===== $Title ====="
    & $cli chat `
        --project-root $ProjectRoot `
        --experts $Expert `
        --base-model $BaseModel `
        --max-tokens $Tokens `
        --prompt $Prompt
    Write-Host ""
}

Invoke-Test "Schema generation (draft-07)" @'
Generate a JSON Schema (draft-07) for an object with fields "productId" (string), "price" (number, minimum 0), and optional "tags" (array of strings). Respond only with the JSON schema.
'@

Invoke-Test "Flat to nested transform" @'
Transform the flat JSON {"user_id": "123", "profile_name": "Alice", "profile_age": 34} into the nested structure {"user": {"id": "...", "profile": {"name": "...", "age": ...}}}. Respond only with the transformed JSON.
'@

Invoke-Test "Array handling (todos)" @'
Return an array of exactly three todo objects sorted by priority descending. Each object must have "title" (string) and "priority" (integer). Respond only with the JSON array.
'@

Invoke-Test "Item count accuracy (hex strings)" @'
Produce a JSON array with exactly 3 random hex strings of length 6. No additional fields. Respond only with the JSON array.
'@

Invoke-Test "Numeric aggregation" @'
Given the order totals [120.5, 50, 30], return {"total": <sum>, "average": <mean>} with numeric values only (no expressions). Respond only with the JSON object.
'@

