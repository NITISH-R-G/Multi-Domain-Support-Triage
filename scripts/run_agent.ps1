# Run the triage agent from any cwd. Repository root = parent of scripts/.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$MainPy = Join-Path $RepoRoot "code\main.py"
if (-not (Test-Path $MainPy)) {
    Write-Error "Could not find code\main.py under $RepoRoot"
    exit 1
}
& python $MainPy @args
exit $LASTEXITCODE
