# Support triage agent (Orchestrate)

> **Evaluators:** primary **setup + approach overview** for the whole submission is the **repository root** [`../README.md`](../README.md). This file focuses on `code/` module details and flags.

Terminal agent that reads `support_tickets/support_tickets.csv`, retrieves grounded snippets from the offline `data/` corpus (**BM25 + TF‑IDF fusion + lexical rerank**), applies risk-based escalation rules + taxonomy mapping, and writes predictions to `support_tickets/output.csv`.

**Design rationale & decision flowchart:** [`../docs/decisions.md`](../docs/decisions.md). **Interview / demo / rubric:** [`../docs/interview.md`](../docs/interview.md), [`../docs/demo-script.md`](../docs/demo-script.md), [`../docs/DEV_EVAL.md`](../docs/DEV_EVAL.md).

## Setup

```bash
cd code
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

Copy the repo’s `.env.example` to the repository root as `.env` and set at least:

```env
OPENAI_API_KEY=sk-...
# optional:
# OPENAI_MODEL=gpt-4o-mini
# ORCHESTRATE_SEED=42
# TOP_K=6
# LOW_BM25_THRESHOLD=7.0
# ORCHESTRATE_DISABLE_LLM=1
# ORCHESTRATE_INDEX_VERSION=2
# HYBRID_CANDIDATES=160
# BM25_WEIGHT=0.55
# TFIDF_WEIGHT=0.45
#
# Grounding (post-generation checks vs retrieved text):
# ORCHESTRATE_GROUNDING_MIN_OVERLAP=0.12
# ORCHESTRATE_GROUNDING_FAIL_MODE=resynthesize   # or: escalate
#
# Lexical rerank bonuses (query term + brand alignment):
# ORCHESTRATE_RERANK_BONUS_TEAM=5
# ORCHESTRATE_RERANK_BONUS_WORKSPACE=5
# ORCHESTRATE_RERANK_BONUS_BRAND=3
```

If `OPENAI_API_KEY` is unset (or `ORCHESTRATE_DISABLE_LLM=1`), the agent uses an **offline synthesis** path (structured steps from retrieved articles; weaker than a quota-available LLM, but fully corpus-grounded).

## Run

From the **repository root** (recommended — avoids shadowing Python’s stdlib `code` module on Linux):

```bash
python code/main.py
```

Or from the `code/` directory:

```bash
python main.py
```

(`python -m code` is unreliable because it may load the **stdlib** `code` module instead of this folder.)

Options:

```text
--input   path to input CSV (default: ../support_tickets/support_tickets.csv)
--output  path to output CSV (default: ../support_tickets/output.csv)
--limit N process only the first N rows (default 0 = all rows; must be >= 0)
--fail-fast        exit on first row exception (exit 2); default is write escalated placeholder rows
--progress         tqdm progress bar (requires `tqdm` installed)
--max-field-chars N cap Issue/Subject length per row (default: env ORCHESTRATE_MAX_FIELD_CHARS or 200000)
```

Exit codes: **0** success; **2** user error (missing input, bad CSV schema, bad `--limit` / `--max-field-chars`, unusable `--output`, missing `data/`, index lock timeout, **`--fail-fast` row error**). Exceptions in row processing are caught by default (escalated row); otherwise **1** for unexpected crashes.

The first run builds a retrieval index under `code/.cache/bm25_index.pkl`. Delete it if you change chunking/fusion logic or bump `ORCHESTRATE_INDEX_VERSION`.

### Quick regression (sample file)

```bash
python run_eval.py --offline
```

Optional diagnostics on the generated `sample_pred.csv`:

```bash
python run_eval.py --offline --report-quality
```

`eval_sample.py` reports exact match on routing columns and **fuzzy stats on `response`** (normalized exact, token F1, character overlap). Use them to catch regressions on free-text answers; the official holdout is still scored by the platform.

Compare any gold CSV to predictions (e.g. internal dev labels with `Justification`):

```bash
python compare_outputs.py --gold ../path/to/gold.csv --pred ../support_tickets/output.csv
```

### Tests

```bash
cd code
python -m pytest tests -q
```

CI (GitHub Actions) runs the same **pytest** + **`run_eval.py --offline`** on each push/PR.

## Architecture

| Module          | Role                                               |
| --------------- | -------------------------------------------------- |
| `corpus.py`     | Loads markdown, strips noise, chunks articles       |
| `retrieve.py`   | Hybrid retrieval index + brand filtering + rerank |
| `taxonomy.py`   | Canonical `product_area` mapping                  |
| `grounding.py` / `postprocess.py` | Cheap grounding checks + finalize |
| `risk.py`       | Regex escalation triggers (e.g. grading disputes) |
| `openai_agent.py` | JSON-grounded LLM decisioning + offline synthesis |
| `eval_metrics.py` / `eval_sample.py` | Sample regression metrics |
| `ticket_hints.py` | Optional multi-topic heuristics (tests / docs) |
| `main.py`       | CSV orchestration                                  |

Secrets are read **only** from the environment (never commit `.env`).
