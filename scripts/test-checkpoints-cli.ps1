#!/usr/bin/env pwsh
# Quick checkpoint test using Rust CLI

$ErrorActionPreference = "Stop"

$CLI = "..\..\cli\target\release\expert-cli.exe"
$CHECKPOINTS = @("Base", "64", "96", "250", "final")

$TESTS = @(
    @{Name="Simple Object"; Prompt='Create JSON for person: name "John", age 30'},
    @{Name="Nested Object"; Prompt="Create JSON with user.profile.name structure"},
    @{Name="Array"; Prompt="Create JSON array with 3 products"},
    @{Name="Schema"; Prompt="Create JSON schema for blog post with title and tags"},
    @{Name="Repair"; Prompt='Fix JSON: {"name": "John" "age": 30}'}
)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "JSON EXPERT CHECKPOINT ANALYSIS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

foreach ($checkpoint in $CHECKPOINTS) {
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Yellow
    Write-Host "CHECKPOINT: $checkpoint" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Yellow
    
    foreach ($test in $TESTS) {
        Write-Host "`n  Test: $($test.Name)" -ForegroundColor Cyan
        Write-Host "  Prompt: $($test.Prompt)" -ForegroundColor Gray
        
        if ($checkpoint -eq "Base") {
            $output = & $CLI chat --prompt $test.Prompt --max-tokens 80 --device cuda --temperature 0.1 2>&1 | Out-String
        } else {
            # TODO: Implement adapter loading in CLI
            Write-Host "  [SKIP] Adapter loading not yet implemented in CLI" -ForegroundColor Yellow
            continue
        }
        
        Write-Host "  Output: $($output.Trim().Substring(0, [Math]::Min(100, $output.Trim().Length)))..." -ForegroundColor White
    }
    
    Write-Host ""
}

