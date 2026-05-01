# Run the same checks as GitHub CI plus a full offline batch (repo root = parent of scripts/).
# Usage (PowerShell): pwsh -File scripts/verify_local.ps1
# Optional: skip full CSV run with env VERIFY_SKIP_FULL_BATCH=1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "== install deps (requirements.txt) ==" -ForegroundColor Cyan
python -m pip install -q -r code/requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== CLI --help ==" -ForegroundColor Cyan
Set-Location "$RepoRoot\code"
python main.py --help | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== pytest ==" -ForegroundColor Cyan
python -m pytest tests -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== sample regression (offline) ==" -ForegroundColor Cyan
$env:ORCHESTRATE_DISABLE_LLM = "1"
python run_eval.py --offline
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($env:VERIFY_SKIP_FULL_BATCH -eq "1") {
    Write-Host "VERIFY_SKIP_FULL_BATCH=1: skipping full main.py run." -ForegroundColor Yellow
    exit 0
}

Write-Host "== full batch main.py (offline, all rows) ==" -ForegroundColor Cyan
python main.py --limit 0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "All verification steps passed." -ForegroundColor Green
