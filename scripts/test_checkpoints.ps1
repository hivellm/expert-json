#!/usr/bin/env pwsh
# Test all JSON expert checkpoints

$ErrorActionPreference = "Stop"

Write-Host "Activating venv_windows..." -ForegroundColor Cyan
& ..\..\..\cli\venv_windows\Scripts\Activate.ps1

Write-Host "Running checkpoint analysis..." -ForegroundColor Cyan
python test_checkpoints.py

Write-Host "`nDone! Check ../checkpoint_analysis_json.json for results" -ForegroundColor Green

