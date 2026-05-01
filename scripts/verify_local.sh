#!/usr/bin/env bash
# Same checks as CI + full offline batch. Optional: VERIFY_SKIP_FULL_BATCH=1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== install deps =="
python -m pip install -q -r code/requirements.txt

echo "== CLI --help =="
(cd "$ROOT/code" && python main.py --help >/dev/null)

echo "== pytest =="
(cd "$ROOT/code" && python -m pytest tests -q)

echo "== sample regression (offline) =="
(cd "$ROOT/code" && ORCHESTRATE_DISABLE_LLM=1 python run_eval.py --offline)

if [[ "${VERIFY_SKIP_FULL_BATCH:-}" == "1" ]]; then
  echo "VERIFY_SKIP_FULL_BATCH=1: skipping full main.py run."
  exit 0
fi

echo "== full batch main.py (offline, all rows) =="
(cd "$ROOT/code" && ORCHESTRATE_DISABLE_LLM=1 python main.py --limit 0)

echo "All verification steps passed."
