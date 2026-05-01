# Support triage agent (Orchestrate)

Terminal agent that reads `support_tickets/support_tickets.csv`, retrieves grounded snippets from the offline `data/` corpus (BM25 + overlap rerank), applies risk-based escalation rules, and writes predictions to `support_tickets/output.csv`.

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
```

If `OPENAI_API_KEY` is unset, the agent uses an extractive fallback (weaker, but runs offline except for the corpus).

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

The first run builds a BM25 index under `code/.cache/bm25_index.pkl`; delete that file if you change chunking logic.

## Architecture

| Module          | Role                                               |
| --------------- | -------------------------------------------------- |
| `corpus.py`     | Loads markdown, strips noise, chunks articles       |
| `retrieve.py`   | BM25 index, brand filtering, lexical rerank        |
| `risk.py`       | Regex escalation triggers (e.g. grading disputes) |
| `openai_agent.py` | JSON-grounded LLM decisioning + fallback        |
| `main.py`       | CSV orchestration                                  |

Secrets are read **only** from the environment (never commit `.env`).
