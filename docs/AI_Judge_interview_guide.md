# AI Judge interview guide — question bank & how to answer

Use with [`interview.md`](./interview.md) (short cheat sheet) and [`decisions.md`](./decisions.md) (design truth). **Camera on**, ~**30 minutes**. The judge can see your submission; questions below mirror **`evaluation_criteria.md`**.

**Answer recipe:** 30–60 seconds: claim → **why** → **trade-off** → **failure mode** (optional). Honesty beats hype.

---

## 1. Opening & framing

Possible questions:

- Walk me through your solution in **two minutes**.
- What problem does your agent solve end-to-end?
- What would you put on **slide one** for an exec?
- What is the **single biggest risk** in your design?

**Angles:** Retrieval-grounded triage; corpus-only answers; escalate when unsafe or unsupported.

---

## 2. Architecture & module boundaries

- Why split **`retrieve` / `openai_agent` / `postprocess` / `risk` / `taxonomy`** instead of one script?
- Where does **reasoning** happen vs **retrieval** vs **policy**?
- Why **`main.py`** as CLI vs a notebook?
- How would you add a **second LLM provider** without rewriting everything?

**Own:** Pipeline stages; lazy imports in hot paths; env-driven optional LLM.

---

## 3. Retrieval (BM25 + TF-IDF)

- Why **BM25**?
- Why add **TF-IDF cosine** fusion—what failure mode does it reduce?
- What do **`HYBRID_CANDIDATES`**, **`BM25_WEIGHT`**, **`TFIDF_WEIGHT`** control?
- Why **lexical rerank bonuses** (team/workspace/brand)?
- What happens when **top BM25 score is low** (`LOW_BM25_THRESHOLD`)?
- **Alternatives considered:** dense embeddings, cross-encoders, Pinecone/Weaviate—why accept or reject them for *this* hackathon?

**Honest limits:** Paraphrase mismatch; no semantic recall guarantee without embeddings.

---

## 4. Corpus grounding & hallucinations

- How do you ensure answers use **`data/`** and not parametric knowledge?
- What does **`format_context`** pass into the LLM?
- What is **`GROUNDING_MIN_OVERLAP`** doing?
- **`GROUNDING_FAIL_MODE=resynthesize` vs `escalate`**—when pick each?
- What does **`has_unsupported_numbers`** guard?
- What if the LLM **ignores** context—what breaks first?

**Sound bite:** “LLM only compresses **retrieved** text; grounding gates catch drift.”

---

## 5. Escalation & safety

- Walk through **`risk.py`**—give **two** patterns and why they escalate **before** generation.
- What is **cross-ecosystem escalation** (`cross_ecosystem.py`)?
- When would you **escalate** vs **reply “out of scope”**?
- How do you handle **prompt injection** or **jailbreak** language?
- Grading disputes, legal threats, self-harm strings—where handled?

**Don’t claim:** Perfect adversarial robustness.

---

## 6. Taxonomy & outputs

- How is **`product_area`** chosen and normalized?
- What is **`CANONICAL_PRODUCT_AREAS`** for?
- **`request_type`** — who sets `invalid` vs model vs heuristics?
- **`Company=None`** — how is brand inferred?
- Multi-topic rows—what’s your policy?

---

## 7. LLM usage & offline mode

- Why **structured JSON** from OpenAI?
- **`temperature`**, **`response_format`**—why these choices?
- What happens on **API failure** / **rate limit**?
- **`ORCHESTRATE_DISABLE_LLM=1`** — what path runs?
- Why **`fallback_from_hits`** sometimes produces different **`product_area`** slugs—how does **`finalize_decision`** fix that?

---

## 8. Determinism, testing, CI

- What is **seeded** / **deterministic** in your pipeline?
- What is **not** deterministic (API sampling, etc.)?
- What does **`pytest`** cover? What **doesn’t** it cover?
- What does **GitHub Actions** run—would your submission **pass CI**?

---

## 9. Output CSV & evaluation alignment

- How do you validate **`status`**, **`product_area`**, **`response`** quality?
- What did **`run_eval.py --offline`** tell you?
- How would you improve **`response`** if scores were low—without breaking grounding?

---

## 10. AI assistance & transcript (`AI Fluency`)

- How did you use **AI coding tools**—Cursor, Copilot, etc.?
- What did **you** design vs what the tool **generated**?
- Give an example where you **rejected** the AI’s suggestion.
- How did your **prompting** evolve during the hackathon?
- If the transcript shows rough early prompts, how do you frame that positively?

**Strong answer:** Scoped tasks, review diffs, run tests, own architectural calls.

---

## 11. Failure modes & “what would you fix?”

- Name **three** ways your agent fails.
- Where does it fail **first** on **non-English** tickets?
- Biggest weakness vs **embedding-based** retrieval?
- If you had **one more day**, what ship order: embeddings, better regex, UI, monitoring?

---

## 12. Product / business angle

- Who is the **user** of this agent?
- Why **escalate** instead of always answering—business trade-off?
- How would you **measure success** in production?

---

## 13. Ethics & responsibility

- Why escalate **billing / fraud / legal** instead of improvising?
- How do you reduce **harm** from wrong answers?

---

## 14. Stress-style drills

- “Your **`product_area`** for row X is wrong—how would you debug?”
- “Prove retrieval ran for this ticket.”
- “Why shouldn’t we use **live Google** for answers?”

---

## 15. Closing

- Any questions for us?
- Anything you **wish** you’d built?

**Tip:** Prepare **one** crisp failure + **one** mitigation each for retrieval, grounding, escalation.

---

## Quick map → repo files

| Topic | Where to point |
|-------|----------------|
| Retrieval | `code/retrieve.py` |
| Grounding | `code/grounding.py`, `code/postprocess.py` |
| Risk | `code/risk.py`, `code/cross_ecosystem.py` |
| Taxonomy | `code/taxonomy.py` |
| LLM | `code/openai_agent.py` |
| CLI | `code/main.py` |
| Design narrative | `docs/decisions.md` |

---

*This guide lists **likely** question styles—not every judge uses every question.*
