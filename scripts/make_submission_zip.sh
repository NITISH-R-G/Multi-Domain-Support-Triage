#!/usr/bin/env bash
# Build a submission ZIP from tracked git files only (no .git folder, no untracked junk).
# Output: ../$(basename "$(pwd)")-submission.zip  next to the repo root folder by default.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
OUT="${1:-$(dirname "$ROOT")/$(basename "$ROOT")-submission.zip}"
cd "$ROOT"
git archive --format=zip -o "$OUT" HEAD
echo "Wrote $OUT"
