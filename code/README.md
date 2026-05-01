# Support triage agent (Orchestrate)

Terminal agent that reads `support_tickets/support_tickets.csv`, retrieves grounded snippets from the offline `data/` corpus (**BM25 + TF‑IDF fusion + lexical rerank**), applies risk-based escalation rules + taxonomy mapping, and writes predictions to `support_tickets/output.csv`.

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
```

If `OPENAI_API_KEY` is unset (or `ORCHESTRATE_DISABLE_LLM=1`), the agent uses an **offline synthesis** path (structured steps from retrieved articles; weaker than a quota-available LLM, but fully corpus-grounded).

## Run

From the `code/` directory (so imports resolve):

```bash
python main.py
```

Options:

```text
--input   path to input CSV (default: ../support_tickets/support_tickets.csv)
--output  path to output CSV (default: ../support_tickets/output.csv)
--limit N process only the first N rows (debug)
```

The first run builds a retrieval index under `code/.cache/bm25_index.pkl`. Delete it if you change chunking/fusion logic or bump `ORCHESTRATE_INDEX_VERSION`.

### Quick regression (sample file)

```bash
python run_eval.py --offline
```

Optional diagnostics on the generated `sample_pred.csv`:

```bash
python run_eval.py --offline --report-quality
```

## Architecture

| Module          | Role                                               |
| --------------- | -------------------------------------------------- |
| `corpus.py`     | Loads markdown, strips noise, chunks articles       |
| `retrieve.py`   | Hybrid retrieval index + brand filtering + rerank |
| `taxonomy.py`   | Canonical `product_area` mapping                  |
| `grounding.py` / `postprocess.py` | Cheap grounding checks + finalize |
| `risk.py`       | Regex escalation triggers (e.g. grading disputes) |
| `openai_agent.py` | JSON-grounded LLM decisioning + offline synthesis |
| `main.py`       | CSV orchestration                                  |

Secrets are read **only** from the environment (never commit `.env`).
