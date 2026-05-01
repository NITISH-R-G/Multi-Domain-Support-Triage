# Build submission ZIP from tracked git files only (see README "Packaging a ZIP").
# Usage: pwsh -File scripts/make_submission_zip.ps1 [optional-output-path.zip]
$ErrorActionPreference = "Stop"
$RepoRoot = git rev-parse --show-toplevel
if (-not $RepoRoot) { Write-Error "Not in a git repo"; exit 1 }
Set-Location $RepoRoot

$DefaultOut = Join-Path (Split-Path $RepoRoot -Parent) "$(Split-Path $RepoRoot -Leaf)-submission.zip"
$OutZip = if ($args.Count -ge 1) { $args[0] } else { $DefaultOut }

git archive --format=zip -o $OutZip HEAD
Write-Host "Wrote $OutZip"
