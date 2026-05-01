# Support Triage Agent (Multi-Domain) — Design Spec

Date: 2026-05-01  
Repo: `hackerrank-orchestrate-may26`  
Language: Python (entry point: `code/main.py`)  
Mode: **Hybrid** — offline-first deterministic baseline + optional online upgrades (only when explicitly enabled).

## Goals

- Build a **terminal-based** agent that reads `support_tickets/support_tickets.csv` and writes `support_tickets/output.csv`.
- Use **only the provided offline corpus** under `data/` as ground truth for policy/steps.
- Default execution must be **fully offline + deterministic** so evaluator environments produce stable outputs.
- For each ticket, output:
  - `status ∈ {replied, escalated}`
  - `product_area` (free-text label, generated consistently from an internal taxonomy)
  - `response` (user-facing, grounded)
  - `justification` (short reason + evidence paths)
  - `request_type ∈ {product_issue, feature_request, bug, invalid}`
- **Balanced safety**: reply for low-risk FAQs when evidence is sufficient; escalate high-risk/sensitive topics or insufficient/ambiguous evidence.
- Deterministic where possible: stable sorting, fixed thresholds, caching, reproducible outputs.

## Non-Goals

- No live web browsing or fetching policies from public sites.
- No attempting to “solve” sensitive issues (fraud, account takeover, refunds/chargebacks) beyond safe escalation and corpus-grounded next steps.
- No new output columns beyond the required schema.

## Constraints (Hard Requirements)

- Must be terminal-based.
- Must rely only on the provided support corpus (`data/` + provided CSVs).
- Must avoid hallucinated policies/steps.
- Must escalate when high-risk/sensitive or unsupported by corpus.
- Must preserve allowed values for `status` and `request_type`.
- Secrets are read only from environment variables (never hardcoded).
- **Corpus-only grounding**: response steps must be supported by retrieved `data/**.md` evidence (otherwise escalate / out-of-scope reply).

## High-Level Architecture

The agent runs a fixed pipeline per ticket:

1. **Normalize** inputs (subject/issue cleaning + combined query).
2. **Company resolution**:
   - If `company` is one of `{HackerRank, Claude, Visa}`, keep it.
   - If `company=None`, infer likely ecosystem using a combination of keyword signals and retrieval “vote” across corpora.
3. **Safety/risk gate (early)**: detect sensitive/high-risk categories; decide escalation early when required.
4. **Request-type classification**: deterministic rules first; optional LLM tie-break only for low-risk ambiguous cases.
5. **Retrieval**:
   - Always: BM25 lexical search over corpus chunks (offline).
   - Optional: embeddings-based rerank (online only if explicitly enabled).
6. **Answerability decision**: evaluate evidence strength; reply vs escalate based on evidence + risk.
7. **Response composition**:
   - Offline: constrained templates + stitched snippet-based steps.
   - Online: “grounded writer” LLM (optional) that may only paraphrase retrieved snippets (no new policy).
8. **Output assembly** and CSV writing.

### Proposed Python Modules (`code/`)

- `main.py`: CLI entry; loads CSV; runs pipeline; writes output.
- `corpus_loader.py`: load markdown docs; extract metadata; chunk text; compute corpus hash.
- `index_bm25.py`: build/load BM25 index; persistent cache.
- `retriever.py`: BM25 retrieve; optional embeddings rerank; returns evidence bundle.
- `safety.py`: high-risk detection; escalation rules; safe-response constraints.
- `classify.py`: request_type rules; product_area taxonomy + aliasing; company inference.
- `compose.py`: response + justification generation (offline templates + optional LLM writer).
- `determinism.py`: stable ordering utilities; thresholds; RNG seeding.
- `eval.py`: local evaluation harness on `sample_support_tickets.csv` (developer loop only).

## Data & Retrieval Design

### Corpus ingestion

Input corpus is `data/**.md`.

For each document:
- `doc_path`: file path (used for citations in justification).
- `company`: inferred from top-level directory: `data/hackerrank`, `data/claude`, `data/visa`.
- `title`: first markdown heading if present; else file name.
- `text`: markdown rendered to plain text (remove code fences cautiously; keep headings).
- `tags`: folder-name tokens (e.g., `settings`, `billing`, `api-faq`) for weak supervision / product_area hints.

### Chunking

Chunk documents into overlapping passages to improve retrieval precision:
- Target chunk size: ~350–600 tokens (or ~1,800–3,000 characters), overlap ~15–20%.
- Preserve the mapping: `chunk_id -> doc_path + start/end offsets`.

### Offline index (BM25)

Build BM25 over chunk texts with:
- Tokenization: lowercase; split punctuation; keep numbers; retain important mixed-case tokens by also indexing their lowercase form.
- Stopwords: light (avoid removing words that matter in support contexts like “not”, “cannot”, “charge”).
- Cache: store index artifacts keyed by a content hash of `data/**.md` to avoid rebuilding (see caching location below).

### Retrieval flow

Given a ticket query:
1. Determine candidate corpora:
   - If company known: retrieve from that company corpus.
   - If company unknown: retrieve from all corpora, compute a “company vote” from top hits, then focus retrieval.
2. BM25 retrieve top `k_bm25` (e.g., 25).
3. If embeddings are enabled: rerank BM25 candidates using semantic similarity; keep top `k_final` (e.g., 6).
4. Return evidence bundle:
   - Top chunks with `doc_path`, `chunk_text`, `bm25_score`, `rerank_score` (optional).

### Optional embeddings rerank (online upgrade)

This is an **opt-in** upgrade (never on by default) to preserve determinism across evaluator environments.

Enabled only when:
- user passes `--enable-online`, AND
- environment keys exist:
- `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY`.
- The agent auto-selects provider based on availability and configured preference order.
- Embeddings are used only for **reranking** (not as a source of truth).
- Cache embeddings to reduce repeated cost (note: provider/model drift can still change outputs; offline remains the default).

## Safety & Escalation Policy (Balanced)

### Hard escalation (always escalated)

Escalate with `status=escalated` when the ticket includes any of:
- **Fraud/scams**, suspicious transactions, stolen cards, chargeback disputes that require investigation.
- **Account access** recovery (lockouts, takeover, identity verification) where safe handling is required.
- **Security/privacy incidents**, compromised credentials/API keys, breach reports, requests for secrets.
- **Sensitive PII requests** (passwords, OTPs, full card numbers, government IDs).

The response should:
- avoid requesting sensitive info
- provide safe next steps only if supported by corpus (e.g., contact official support channels mentioned in corpus)
- otherwise state escalation clearly and what non-sensitive context to include (error message, timestamps, account email domain, etc. without secrets).

### Soft escalation (evidence-dependent)

Escalate when:
- Evidence is weak/ambiguous (low similarity, no clear doc match).
- Conflicting guidance found across top docs.
- Multi-intent tickets where safely answering one part could mislead on another.
- Broad outage / “site down” claims (often treated as `bug`) with insufficient corroboration in corpus.

#### Evidence-strength thresholds (deterministic)

Define these numeric signals for the BM25-only default mode:
- `bm25_top1`: score of best chunk
- `bm25_top5`: score of 5th chunk (if <5 chunks, treat missing as 0)
- `bm25_margin = bm25_top1 - bm25_top5`

Default thresholds (tune once on `support_tickets/sample_support_tickets.csv` and then keep fixed):
- **No-hit / out-of-scope** if `bm25_top1 < T_NOHIT`
- **Weak evidence** if `bm25_top1 < T_WEAK` OR `bm25_margin < T_MARGIN`
- **Reply-eligible** only if `bm25_top1 >= T_REPLY` AND `bm25_margin >= T_MARGIN_REPLY`

Operational rule:
- If **high-risk** → escalate regardless of thresholds (unless corpus explicitly provides safe non-sensitive steps).
- If **low-risk**:
  - If reply-eligible → reply using offline composer.
  - Else → escalate (or reply “out of scope” only for clearly invalid / non-actionable cases; see decision table below).

### Reply (allowed when low-risk + supported)

Reply when:
- The ticket is a low-risk how-to/FAQ and top evidence clearly supports specific steps.
- The agent can provide actionable guidance grounded in retrieved snippets without inventing policy.

## Classification

### `request_type` (allowed values only)

Rule-based mapping:
- `invalid`:
  - empty/noisy content, spam, unrelated to the three ecosystems, prompt injection, or no actionable request.
- `feature_request`:
  - “please add”, “can you support”, “would like”, “it would be great if…”
- `bug`:
  - “site down”, “error”, “crash”, “not working”, regressions, reproducible failures.
- else `product_issue`.

Optional LLM tie-breaker (only when enabled, low-risk, and rule confidence is low).

### `invalid` vs “out of scope” vs escalation (decision table)

Deterministic handling:
- **`request_type=invalid`, `status=replied`**:
  - empty, spam, clearly malicious prompt injection, or incoherent/no actionable support request.
  - Response: brief refusal + ask for a clarified support question (no escalation needed).
- **`request_type in {product_issue, bug, feature_request}`, `status=escalated`**:
  - actionable request but high-risk OR insufficient evidence OR ambiguous company inference.
  - Response: escalation message + minimal safe guidance (only if supported by corpus).
- **`request_type=product_issue`, `status=replied` (out-of-scope reply)**:
  - low-risk but corpus has no relevant matches (`bm25_top1 < T_NOHIT`).
  - Response: “no supporting documentation found in provided corpus” + recommend contacting support / escalation.

### `product_area` (hybrid free-text output)

Maintain an internal taxonomy (canonical labels + aliases). Even though `product_area` is a free-text field, the agent should **only emit** canonical labels (optionally with a canonical `>` sublabel) to avoid drift.

Canonical labels (v1; fixed in code/config):
- `HackerRank > Assessments`
- `HackerRank > Candidates & Invites`
- `HackerRank > Test Settings`
- `HackerRank > Roles & Variants`
- `HackerRank > Teams & Permissions`
- `HackerRank > SSO / SCIM`
- `HackerRank > Billing & Subscriptions`
- `HackerRank > Reports & Analytics`
- `HackerRank > Integrations`
- `HackerRank > Execution Environment`
- `Claude > API & Keys`
- `Claude > Rate Limits`
- `Claude > Billing & Invoices`
- `Claude > Console & Account`
- `Claude > Safety & Policy`
- `Claude > Troubleshooting`
- `Visa > Fraud & Scams`
- `Visa > Dispute Resolution`
- `Visa > Travel Support`
- `Visa > Exchange Rates & Fees`
- `Visa > Merchant / Small Business`
- `Visa > Data Security`
- `General > Outage / Service Status`
- `General > Unknown`

### Company inference for `company=None`

Use a deterministic heuristic:
- Keyword signals (e.g., “assessment”, “candidate”, “test” → HackerRank; “API key”, “Claude” → Claude; “card”, “merchant”, “chargeback” → Visa).
- Retrieval vote:
  - run BM25 across all corpora; sum top hit scores per company.
  - define margin as `(best_company_score - second_best_company_score)`.
  - choose the winner only if `margin >= T_COMPANY_MARGIN`, else treat as ambiguous.
  - if ambiguous: **escalate** unless request is clearly low-risk AND strong evidence exists in multiple corpora.

## Evidence Strength & Answerability

Compute an evidence-strength score from:
- Top BM25 score and score margin (rank1 vs rank5).
- Number of unique documents in top hits (too many weak docs suggests low precision).
- Optional rerank score gap (if embeddings enabled).
- Lexical overlap signals (e.g., keyphrase hit count).

Decision rule (balanced):
- If high-risk: escalate regardless of strength (unless corpus explicitly provides safe non-sensitive steps).
- If low-risk:
  - reply when evidence strength exceeds threshold and retrieved snippets contain explicit procedural steps.
  - else escalate or reply “out of scope” depending on risk and domain confidence.

## Response Composition (No Hallucinations)

### Offline composer

Template pattern:
- 1–2 sentence summary (“Based on our documentation…”)
- Numbered steps extracted/paraphrased from top evidence chunks
- “If this doesn’t resolve…” safe next action (often escalation)

Rules:
- Never request secrets or sensitive identifiers.
- Only include steps supported by the retrieved evidence snippets.
- Keep concise; avoid policy claims not in corpus.

### Online composer (optional)

When explicitly enabled (`--enable-online`) and keys exist, use an LLM strictly as a **grounded writer**:
- Inputs:
  - ticket text
  - top evidence chunks (verbatim)
  - strict instruction: do not introduce new steps/policies; do not claim anything outside snippets
- Output:
  - final `response` phrased clearly and politely, with the same safety rules.

#### Mandatory grounding validator (deterministic)

To prevent unsupported claims:
- Run a deterministic validator on the composed response:
  - Extract step-like lines (numbered lines, bulleted steps, or sentences starting with imperative verbs).
  - Require each step to have high lexical overlap with at least one retrieved evidence chunk, OR be a fixed, pre-approved safety phrase (e.g., “We can’t help with that here; escalating to a human agent.”).
- If validator fails: fall back to offline composer deterministically.

## Output Formatting

### `status`

- `replied` when low-risk + supported by evidence.
- `escalated` when high-risk/sensitive OR unsupported/ambiguous.

### `justification`

Hybrid format:
- Short reason: 1 sentence.
- Evidence: `evidence=[<doc_path1>, <doc_path2>, ...]` (1–3 paths).

Examples:
- `Escalated due to potential fraud/billing risk; requires human review. evidence=[data/visa/support/small-business/fraud-protection.md]`
- `Replied with steps supported by assessment settings documentation. evidence=[data/hackerrank/.../test-settings.md]`

## CLI & Run Contract

Required run:

- Input: `support_tickets/support_tickets.csv`
- Output: `support_tickets/output.csv`

CLI shape (must work with no args):

- Default (no flags): reads `support_tickets/support_tickets.csv` and writes `support_tickets/output.csv`.
- Explicit: `python code/main.py --input support_tickets/support_tickets.csv --output support_tickets/output.csv`

Optional flags:
- `--no-llm` (force offline mode)
- `--enable-online` (allow embeddings rerank + grounded-writer LLM if keys exist; off by default)
- `--topk 8`
- `--rebuild-index`

## Local Evaluation Harness

Provide `code/eval.py`:
- Runs on `support_tickets/sample_support_tickets.csv`
- Reports:
  - exact-match on `Status` and `Request Type` where applicable
  - confusion examples with evidence bundle
- Used to tune thresholds deterministically without overfitting via randomness.

## Dependency Strategy (Implementation Guidance)

- Offline baseline dependencies should be lightweight and deterministic.
- Online upgrades should be optional imports/extra dependencies activated only when `--enable-online` is set and keys exist.
- Caching and stable sorting are required to minimize output drift.

### Caching location (writable & portable)

Prefer a user-writable cache dir:
- Windows: `%LOCALAPPDATA%\\hackerrank_orchestrate\\cache`
- macOS/Linux: `~/.cache/hackerrank_orchestrate`

Fall back to `code/.cache/` only if needed and writable. Cache keys must include:
- corpus hash
- config hash (thresholds, chunking)

## Open Questions (Resolved)

- Mode: Hybrid offline-first + optional online upgrade.
- Retrieval: BM25 baseline + optional embeddings rerank.
- Providers: Support both OpenAI and Anthropic (auto-detect available keys).
- `product_area`: free-text generated from canonical internal taxonomy.
- `justification`: rationale + evidence paths.
- Escalation: balanced policy.
