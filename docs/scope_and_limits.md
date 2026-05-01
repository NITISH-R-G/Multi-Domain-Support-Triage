# Scope and limits (what we built vs what we did not)

This keeps expectations aligned with **`problem_statement.md`**: terminal agent, **offline corpus only**, CSV output, escalate when unsafe.

## In scope (implemented)

- **Hybrid lexical retrieval** (BM25 candidates + fused TF‑IDF cosine + lexical rerank bonuses).
- **Risk routing** via maintained regex patterns (expandable in `risk.py`).
- **Canonical `product_area`** mapping tied to corpus paths and brand intent (`taxonomy.py`).
- **Grounding checks** (lexical overlap + numeric-string heuristic) with configurable failure behavior.
- **Optional OpenAI** structured JSON over retrieved context; **offline synthesis** when disabled or API fails.
- **CLI** hardened for batch runs (validation, row isolation, merge checks).

## Explicit non-goals (for reviewers)

- **No vector DB / embedding index** in the baseline pipeline — avoids GPU dependency and keeps CI deterministic; trade-off is weaker semantic recall on paraphrases.
- **No human review queue UI** — output is CSV rows only.
- **Cross-ecosystem tickets** (pairwise: HackerRank+Claude, HackerRank+Visa financial, Claude+Visa financial) **escalate** by default — avoids one wrong blended answer. Same-brand multi-question rows still get a single primary reply + transparency note.

## When embeddings would be justified

If targeting **top-tier recall on paraphrase**, the next increment would be **cached embedding index** over the same chunks (hybrid RRF with BM25), still **no live web** for answers.
