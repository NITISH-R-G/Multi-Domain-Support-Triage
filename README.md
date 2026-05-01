# HackerRank Orchestrate

Starter repository for the **HackerRank Orchestrate** 24-hour hackathon (May 1–2, 2026).

Build a terminal-based AI agent that triages real support tickets across three product ecosystems; **HackerRank**, **Claude**, and **Visa** — using only the support corpus shipped in this repo.

Read [`problem_statement.md`](./problem_statement.md) for the full task spec, input/output schema, and allowed values, and [`evaluation_criteria.md`](./evaluation_criteria.md) for how submissions are scored.

### Start here (run the bundled agent)

From the **repository root** (after `pip install -r code/requirements.txt`):

| Shell | Command |
|-------|---------|
| **Any** | `python -m code` — same as `python code/main.py` with correct imports |
| **bash / zsh** | `./scripts/run_agent.sh` or `bash scripts/run_agent.sh` |
| **PowerShell** | `pwsh -File scripts/run_agent.ps1` |

Optional offline-only: set `ORCHESTRATE_DISABLE_LLM=1`, then run one of the above. Full CLI flags are in [`code/README.md`](./code/README.md).

**Interview / demo:** [`docs/interview.md`](./docs/interview.md), [`docs/demo-script.md`](./docs/demo-script.md). **Manual answer quality:** [`docs/DEV_EVAL.md`](./docs/DEV_EVAL.md). **Scope:** [`docs/scope_and_limits.md`](./docs/scope_and_limits.md).

---

## Contents

1. [Repository layout](#repository-layout)
2. [What you need to build](#what-you-need-to-build)
3. [Where your code goes](#where-your-code-goes)
4. [Quickstart](#quickstart)
5. [Chat transcript logging](#chat-transcript-logging)
6. [Submission](#submission)
7. [Judge interview](#judge-interview)
8. [Evaluation criteria](#evaluation-criteria)

---

## Repository layout

```
.
├── AGENTS.md                       # Rules for AI coding tools + transcript logging
├── problem_statement.md            # Full task description and I/O schema
├── README.md                       # You are here
├── docs/                           # decisions.md, interview prep, demo script, dev rubric
├── scripts/                        # run_agent.sh / run_agent.ps1 (repo-root invocation)
├── code/                           # Participant agent (see code/README.md)
│   ├── main.py                     # CLI entry: reads CSV, writes predictions
│   ├── retrieve.py                 # Hybrid retrieval + reranking
│   ├── eval_sample.py              # Metrics vs sample_support_tickets.csv
│   └── tests/                      # pytest regression checks
├── data/                           # Offline support corpus (required to run locally)
│   ├── hackerrank/
│   ├── claude/
│   └── visa/
└── support_tickets/
    ├── sample_support_tickets.csv  # Labeled examples for development
    ├── support_tickets.csv         # Inputs for final predictions
    └── output.csv                  # Generated predictions (create by running the agent)
```

---

## What you need to build

A terminal-based agent that, for each row in `support_tickets/support_tickets.csv`, produces:

| Column         | Allowed values                                          |
| -------------- | ------------------------------------------------------- |
| `status`       | `replied`, `escalated`                                  |
| `product_area` | most relevant support category / domain area            |
| `response`     | user-facing answer grounded in the provided corpus      |
| `justification`| concise explanation of the routing/answering decision   |
| `request_type` | `product_issue`, `feature_request`, `bug`, `invalid`    |

Hard requirements (from `problem_statement.md`):

- Must be **terminal-based**.
- Must use **only the provided support corpus** (no live web calls for ground-truth answers).
- Must **escalate** high-risk, sensitive, or unsupported cases instead of guessing.
- Must avoid hallucinated policies or unsupported claims.

Beyond that you are free to bring your own approach — RAG, vector DBs, tool use, structured output, agent frameworks, classical ML, or anything else.

---

## Where your code goes

Implement the agent under [`code/`](./code/). This checkout includes a **Python** reference implementation: hybrid retrieval over `data/`, risk-based escalation, optional OpenAI JSON generation with offline fallback, and CSV I/O. Full setup, environment variables, and regression commands are documented in **[`code/README.md`](./code/README.md)**.

Conventions:

- Read secrets **only from environment variables** (see `.env.example`). **Never hardcode keys.**
- Be **deterministic** where possible (seeded retrieval / sampling).
- Write predictions to `support_tickets/output.csv`.

---

## Quickstart

Clone the repository and keep the **`data/`** folder next to `code/` — the agent does not fetch live help-center content; it reads the bundled corpus.

```bash
cd hackerrank-orchestrate-may26
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r code/requirements.txt
# Optional: fully offline run (no LLM API)
set ORCHESTRATE_DISABLE_LLM=1   # Windows cmd
# export ORCHESTRATE_DISABLE_LLM=1   # macOS / Linux
python -m code
```

This writes `support_tickets/output.csv`. **Regression:** `cd code` then `python run_eval.py --offline` (compares to `sample_support_tickets.csv`).

Submission expects a **zip of `code/` only** (no `data/` in the zip); evaluators use their own corpus copy. Your **`output.csv`** is uploaded separately.

---

## Chat transcript logging

This repo ships with an `AGENTS.md` that any modern AI coding tool (Cursor, Claude Code, Codex, Gemini CLI, Copilot, etc.) will read. It instructs the tool to append every conversation turn to a single shared log file:

| Platform       | Path                                              |
| -------------- | ------------------------------------------------- |
| macOS / Linux  | `$HOME/hackerrank_orchestrate/log.txt`            |
| Windows        | `%USERPROFILE%\hackerrank_orchestrate\log.txt`    |

You don't need to do anything to enable it — just use your AI tool normally. You'll upload this `log.txt` as your chat transcript at submission time.

---

## Submission

Submit on the HackerRank Community Platform:
<https://www.hackerrank.com/contests/hackerrank-orchestrate-may26/challenges/support-agent/submission>

You will upload **three** files:

1. **Code zip** — zip your `code/` directory and upload it. Exclude virtualenvs, `node_modules`, build artifacts, the `data/` corpus, and the `support_tickets/` CSVs.
2. **Predictions CSV** — your agent's output for `support_tickets/support_tickets.csv` (i.e. the populated `output.csv`).
3. **Chat transcript** — the `log.txt` from the path in [Chat transcript logging](#chat-transcript-logging).

---

## Judge interview

After a successful submission, your AI Judge interview will happen within a few hours after the hackathon ends. It will stay open for the next 4 hours. 

The AI Judge will have access to your submission and may ask about your approach, decisions, and how you used AI while building your solution. The interview will be 30 minutes long, and keeping your camera on is mandatory.

Results will be announced on May 15, 2026

---

## Evaluation criteria

Submissions are scored across four dimensions: agent design (your `code/`), the AI Judge interview, output accuracy on `support_tickets/output.csv`, and AI fluency from your chat transcript.

See [`evaluation_criteria.md`](./evaluation_criteria.md) for the full rubric. Design notes for this repo’s agent: [`docs/decisions.md`](./docs/decisions.md).