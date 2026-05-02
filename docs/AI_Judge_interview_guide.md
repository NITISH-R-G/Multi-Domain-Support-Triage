# AI Judge interview guide — questions & model answers

Study alongside [`interview.md`](./interview.md) and [`decisions.md`](./decisions.md). **Adapt** answers to what *you* actually did—don’t read these verbatim if untrue for your run.

**Answer shape:** claim → **why** → **trade-off** → **failure/limit** (when relevant).

---

## 1. Opening & framing

**Q: Walk through your solution in two minutes.**

**A:** The agent is a **batch CSV pipeline** (`main.py`): read each ticket → **retrieve** top chunks from the offline markdown corpus in `data/` using **hybrid BM25 + TF-IDF** (`retrieve.py`) scoped by brand → optional **OpenAI** turns retrieved context into structured JSON (`openai_agent.py`) → **`postprocess`** aligns taxonomy, runs **grounding** checks, then writes **`status`, `product_area`, `response`, `justification`, `request_type`**. If retrieval is weak or policy says so, we **escalate** or **offline-synthesize** from hits instead of inventing policies.

---

**Q: What problem does it solve end-to-end?**

**A:** **First-line support triage** for three brands (HackerRank, Claude, Visa): classify the ticket, pull relevant help-center text we actually ship in `data/`, reply when safe or **escalate** when the ticket needs a human (risk, legal-ish, cross-product, or no good retrieval match).

---

**Q: What would you put on slide one for an exec?**

**A:** “**Corpus-grounded** ticket triage: same answers a human would find in our help library—**not** the open web; **escalate** when policy or risk says so.”

---

**Q: What is the single biggest risk in your design?**

**A:** **Lexical retrieval** can miss paraphrased tickets, so we can get **weak hits** and then either **escalate** (low scores) or **over-rely** on the LLM unless grounding catches drift. Mitigations today: hybrid fusion, grounding overlap, numeric guard, escalation routes.

---

## 2. Architecture & module boundaries

**Q: Why split retrieve / openai_agent / postprocess / risk / taxonomy?**

**A:** **Separation of concerns**: retrieval is **deterministic** and fast; **risk** runs **before** expensive generation; **LLM** only sees packaged context; **postprocess** is the **single place** for taxonomy + grounding so we don’t duplicate logic. Easier to test (`pytest`) and to swap the LLM or retrieval later.

---

**Q: Where does reasoning happen vs retrieval vs policy?**

**A:** **Retrieval** = evidence fetch (`retrieve.py`). **Policy** = risk regex + cross-ecosystem + invalid small-talk (`risk.py`, `cross_ecosystem.py`, `taxonomy.py`). **Reasoning/synthesis** = LLM or **`fallback_from_hits`** (`openai_agent.py`, `answer_synthesis.py`). **Final merge** = `finalize_decision` in `postprocess.py`.

---

**Q: Why CLI (`main.py`) not a notebook?**

**A:** The challenge is **terminal-based**, batch **CSV in/out**, and evaluators need a **reproducible command**. A notebook is easier for exploration but worse for **CI**, diff review, and **submission**.

---

**Q: How would you add a second LLM provider?**

**A:** Isolate provider calls behind a small interface in **`openai_agent.py`** (or a new `llm_providers.py`): same input `{context, ticket}` → same JSON schema out. Wire with **env** like `LLM_PROVIDER=openai|anthropic`. Keep **`decide_with_openai`** name or rename for clarity.

---

## 3. Retrieval (BM25 + TF-IDF)

**Q: Why BM25?**

**A:** Strong **lexical** baseline for support articles: fast, no GPU, works well when ticket words overlap doc words; **deterministic** given fixed corpus and index version.

---

**Q: Why add TF-IDF fusion?**

**A:** BM25 can rank by term frequency quirks; **cosine TF-IDF** on the same tokenized docs adds a **second signal** when wording diverges slightly. We **normalize and fuse** scores (`BM25_WEIGHT`, `TFIDF_WEIGHT`) to stabilize ranking on noisy queries.

---

**Q: What do HYBRID_CANDIDATES, BM25_WEIGHT, TFIDF_WEIGHT control?**

**A:** **`HYBRID_CANDIDATES`** = how many BM25 top docs enter the fusion stage (recall vs speed). **Weights** = balance between BM25 vs TF-IDF in the fused score after min-max normalization on the candidate set.

---

**Q: Why lexical rerank bonuses (team / workspace / brand)?**

**A:** When the **query** mentions e.g. “team” or “workspace” and the **chunk** does too, we **boost** score—cheap signal that often matches real user language in this corpus.

---

**Q: What happens when top BM25 score is low (`LOW_BM25_THRESHOLD`)?**

**A:** `should_escalate_low_retrieval` flags **`low_retrieval`**. The LLM path is pushed toward **escalation** or conservative answers; offline path may escalate if combined with empty/poor hits—exact behavior is in `openai_agent.py` / `fallback_from_hits` + `finalize_decision`.

---

**Q: Why not embeddings / Pinecone for this hackathon?**

**A:** **Trade-off:** embeddings add **dependencies, build time, CI complexity,** and GPU/hosted infra choices. We prioritized **reproducible** lexical retrieval + tests + CI green. **Honest limit:** paraphrases suffer; **next increment** would be **cached dense vectors** merged with BM25 (hybrid), still offline.

---

## 4. Corpus grounding & hallucinations

**Q: How do you ensure answers use `data/` not parametric knowledge?**

**A:** **Every LLM call** includes **`format_context(hits)`**—only retrieved chunk text + titles/paths. Instructions say **do not invent** URLs/numbers not in context. **Post-check:** **`lexical_overlap`** between response and top hits + **`has_unsupported_numbers`** flags digit-heavy claims not in evidence.

---

**Q: What does `format_context` pass?**

**A:** For each hit: **score, brand, path, title, breadcrumbs, truncated body**—so the model can cite real library structure.

---

**Q: What is `GROUNDING_MIN_OVERLAP`?**

**A:** Minimum **fraction of non-stopword response tokens** that appear in retrieved evidence. Below threshold → **resynthesize from hits** or **escalate** depending on `GROUNDING_FAIL_MODE`.

---

**Q: `GROUNDING_FAIL_MODE=resynthesize` vs `escalate`?**

**A:** **Resynthesize** (default): safer UX—still produce an answer from chunks via `fallback_from_hits`. **Escalate**: stricter—when we distrust the generator entirely (e.g. compliance-heavy org).

---

**Q: What does `has_unsupported_numbers` guard?**

**A:** Long digit strings (phones, IDs) in the response that **don’t appear** in retrieved text—reduces **fabricated numbers**.

---

**Q: What if the LLM ignores context?**

**A:** Grounding overlap drops → we **replace** with offline synthesis or escalate per mode; JSON parse failures **fall back** to offline or escalate when confidence is low.

---

## 5. Escalation & safety

**Q: Give two `risk.py` patterns and why they escalate before generation.**

**A:** Example 1: **“grading dispute / change my score”**—outcome manipulation; public docs rarely authorize reversing grades → **escalate**. Example 2: **legal threat / self-harm** strings—route to humans per duty-of-care / policy—not answer from FAQs.

---

**Q: What is cross-ecosystem escalation?**

**A:** If one ticket clearly mixes **two product worlds** (e.g. **HackerRank + Claude**, or **Claude + Visa card/fraud context**), answering once would **blend policies** wrong—we **escalate** with a clear reason (`cross_ecosystem.py`). **Visa** detection requires **financial/product** cues to avoid “immigration visa” false positives.

---

**Q: Escalate vs reply “out of scope”?**

**A:** **`invalid` + short reply** for spam/thanks/trivia (`taxonomy` / invalid heuristics). **Escalate** when human judgment is required (risk, legal, mixed vendors, strong uncertainty).

---

**Q: Prompt injection / jailbreak?**

**A:** **Risk patterns** catch many “reveal your prompt/rules” style asks; we **don’t claim** full robustness—regex lists can miss novel attacks.

---

## 6. Taxonomy & outputs

**Q: How is `product_area` chosen?**

**A:** Model suggests something → **`normalize_product_area`** maps to **`CANONICAL_PRODUCT_AREAS`** using rules + top chunk path/title + ticket text (`taxonomy.py`). Keeps labels **evaluator-friendly** and stable.

---

**Q: What is `CANONICAL_PRODUCT_AREAS` for?**

**A:** Small **fixed vocabulary** (`screen`, `community`, `privacy`, …) so outputs aren’t random free-text categories.

---

**Q: Who sets `request_type` invalid vs model?**

**A:** **`infer_request_type`** can override for obvious cases (small talk, outage wording → bug, etc.); otherwise LLM/offline draft + validation in **`_validate_row`**.

---

**Q: `Company=None` — brand inference?**

**A:** **`infer_brand`** scores BM25 per brand mask on query tokens and picks best (`retrieve.py`), then retrieval runs **scoped** to that brand.

---

**Q: Multi-topic rows?**

**A:** Same-brand bundles: **`ticket_hints`** adds a **justification note**; cross-brand → **escalate** (`cross_ecosystem`). No automatic ticket splitting.

---

## 7. LLM usage & offline mode

**Q: Why structured JSON from OpenAI?**

**A:** **Machine-checkable** outputs; aligns to CSV schema; reduces rambling; easier to **validate** and fix enums.

---

**Q: `temperature` ~0.1 and `response_format` JSON?**

**A:** Low temperature for **stable** routing text; **JSON mode** enforces parseable output for downstream validation.

---

**Q: API failure / rate limit?**

**A:** **Catch exception** → `fallback_from_hits` with explanation in justification path—pipeline **does not crash** the batch.

---

**Q: `ORCHESTRATE_DISABLE_LLM=1`?**

**A:** Skips API; uses **offline synthesis** from retrieved chunks only—fully reproducible for CI and baseline metrics.

---

**Q: `fallback_from_hits` product_area slugs vs finalize?**

**A:** Fallback may derive a slug from breadcrumbs; **`finalize_decision`** runs **`normalize_product_area`** so final CSV uses **canonical** labels.

---

## 8. Determinism, testing, CI

**Q: What is seeded / deterministic?**

**A:** **`SEED`** for Python/NumPy where used; **same corpus + same env** → same index when cache rebuilt; **offline** path deterministic. **LLM API** can still vary slightly.

---

**Q: What does pytest cover?**

**A:** CSV I/O, taxonomy, risk, merge CLI, module invocation, **golden sample routing** (offline), cross-ecosystem, etc. **Does not** prove hidden leaderboard accuracy.

---

**Q: CI?**

**A:** **`pip install`**, **`main.py --help`**, **`pytest`**, **`run_eval --offline`**—matches `scripts/verify_local.*`.

---

## 9. Output CSV & evaluation alignment

**Q: How do you validate outputs?**

**A:** **`run_eval.py` / `eval_sample.py`** for **routing** exact match on public sample; fuzzy stats on free text; **manual spot checks** per `DEV_EVAL.md` for tone/grounding.

---

**Q: Improve low response scores without breaking grounding?**

**A:** Tune prompts to **cite steps from chunks**; increase **`TOP_K`** slightly; improve **chunking** in corpus loader; **optional** embeddings for recall—**not** “be more creative” without evidence.

---

## 10. AI assistance & transcript

**Q: How did you use AI tools?**

**A:** Use your **truth**: e.g. “Cursor for implementation + refactors; I specified architecture, reviewed every diff, ran **pytest** and **run_eval** before accepting changes.”

---

**Q: What did you design vs AI generate?**

**A:** **You should own:** pipeline stages, retrieval approach, escalation philosophy, env/CLI contract. **AI often helped:** boilerplate, tests, docstrings—**you** integrated and verified.

---

**Q: Example of rejecting AI?**

**A:** Any real story: “Suggested combining retrieval into one file—I kept **`retrieve.py` separate** for testability and caching.”

---

**Q: Rough early prompts in transcript?**

**A:** “Early prompts were broad; I narrowed scope—**file-by-file**, **run tests after each change**—the transcript shows **iteration**, not blind acceptance.”

---

## 11. Failure modes & fixes

**Q: Name three failures.**

**A:** (1) **Paraphrase** → miss retrieval. (2) **Wrong brand** when `Company=None`. (3) **Regex gaps** on novel harmful text.

**Fixes:** embeddings/hybrid; better brand features; expand risk list + monitoring.

---

**Q: Non-English tickets?**

**A:** Corpus and tokenizer are **English-centric** → **degraded** retrieval; would add language detect + route/translate **carefully** (cost/latency).

---

**Q: One more day—priority order?**

**A:** **Cached embeddings + hybrid** (recall) **or** calibration sweep on grounding thresholds—pick based on whether failures were **recall** vs **unsafe replies**.

---

## 12. Product / business

**Q: Who is the user?**

**A:** **Support ops / triage queue**—reduce volume hitting humans; **not** a replacement for crisis or legal.

---

**Q: Why escalate vs always answer?**

**A:** **Wrong answer** on billing/legal costs more than a human touch; trust > completion rate.

---

**Q: Measure success in production?**

**A:** Deflection rate, **CSAT** on bot replies, **escalation quality**, **grounding audit** sample, **incident** rate from bad answers.

---

## 13. Ethics

**Q: Why escalate billing/fraud/legal instead of improvising?**

**A:** FAQs aren’t **authorization** to change money outcomes or legal positions; **escalation** reduces harm and liability.

---

**Q: Reduce harm from wrong answers?**

**A:** **Retrieve-first**, **ground checks**, **escalate** under uncertainty, **no live web** for authoritative claims.

---

## 14. Stress drills

**Q: `product_area` wrong for row X—how debug?**

**A:** Reproduce row → print **top hits** + scores → check **brand** + **taxonomy rules** → compare **`map_product_area`** inputs; adjust rule or retrieval weight—not guess labels.

---

**Q: Prove retrieval ran.**

**A:** **Justification** cites paths/titles; **logging** could add chunk IDs (future); **debugger**: inspect **`hits`** list for that row in `process_row`.

---

**Q: Why not live Google?**

**A:** Challenge requires **bundled corpus only**; live web **breaks** reproducibility and **ground truth** alignment with evaluator labels.

---

## 15. Closing

**Q: Questions for us?**

**A:** Have one **substantive** question (e.g. how production eval differs from contest)—optional.

---

**Q: What do you wish you’d built?**

**A:** Honest: **embedding index** + **calibrated escalation dashboard**—pick what fits your story.

---

## Quick map → repo files

| Topic | File(s) |
|-------|---------|
| Retrieval | `code/retrieve.py` |
| Grounding | `code/grounding.py`, `code/postprocess.py` |
| Risk | `code/risk.py`, `code/cross_ecosystem.py` |
| Taxonomy | `code/taxonomy.py` |
| LLM | `code/openai_agent.py` |
| CLI | `code/main.py` |
| Design | `docs/decisions.md` |

---

*Adapt answers to your actual choices. Judges reward **honest limits** and **clear ownership**.*
