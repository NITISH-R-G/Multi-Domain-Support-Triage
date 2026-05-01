# Path to strongest competitive position — implementation plan

> **For agentic workers:** Implement phase-by-phase; checkpoint after each phase with `scripts/verify_local.*` and documented metrics.

**Goal:** Maximize expected placement on **HackerRank Orchestrate** by aligning code, outputs, and interview narrative with `evaluation_criteria.md`, closing measurable gaps on routing + answer quality, and eliminating preventable submission mistakes.

**Honesty (read once):** No implementation makes winning **certain**. Hidden labels, rival submissions, and subjective interview scoring are **unknowables**. This plan aims for **dominant robustness**—best-effort **maximum expected score**, not a mathematical guarantee.

**Architecture:** Keep the current pipeline (**retrieve → decide → postprocess → CSV**) and strengthen it incrementally: better retrieval where lexical fails, tighter grounding and taxonomy alignment, systematic measurement against **sample + synthetic adversarial rows**, and presentation artifacts for judges.

**Tech Stack:** Python 3.11+, existing `rank-bm25` / numpy / pandas / optional OpenAI; optional **sentence-transformers** or hosted embeddings behind feature flags if added.

---

## File map (what you will touch most)

| Area | Primary files |
|------|----------------|
| Retrieval | `code/retrieve.py`, `code/corpus.py`, `code/config.py` |
| Routing / safety | `code/risk.py`, `code/cross_ecosystem.py`, `code/taxonomy.py` |
| Answers | `code/openai_agent.py`, `code/postprocess.py`, `code/grounding.py`, `code/answer_synthesis.py` |
| I/O & CLI | `code/main.py`, `code/csv_io.py` |
| Measurement | `code/run_eval.py`, `code/eval_sample.py`, `support_tickets/sample_eval_report.csv` |
| Docs / judge | `docs/interview.md`, `docs/decisions.md`, `README.md`, `evaluation_criteria.md` |

---

## Phase 0 — Freeze a baseline (half day)

**Purpose:** Every later change is judged against numbers, not vibes.

- [ ] Record **current** metrics in a single note (gitignored or `docs/`): Python version, commit hash, env vars (`ORCHESTRATE_*`, `OPENAI_MODEL`).
- [ ] Run `scripts/verify_local.ps1` / `.sh` → capture pytest count, sample **routing** exact %, full batch row count.
- [ ] Run **with LLM enabled** (if allowed for final submit): `python main.py --limit 0` once; save token-F1 / overlap from `eval_sample.py` if you add `--report-quality` path—baseline **free-text** quality.
- [ ] Export `support_tickets/output.csv` checksum or row count into that note.

**Exit criterion:** You can answer “what regressed?” after any experiment.

---

## Phase 1 — Maximize proxy for hidden CSV accuracy (largest lever)

### 1A — Exhaust the public sample as a syllabus

- [ ] Build a **row-by-row diff** script or notebook: for each `sample_support_tickets.csv` row, show gold vs pred for all five columns (reuse merge logic from `eval_sample.py`).
- [ ] Tag failures: **routing** vs **response text** vs **justification**.
- [ ] For every routing mismatch (should be rare offline): **root-cause** (brand inference, taxonomy rule, risk false positive).
- [ ] Add **pytest** cases that encode gold expectations for **routing columns** on sample rows (golden-file style), so refactors can’t silently break routing.

**Files:** `code/tests/` new module e.g. `test_sample_routing_golden.py`; possibly small fixture CSV under `code/tests/fixtures/`.

### 1B — Synthetic / adversarial suite (proxy for “malicious / multi-topic / None company”)

- [ ] Curate ~20–40 **hand-written** tickets covering: injection phrases, dual-intent same-brand, `Company=None` edge cases, billing-ish wording, outage wording.
- [ ] For each, document **expected** `status` + `request_type` + rough `product_area` **as you intend policy**—this becomes your **contract**.
- [ ] Add tests OR a `run_adversarial_eval.py` that fails CI when behavior drifts.

**Files:** `code/tests/test_adversarial_routing.py` or `support_tickets/adversarial_tickets.csv` + runner.

### 1C — Retrieval upgrade (optional but high ceiling when lexical fails)

Pick **one** path—do not half-do both:

| Option | When | Work |
|--------|------|------|
| **A. Cached dense embeddings** | Paraphrase-heavy hidden set | Build offline index (e.g. `sentence-transformers`) over same chunks; hybrid fuse with BM25 scores; bump `ORCHESTRATE_INDEX_VERSION`; CI either caches model or skips embedding job with env flag. |
| **B. Query expansion** | No GPU / lighter | Synonym / acronym map per brand; expand query tokens before BM25. |

- [ ] AB test vs baseline on **sample + adversarial** fuzzy metrics and routing %.

**Files:** `code/retrieve.py`, `code/config.py`, new `code/embeddings.py` or `code/query_expand.py`; `requirements.txt` only if new deps.

---

## Phase 2 — Answer + justification quality (ties breaker after routing matches)

### 2A — LLM path quality

- [ ] Tune **system/user prompts** in `openai_agent.py`: insist on **short** responses, **numbered steps**, **cite article titles** in justification.
- [ ] Keep **`temperature` low** (already ~0.1); validate **JSON** parsing failures → escalate or offline fallback (already partially there).
- [ ] Run **with API** on full `support_tickets.csv`; compare `eval_sample.py` fuzzy scores **with LLM on vs off**—choose submit mode intentionally.

### 2B — Grounding hardness

- [ ] Sweep `ORCHESTRATE_GROUNDING_MIN_OVERLAP` and `GROUNDING_FAIL_MODE` on sample—plot **trade-off**: fewer hallucinations vs more escalations.
- [ ] If eval penalizes unsafe replies more than escalations, bias toward **`escalate`** on grounding fail.

**Files:** `code/postprocess.py`, `code/grounding.py`, `code/config.py`.

### 2C — `product_area` frozen ontology

- [ ] Ensure **every** output maps into **`taxonomy.CANONICAL_PRODUCT_AREAS`** (already partly enforced)—add assertion in `_validate_row` or finalize step that logs **unexpected** labels in dev.
- [ ] Add mapping table from retrieval breadcrumbs → canonical labels (reduce slug drift from `fallback_from_hits`).

**Files:** `code/taxonomy.py`, `code/openai_agent.py`, `code/postprocess.py`.

---

## Phase 3 — Submission & reproducibility (prevent unforced errors)

- [ ] **Pin** Python patch version in README optional table (e.g. “tested 3.11.x”).
- [ ] Document exact command sequence for **final** `output.csv` generation (LLM on/off).
- [ ] Pre-submit checklist in README: zip contents per organizer rules, **`output.csv`** regenerated same day, **`log.txt`** present and non-empty.
- [ ] CI green on default branch before zip.

**Files:** `README.md`, `.github/workflows/ci.yml` (only if adding useful smoke).

---

## Phase 4 — Interview + transcript (human-led, non-optional for “winner spot”)

These **cannot** be coded, but decide outcomes when CSV scores cluster.

- [ ] **Interview:** rehearse 10 prompts: architecture, why no embeddings / why embeddings, failure modes, multi-brand policy, honesty about AI assistance (`docs/interview.md` + your real decisions).
- [ ] **Transcript:** ensure `log.txt` shows **scoped asks**, **rejections of bad AI patches**, **your architectural commits**—not only “make it work.”

---

## Phase 5 — Diminishing returns (only if time remains)

- [ ] Narrative polish: one-page **architecture diagram** for judges (`docs/decisions.md` already has mermaid).
- [ ] Manual spot-check **10 random** output rows against retrieved chunks (`DEV_EVAL.md` rubric).
- [ ] Optional: tiny **ensemble** (two retrieval configs + vote on `status`)—high complexity; only if Phase 1 plateaued.

---

## Success metrics (definition of “done” for this plan)

| Metric | Target |
|--------|--------|
| CI + verify scripts | Always green |
| Sample routing columns (`status`, `request_type`, `product_area`) | **100%** offline (maintain) |
| Sample free-text | Improve token-F1 / overlap vs baseline when LLM on |
| Adversarial suite | **0 unintended regressions** after changes |
| Interview | Can explain every module in `code/` in ≤2 minutes each |

---

## What “winner no matter what” actually requires (truth)

1. **Higher hidden CSV score than everyone else** — unknowable until results.  
2. **Interview ceiling** — preparation, not repo content alone.  
3. **Luck / tie variance** — minimized by **margin**, not eliminated.

This plan maximizes **margin**; it does not issue a certificate of victory.
