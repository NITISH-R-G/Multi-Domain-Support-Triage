#!/usr/bin/env bash
# Run the triage agent from any cwd. Repository root = parent of this script's directory.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python "$ROOT/code/main.py" "$@"
