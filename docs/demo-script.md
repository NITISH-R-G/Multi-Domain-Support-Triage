# 2-minute demo script (live or recording)

**Goal:** Show **trust**, **grounding**, and **escalation** — not feature laundry.

## Setup (5 seconds)

- Repo with `data/` present; `pip install -r code/requirements.txt`.
- `export ORCHESTRATE_DISABLE_LLM=1` (repeatable) **or** show both offline + LLM if quota allows.

## Minute 0:00–0:30 — Happy path (grounded reply)

1. Point to **`support_tickets/sample_support_tickets.csv`** — realistic ticket.
2. Run from repo root: **`python code/main.py --limit 1`** (or `scripts/run_agent.sh`) writing to a temp output.
3. Open row: show **`status=replied`**, **`justification`** citing retrieval path/score language.

**Say:** “Answers are composed from retrieved chunks only in offline mode.”

## Minute 0:30–1:00 — Escalation (risk)

1. Show **`risk.py`** pattern example (grading dispute / outage wording) or a ticket that triggers **`escalated`**.
2. Show **`status=escalated`** and generic safe response — **no invented policy**.

**Say:** “We escalate before we invent.”

## Minute 1:00–1:30 — Invalid / out-of-scope

1. Short gratitude or trivia-style row → **`request_type=invalid`** or out-of-scope reply.

**Say:** “Invalid bucket avoids wasting human escalation.”

## Minute 1:30–2:00 — Engineering credibility

1. **`python -m pytest code/tests -q`**
2. **`python code/run_eval.py --offline`** — routing metrics on sample.

**Say:** “Regression + CLI resilience so iteration doesn’t rot quality.”

## One sentence close

“We optimized **trustworthy routing and corpus-grounded text**, not parametric knowledge—and we know exactly where paraphrase and multilingual inputs degrade.”
