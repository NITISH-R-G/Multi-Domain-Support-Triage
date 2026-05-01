# Interview prep — failure modes, limits, and answers you should own

Use this in the **AI Judge interview** (camera on). Honesty beats hype.

## What this agent is

- **Offline-first triage** over a **fixed markdown corpus** (`data/`): retrieve → route → compose answer from snippets or escalate.
- **Optional LLM** compresses/summarizes **only over retrieved context**; **quota/offline** falls back to deterministic synthesis.

## What it is not

- Not live web search; **no** fetching current outage pages.
- Not a **multi-turn** chatbot or CRM integration.
- Not **embedding-grounded** semantic search in the default path (lexical hybrid BM25 + TF‑IDF); **say so clearly** if asked why vs Pinecone/etc.

## Failure modes (be ready to name three)

1. **Paraphrase gap:** Ticket wording ≠ article wording → retrieval misses → escalation or weak overlap → grounding rewrite or escalate (`ORCHESTRATE_GROUNDING_FAIL_MODE`).
2. **Policy-sensitive asks:** Regex risk rules fire → escalate **before** creative answering (grading disputes, legal language, etc.).
3. **Malformed / hostile tickets:** Injection-ish asks escalate by policy; **don’t claim** perfect adversarial robustness.

## Edge cases you should admit

| Scenario | Honest line |
|----------|-------------|
| Multi-request in one row | Note in **justification** for same-brand tickets (`ticket_hints`). **Cross-ecosystem** (e.g. HackerRank + Claude, or Claude + lost Visa card) → **escalated** (`cross_ecosystem.py`). |
| Wrong `Company` field | Brand inference from query text + retrieval brand mask — **can mis-route**. |
| Non‑English | Mostly English corpus → **degraded** retrieval. |

## Trade-offs you chose deliberately

- **Determinism & reproducibility** over strongest neural retrieval on GPU.
- **Explicit escalation** over hallucinating policies for billing/legal/medical-style asks.

## If asked “how do you know it wins?”

- **You don’t know hidden scores.** Say you optimized **routing + grounding guards**, ran **sample regression** + **manual rubric spot checks** (see `DEV_EVAL.md`), and designed for **interview-defensible** limits.
