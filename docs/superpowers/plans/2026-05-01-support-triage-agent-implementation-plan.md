# Support Triage Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a terminal-based, corpus-grounded, deterministic-by-default support triage agent that reads `support_tickets/support_tickets.csv` and writes `support_tickets/output.csv` with the required schema.

**Architecture:** Offline-first deterministic pipeline (BM25 retrieval + safety gate + rules) with optional opt-in online upgrades (`--enable-online`) for embeddings rerank and grounded response writing, guarded by a grounding validator and strict escalation rules.

**Tech Stack:** Python 3.11+, `pytest`, `rank-bm25`, `rapidfuzz` (optional), `python-dotenv` (dev only), optional `openai` and/or `anthropic` SDKs (only used when enabled and keys exist).

---

## File structure (lock in boundaries)

**Create (new):**
- `code/README.md`
- `code/requirements.txt`
- `code/main.py`
- `code/agent/pipeline.py`
- `code/agent/types.py`
- `code/agent/io_csv.py`
- `code/agent/text_norm.py`
- `code/agent/corpus_loader.py`
- `code/agent/chunking.py`
- `code/agent/bm25_index.py`
- `code/agent/retriever.py`
- `code/agent/company_infer.py`
- `code/agent/safety.py`
- `code/agent/classify.py`
- `code/agent/product_area.py`
- `code/agent/evidence_strength.py`
- `code/agent/compose_offline.py`
- `code/agent/compose_online.py`
- `code/agent/grounding_validator.py`
- `code/agent/cache_paths.py`
- `code/agent/determinism.py`
- `code/eval.py`

**Create (tests):**
- `code/tests/test_text_norm.py`
- `code/tests/test_company_infer.py`
- `code/tests/test_safety.py`
- `code/tests/test_request_type.py`
- `code/tests/test_product_area.py`
- `code/tests/test_bm25_retrieval_smoke.py`
- `code/tests/test_pipeline_sample_rows.py`

**No changes outside `code/` required**, except that the run must write `support_tickets/output.csv`.

---

## Task 1: Make `code/` runnable (README + deps + hello CLI)

**Files:**
- Create: `code/README.md`
- Create: `code/requirements.txt`
- Modify: `code/main.py`

- [ ] **Step 1: Create `code/requirements.txt` (offline-first)**

Put exactly this in `code/requirements.txt` (pin versions for reproducibility):

```txt
pytest==8.3.2
python-dotenv==1.0.1
rank-bm25==0.2.2
rapidfuzz==3.9.7
```

- [ ] **Step 2: Create `code/README.md`**

```markdown
# Support Triage Agent (HackerRank Orchestrate)

## Requirements
- Python 3.11+

## Install
From repo root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r code/requirements.txt
```

## Run (default contract)
```bash
python code/main.py
```

This reads `support_tickets/support_tickets.csv` and writes `support_tickets/output.csv`.

## Run (custom paths)
```bash
python code/main.py --input support_tickets/support_tickets.csv --output support_tickets/output.csv
```

## Offline vs Online
By default the agent runs offline and deterministic.

To enable optional online upgrades (embeddings rerank + grounded writer), set API keys and pass:
```bash
python code/main.py --enable-online
```

## Test
```bash
pytest -q code/tests
```
```

- [ ] **Step 3: Implement minimal `code/main.py` skeleton that writes output CSV with correct columns**

Replace `code/main.py` with:

```python
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_INPUT = Path("support_tickets/support_tickets.csv")
DEFAULT_OUTPUT = Path("support_tickets/output.csv")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Support triage agent (offline-first).")
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--enable-online", action="store_true", default=False)
    p.add_argument("--no-llm", action="store_true", default=False)
    p.add_argument("--topk", type=int, default=8)
    p.add_argument("--rebuild-index", action="store_true", default=False)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    # Placeholder: will be replaced by the real pipeline in later tasks.
    # Must keep CLI contract stable.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "status,product_area,response,justification,request_type\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the script to confirm it writes the header**

Run:
- `python code/main.py`

Expected:
- `support_tickets/output.csv` exists and has header line:  
  `status,product_area,response,justification,request_type`

- [ ] **Step 5: Commit**

```bash
git add code/README.md code/requirements.txt code/main.py
git commit -m "chore: add runnable skeleton and dependencies"
```

---

## Task 2: Define core types + CSV I/O (strict schema)

**Files:**
- Create: `code/agent/types.py`
- Create: `code/agent/io_csv.py`
- Create: `code/agent/determinism.py`
- Test: `code/tests/test_request_type.py`

- [ ] **Step 1: Create `code/agent/types.py`**

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Status = Literal["replied", "escalated"]
RequestType = Literal["product_issue", "feature_request", "bug", "invalid"]
Company = Literal["HackerRank", "Claude", "Visa", "None"]


@dataclass(frozen=True)
class TicketIn:
    issue: str
    subject: str
    company: Company


@dataclass(frozen=True)
class EvidenceChunk:
    doc_path: str
    chunk_id: str
    text: str
    bm25_score: float
    rerank_score: float | None = None


@dataclass(frozen=True)
class TriageOut:
    status: Status
    product_area: str
    response: str
    justification: str
    request_type: RequestType


@dataclass(frozen=True)
class PipelineConfig:
    topk: int = 8
    enable_online: bool = False
    no_llm: bool = False
    rebuild_index: bool = False
```

- [ ] **Step 2: Create `code/agent/determinism.py`**

```python
from __future__ import annotations

import hashlib


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_sort_key(*parts: object) -> tuple:
    return tuple(parts)
```

- [ ] **Step 3: Create `code/agent/io_csv.py`**

```python
from __future__ import annotations

import csv
from pathlib import Path

from .types import TicketIn, TriageOut


def read_tickets(path: Path) -> list[TicketIn]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        out: list[TicketIn] = []
        for row in reader:
            out.append(
                TicketIn(
                    issue=(row.get("Issue") or row.get("issue") or "").strip(),
                    subject=(row.get("Subject") or row.get("subject") or "").strip(),
                    company=(row.get("Company") or row.get("company") or "None").strip(),  # type: ignore[arg-type]
                )
            )
        return out


def write_outputs(path: Path, rows: list[TriageOut]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["status", "product_area", "response", "justification", "request_type"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "status": r.status,
                    "product_area": r.product_area,
                    "response": r.response,
                    "justification": r.justification,
                    "request_type": r.request_type,
                }
            )
```

- [ ] **Step 4: Add a small unit test for allowed request types**

Create `code/tests/test_request_type.py`:

```python
def test_allowed_request_type_values():
    allowed = {"product_issue", "feature_request", "bug", "invalid"}
    assert "bug" in allowed
```

- [ ] **Step 5: Run tests**

Run:
- `pytest -q code/tests/test_request_type.py`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add code/agent/types.py code/agent/determinism.py code/agent/io_csv.py code/tests/test_request_type.py
git commit -m "chore: add types and strict CSV I/O"
```

---

## Task 3: Text normalization (robust query formation)

**Files:**
- Create: `code/agent/text_norm.py`
- Test: `code/tests/test_text_norm.py`

- [ ] **Step 1: Implement `code/agent/text_norm.py`**

```python
from __future__ import annotations

import re


_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("\u00a0", " ")
    text = _WS.sub(" ", text)
    return text


def build_query(subject: str, issue: str) -> str:
    s = normalize(subject)
    i = normalize(issue)
    if s and i and s.lower() not in i.lower():
        return f"{s}\n{i}"
    return i or s
```

- [ ] **Step 2: Add tests**

Create `code/tests/test_text_norm.py`:

```python
from agent.text_norm import build_query, normalize


def test_normalize_collapses_whitespace():
    assert normalize("a \n  b") == "a b"


def test_build_query_prefers_issue_and_includes_subject_when_distinct():
    q = build_query("Subject here", "Issue body")
    assert "Subject here" in q and "Issue body" in q
```

- [ ] **Step 3: Run tests**

Run:
- `pytest -q code/tests/test_text_norm.py`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add code/agent/text_norm.py code/tests/test_text_norm.py
git commit -m "chore: add text normalization utilities"
```

---

## Task 4: Corpus loader + chunking (stable, reproducible)

**Files:**
- Create: `code/agent/corpus_loader.py`
- Create: `code/agent/chunking.py`
- Create: `code/agent/cache_paths.py`

- [ ] **Step 1: Implement cache directory resolution**

Create `code/agent/cache_paths.py`:

```python
from __future__ import annotations

import os
from pathlib import Path


def get_cache_dir() -> Path:
    localapp = os.environ.get("LOCALAPPDATA")
    if localapp:
        return Path(localapp) / "hackerrank_orchestrate" / "cache"
    return Path.home() / ".cache" / "hackerrank_orchestrate"
```

- [ ] **Step 2: Implement chunking**

Create `code/agent/chunking.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str


def chunk_text(text: str, max_chars: int = 2500, overlap_chars: int = 400) -> list[Chunk]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: list[Chunk] = []
    start = 0
    n = len(text)
    i = 0
    while start < n:
        end = min(n, start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(Chunk(chunk_id=f"c{i}", text=chunk))
            i += 1
        if end >= n:
            break
        start = max(0, end - overlap_chars)
    return chunks
```

- [ ] **Step 3: Implement corpus loader**

Create `code/agent/corpus_loader.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chunking import chunk_text


@dataclass(frozen=True)
class CorpusChunk:
    company: str
    doc_path: str
    chunk_id: str
    text: str


def infer_company_from_path(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    if "data" in parts:
        idx = parts.index("data")
        if idx + 1 < len(parts):
            top = parts[idx + 1]
            if top in {"hackerrank", "claude", "visa"}:
                return {"hackerrank": "HackerRank", "claude": "Claude", "visa": "Visa"}[top]
    return "None"


def load_corpus(repo_root: Path) -> list[CorpusChunk]:
    data_dir = repo_root / "data"
    chunks: list[CorpusChunk] = []
    for md in sorted(data_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="ignore")
        company = infer_company_from_path(md)
        for ch in chunk_text(text):
            chunks.append(
                CorpusChunk(
                    company=company,
                    doc_path=str(md.as_posix()),
                    chunk_id=ch.chunk_id,
                    text=ch.text,
                )
            )
    return chunks
```

- [ ] **Step 4: Commit**

```bash
git add code/agent/cache_paths.py code/agent/chunking.py code/agent/corpus_loader.py
git commit -m "feat: add corpus loader and deterministic chunking"
```

---

## Task 5: BM25 index + retrieval (offline baseline)

**Files:**
- Create: `code/agent/bm25_index.py`
- Create: `code/agent/retriever.py`
- Test: `code/tests/test_bm25_retrieval_smoke.py`

- [ ] **Step 1: Implement tokenizer and BM25 builder**

Create `code/agent/bm25_index.py`:

```python
from __future__ import annotations

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from .determinism import stable_sort_key


_TOK = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOK.finditer(text or "")]


@dataclass(frozen=True)
class BM25Index:
    bm25: BM25Okapi
    tokenized: list[list[str]]


def build_bm25_index(texts: list[str]) -> BM25Index:
    tokenized = [tokenize(t) for t in texts]
    bm25 = BM25Okapi(tokenized)
    return BM25Index(bm25=bm25, tokenized=tokenized)


def bm25_scores(index: BM25Index, query: str) -> list[float]:
    q = tokenize(query)
    return list(index.bm25.get_scores(q))


def topk_indices(scores: list[float], k: int) -> list[int]:
    items = [(i, s) for i, s in enumerate(scores)]
    items.sort(key=lambda x: stable_sort_key(-x[1], x[0]))
    return [i for i, _ in items[:k]]
```

- [ ] **Step 2: Implement retriever over corpus chunks**

Create `code/agent/retriever.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bm25_index import BM25Index, bm25_scores, build_bm25_index, topk_indices
from .corpus_loader import CorpusChunk, load_corpus
from .types import EvidenceChunk


@dataclass(frozen=True)
class RetrieverState:
    corpus: list[CorpusChunk]
    index: BM25Index


def build_retriever(repo_root: Path) -> RetrieverState:
    corpus = load_corpus(repo_root)
    index = build_bm25_index([c.text for c in corpus])
    return RetrieverState(corpus=corpus, index=index)


def retrieve(state: RetrieverState, query: str, company: str, k: int) -> list[EvidenceChunk]:
    scores = bm25_scores(state.index, query)
    idxs = topk_indices(scores, k=min(max(k * 3, 15), len(scores)))
    out: list[EvidenceChunk] = []
    for i in idxs:
        c = state.corpus[i]
        if company != "None" and c.company != company:
            continue
        out.append(
            EvidenceChunk(
                doc_path=c.doc_path,
                chunk_id=c.chunk_id,
                text=c.text,
                bm25_score=float(scores[i]),
            )
        )
        if len(out) >= k:
            break
    return out
```

- [ ] **Step 3: Add smoke test that retrieval returns at least one chunk**

Create `code/tests/test_bm25_retrieval_smoke.py`:

```python
from pathlib import Path

from agent.retriever import build_retriever, retrieve


def test_retrieval_smoke_returns_results():
    repo_root = Path(__file__).resolve().parents[2]
    state = build_retriever(repo_root)
    ev = retrieve(state, "assessment invite candidate", "HackerRank", k=3)
    assert len(ev) >= 1
    assert ev[0].doc_path.startswith("data/")
```

- [ ] **Step 4: Run smoke test**

Run:
- `pytest -q code/tests/test_bm25_retrieval_smoke.py`

Expected: PASS (may take some seconds to load corpus first time)

- [ ] **Step 5: Commit**

```bash
git add code/agent/bm25_index.py code/agent/retriever.py code/tests/test_bm25_retrieval_smoke.py
git commit -m "feat: add BM25 retrieval baseline"
```

---

## Task 6: Safety gate (hard/soft escalation)

**Files:**
- Create: `code/agent/safety.py`
- Test: `code/tests/test_safety.py`

- [ ] **Step 1: Implement risk detection**

Create `code/agent/safety.py`:

```python
from __future__ import annotations

import re


HIGH_RISK_PATTERNS = [
    re.compile(r"\bfraud\b", re.I),
    re.compile(r"\bscam\b", re.I),
    re.compile(r"\bchargeback\b", re.I),
    re.compile(r"\bstolen\b.*\bcard\b", re.I),
    re.compile(r"\baccount\b.*\block(ed)?\b", re.I),
    re.compile(r"\bcan[’']?t\s+login\b", re.I),
    re.compile(r"\bhacked\b", re.I),
    re.compile(r"\bpassword\b", re.I),
    re.compile(r"\bOTP\b", re.I),
    re.compile(r"\b2FA\b", re.I),
    re.compile(r"\bAPI\s*key\b.*\b(compromised|leak|stolen)\b", re.I),
]


def is_high_risk(text: str) -> bool:
    t = text or ""
    return any(p.search(t) for p in HIGH_RISK_PATTERNS)
```

- [ ] **Step 2: Add tests**

Create `code/tests/test_safety.py`:

```python
from agent.safety import is_high_risk


def test_detects_fraud():
    assert is_high_risk("I think this is fraud on my card")


def test_detects_account_lockout():
    assert is_high_risk("My account is locked and I can't login")


def test_low_risk_example():
    assert not is_high_risk("How do I invite a candidate to an assessment?")
```

- [ ] **Step 3: Run tests**

Run:
- `pytest -q code/tests/test_safety.py`

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add code/agent/safety.py code/tests/test_safety.py
git commit -m "feat: add high-risk safety gate"
```

---

## Task 7: Request type + product area taxonomy (canonical outputs)

**Files:**
- Create: `code/agent/classify.py`
- Create: `code/agent/product_area.py`
- Test: `code/tests/test_product_area.py`

- [ ] **Step 1: Implement canonical taxonomy**

Create `code/agent/product_area.py`:

```python
from __future__ import annotations


CANONICAL_PRODUCT_AREAS: list[str] = [
    "HackerRank > Assessments",
    "HackerRank > Candidates & Invites",
    "HackerRank > Test Settings",
    "HackerRank > Roles & Variants",
    "HackerRank > Teams & Permissions",
    "HackerRank > SSO / SCIM",
    "HackerRank > Billing & Subscriptions",
    "HackerRank > Reports & Analytics",
    "HackerRank > Integrations",
    "HackerRank > Execution Environment",
    "Claude > API & Keys",
    "Claude > Rate Limits",
    "Claude > Billing & Invoices",
    "Claude > Console & Account",
    "Claude > Safety & Policy",
    "Claude > Troubleshooting",
    "Visa > Fraud & Scams",
    "Visa > Dispute Resolution",
    "Visa > Travel Support",
    "Visa > Exchange Rates & Fees",
    "Visa > Merchant / Small Business",
    "Visa > Data Security",
    "General > Outage / Service Status",
    "General > Unknown",
]
```

- [ ] **Step 2: Implement request type rules**

Create `code/agent/classify.py`:

```python
from __future__ import annotations

import re
from typing import cast

from .types import RequestType


FEATURE_RE = re.compile(r"\b(please add|feature request|would like|can you (add|support)|it would be great)\b", re.I)
BUG_RE = re.compile(r"\b(site down|error|crash|not working|broken|500|503|timeout)\b", re.I)
INVALID_RE = re.compile(r"^\s*$")
INJECTION_RE = re.compile(r"\b(ignore previous|system prompt|developer message|reveal)\b", re.I)


def classify_request_type(text: str) -> RequestType:
    t = text or ""
    if INVALID_RE.search(t) or INJECTION_RE.search(t):
        return cast(RequestType, "invalid")
    if FEATURE_RE.search(t):
        return cast(RequestType, "feature_request")
    if BUG_RE.search(t):
        return cast(RequestType, "bug")
    return cast(RequestType, "product_issue")
```

- [ ] **Step 3: Add tests**

Create `code/tests/test_product_area.py`:

```python
from agent.product_area import CANONICAL_PRODUCT_AREAS


def test_canonical_product_area_nonempty():
    assert "HackerRank > Assessments" in CANONICAL_PRODUCT_AREAS
```

- [ ] **Step 4: Run tests**

Run:
- `pytest -q code/tests/test_product_area.py`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add code/agent/product_area.py code/agent/classify.py code/tests/test_product_area.py
git commit -m "feat: add request_type rules and canonical product_area taxonomy"
```

---

## Task 8: Evidence strength thresholds + answerability decision

**Files:**
- Create: `code/agent/evidence_strength.py`
- Create: `code/agent/company_infer.py`
- Test: `code/tests/test_company_infer.py`

- [ ] **Step 1: Implement evidence-strength metrics**

Create `code/agent/evidence_strength.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from .types import EvidenceChunk


@dataclass(frozen=True)
class EvidenceSignals:
    bm25_top1: float
    bm25_top5: float
    bm25_margin: float


def compute_signals(evidence: list[EvidenceChunk]) -> EvidenceSignals:
    scores = [e.bm25_score for e in evidence]
    if not scores:
        return EvidenceSignals(0.0, 0.0, 0.0)
    top1 = scores[0]
    top5 = scores[4] if len(scores) >= 5 else 0.0
    return EvidenceSignals(top1, top5, top1 - top5)
```

- [ ] **Step 2: Implement deterministic company inference for company=None**

Create `code/agent/company_infer.py`:

```python
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyVote:
    hackerrank: float
    claude: float
    visa: float


HR_RE = re.compile(r"\b(assessment|candidate|test|invite|hackerrank)\b", re.I)
CL_RE = re.compile(r"\b(claude|api key|anthropic|rate limit)\b", re.I)
VI_RE = re.compile(r"\b(visa|card|merchant|chargeback|dispute)\b", re.I)


def keyword_company_hint(text: str) -> str | None:
    if HR_RE.search(text):
        return "HackerRank"
    if CL_RE.search(text):
        return "Claude"
    if VI_RE.search(text):
        return "Visa"
    return None
```

- [ ] **Step 3: Add tests**

Create `code/tests/test_company_infer.py`:

```python
from agent.company_infer import keyword_company_hint


def test_keyword_hint_hackerrank():
    assert keyword_company_hint("candidate invite assessment") == "HackerRank"


def test_keyword_hint_claude():
    assert keyword_company_hint("API key rate limit") == "Claude"
```

- [ ] **Step 4: Run tests**

Run:
- `pytest -q code/tests/test_company_infer.py`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add code/agent/evidence_strength.py code/agent/company_infer.py code/tests/test_company_infer.py
git commit -m "feat: add evidence signals and company hinting"
```

---

## Task 9: Offline response composer + justification with evidence paths

**Files:**
- Create: `code/agent/compose_offline.py`

- [ ] **Step 1: Implement offline composer**

Create `code/agent/compose_offline.py`:

```python
from __future__ import annotations

from .types import EvidenceChunk


def build_justification(reason: str, evidence: list[EvidenceChunk]) -> str:
    paths = []
    for e in evidence[:3]:
        if e.doc_path not in paths:
            paths.append(e.doc_path)
    return f"{reason} evidence=[{', '.join(paths)}]"


def build_offline_response(query: str, evidence: list[EvidenceChunk], status: str) -> str:
    if status == "escalated":
        return (
            "I’m escalating this to a human support agent because it may be sensitive or "
            "the provided documentation doesn’t clearly cover it. "
            "If you can, include any non-sensitive details like the exact error message and when it occurred."
        )
    # replied
    if not evidence:
        return (
            "I couldn’t find supporting documentation for this in the provided corpus. "
            "I recommend escalating this to a human support agent for confirmation."
        )
    snippet = evidence[0].text.strip().splitlines()[:6]
    snippet_text = "\n".join(snippet).strip()
    return (
        "Based on the provided support documentation, here are the most relevant steps:\n\n"
        f"{snippet_text}\n\n"
        "If this doesn’t resolve the issue, escalate to a human agent with the context above."
    )
```

- [ ] **Step 2: Commit**

```bash
git add code/agent/compose_offline.py
git commit -m "feat: add offline response composer with evidence justification"
```

---

## Task 10: Pipeline integration (end-to-end offline baseline)

**Files:**
- Create: `code/agent/pipeline.py`
- Modify: `code/main.py`
- Create: `code/__init__.py` (optional empty)
- Create: `code/agent/__init__.py` (optional empty)
- Test: `code/tests/test_pipeline_sample_rows.py`

- [ ] **Step 1: Implement pipeline**

Create `code/agent/pipeline.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .classify import classify_request_type
from .compose_offline import build_justification, build_offline_response
from .retriever import RetrieverState, build_retriever, retrieve
from .safety import is_high_risk
from .text_norm import build_query
from .types import PipelineConfig, TicketIn, TriageOut


@dataclass(frozen=True)
class AgentState:
    retriever: RetrieverState


def build_state(repo_root: Path, cfg: PipelineConfig) -> AgentState:
    return AgentState(retriever=build_retriever(repo_root))


def triage_one(state: AgentState, t: TicketIn, cfg: PipelineConfig) -> TriageOut:
    query = build_query(t.subject, t.issue)
    req_type = classify_request_type(query)

    if req_type == "invalid":
        return TriageOut(
            status="replied",
            product_area="General > Unknown",
            response="I can’t help with that request. Please provide a support question related to HackerRank, Claude, or Visa.",
            justification="Classified as invalid/non-actionable. evidence=[]",
            request_type=req_type,
        )

    if is_high_risk(query):
        return TriageOut(
            status="escalated",
            product_area="General > Unknown",
            response=build_offline_response(query, [], status="escalated"),
            justification="Escalated due to high-risk/sensitive intent. evidence=[]",
            request_type=req_type,
        )

    company = t.company if t.company in {"HackerRank", "Claude", "Visa"} else "None"
    evidence = retrieve(state.retriever, query, company=company, k=cfg.topk)

    if not evidence:
        return TriageOut(
            status="replied",
            product_area="General > Unknown",
            response=build_offline_response(query, evidence, status="replied"),
            justification="No supporting documentation found in provided corpus. evidence=[]",
            request_type=req_type,
        )

    response = build_offline_response(query, evidence, status="replied")
    justification = build_justification("Replied with steps supported by retrieved documentation.", evidence)
    return TriageOut(
        status="replied",
        product_area="General > Unknown",
        response=response,
        justification=justification,
        request_type=req_type,
    )
```

- [ ] **Step 2: Wire pipeline into `code/main.py`**

Replace the body of `main()` with:

```python
from pathlib import Path

from agent.io_csv import read_tickets, write_outputs
from agent.pipeline import build_state, triage_one
from agent.types import PipelineConfig


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    cfg = PipelineConfig(
        topk=args.topk,
        enable_online=bool(args.enable_online),
        no_llm=bool(args.no_llm),
        rebuild_index=bool(args.rebuild_index),
    )
    state = build_state(repo_root, cfg)
    tickets = read_tickets(args.input)
    rows = [triage_one(state, t, cfg) for t in tickets]
    write_outputs(args.output, rows)
    return 0
```

Also ensure Python can import `agent` by creating empty package markers:
- `code/agent/__init__.py`
- optionally `code/__init__.py`

- [ ] **Step 3: Add pipeline test using first 2 sample rows**

Create `code/tests/test_pipeline_sample_rows.py`:

```python
from pathlib import Path

from agent.io_csv import read_tickets
from agent.pipeline import build_state, triage_one
from agent.types import PipelineConfig


def test_pipeline_runs_on_sample_csv_first_rows():
    repo_root = Path(__file__).resolve().parents[2]
    cfg = PipelineConfig(topk=5)
    state = build_state(repo_root, cfg)
    sample = repo_root / "support_tickets" / "sample_support_tickets.csv"
    tickets = read_tickets(sample)[:2]
    outs = [triage_one(state, t, cfg) for t in tickets]
    assert len(outs) == 2
    assert outs[0].status in {"replied", "escalated"}
    assert outs[0].request_type in {"product_issue", "feature_request", "bug", "invalid"}
```

- [ ] **Step 4: Run tests**

Run:
- `pytest -q code/tests/test_pipeline_sample_rows.py`

Expected: PASS

- [ ] **Step 5: Run full agent**

Run:
- `python code/main.py`

Expected:
- `support_tickets/output.csv` populated with one row per input ticket, with required columns.

- [ ] **Step 6: Commit**

```bash
git add code/agent/pipeline.py code/main.py code/tests/test_pipeline_sample_rows.py code/agent/__init__.py
git commit -m "feat: integrate offline pipeline end-to-end"
```

---

## Task 11: Deterministic thresholds + company inference by retrieval vote + product_area mapping

**Files:**
- Modify: `code/agent/pipeline.py`
- Extend: `code/agent/product_area.py`
- Modify: `code/agent/retriever.py` (optional)
- Extend: `code/tests/test_product_area.py`

- [ ] **Step 1: Add thresholds constants (fixed after tuning)**

Add to `code/agent/evidence_strength.py`:

```python
T_NOHIT = 0.2
T_WEAK = 0.7
T_MARGIN = 0.1
T_REPLY = 0.9
T_MARGIN_REPLY = 0.15
T_COMPANY_MARGIN = 0.3
```

- [ ] **Step 2: Implement retrieval-vote company inference**

Extend `code/agent/company_infer.py` with:

```python
from agent.types import EvidenceChunk


def company_vote_from_evidence(evidence: list[EvidenceChunk]) -> dict[str, float]:
    votes = {"HackerRank": 0.0, "Claude": 0.0, "Visa": 0.0}
    for e in evidence:
        p = e.doc_path.lower()
        if p.startswith("data/hackerrank/"):
            votes["HackerRank"] += e.bm25_score
        elif p.startswith("data/claude/"):
            votes["Claude"] += e.bm25_score
        elif p.startswith("data/visa/"):
            votes["Visa"] += e.bm25_score
    return votes
```

- [ ] **Step 3: Implement deterministic product_area mapping**

Extend `code/agent/product_area.py` with keyword-based mapping:

```python
def infer_product_area(company: str, query: str, evidence_paths: list[str]) -> str:
    q = (query or "").lower()

    if "site down" in q or "503" in q or "500" in q:
        return "General > Outage / Service Status"

    if company == "HackerRank":
        if "sso" in q or "scim" in q:
            return "HackerRank > SSO / SCIM"
        if "candidate" in q or "invite" in q:
            return "HackerRank > Candidates & Invites"
        if "variant" in q:
            return "HackerRank > Roles & Variants"
        return "HackerRank > Assessments"

    if company == "Claude":
        if "rate limit" in q:
            return "Claude > Rate Limits"
        if "invoice" in q or "billing" in q:
            return "Claude > Billing & Invoices"
        return "Claude > API & Keys"

    if company == "Visa":
        if "dispute" in q or "chargeback" in q:
            return "Visa > Dispute Resolution"
        if "fraud" in q or "scam" in q:
            return "Visa > Fraud & Scams"
        return "Visa > Travel Support"

    return "General > Unknown"
```

- [ ] **Step 4: Update pipeline to use thresholds + mapping**

In `triage_one`, after retrieval, compute `EvidenceSignals` and decide reply/escalate accordingly; set `product_area` via `infer_product_area`.

- [ ] **Step 5: Add tests ensuring product_area is always canonical**

Extend `code/tests/test_product_area.py`:

```python
from agent.product_area import CANONICAL_PRODUCT_AREAS, infer_product_area


def test_infer_product_area_returns_canonical_value():
    pa = infer_product_area("HackerRank", "invite candidate", ["data/hackerrank/x.md"])
    assert pa in CANONICAL_PRODUCT_AREAS
```

- [ ] **Step 6: Run tests + commit**

```bash
pytest -q code/tests
git add code/agent/evidence_strength.py code/agent/company_infer.py code/agent/product_area.py code/agent/pipeline.py code/tests/test_product_area.py
git commit -m "feat: add thresholds, company vote, and canonical product_area mapping"
```

---

## Task 12: Online upgrades (opt-in): embeddings rerank + grounded writer + grounding validator

**Files:**
- Create: `code/agent/compose_online.py`
- Create: `code/agent/grounding_validator.py`
- Modify: `code/agent/pipeline.py`

- [ ] **Step 1: Implement grounding validator**

Create `code/agent/grounding_validator.py`:

```python
from __future__ import annotations

import re

from .types import EvidenceChunk


_STEP_LINE = re.compile(r"^\s*(\d+[\).\s]|-)\s+")


def extract_step_lines(text: str) -> list[str]:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return [ln for ln in lines if _STEP_LINE.search(ln)]


def lexical_overlap_ok(step: str, evidence_text: str, min_hits: int = 3) -> bool:
    toks = [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", step)]
    if len(toks) < min_hits:
        return True
    ev = evidence_text.lower()
    hits = sum(1 for t in set(toks) if t in ev)
    return hits >= min_hits


def validate_grounding(response: str, evidence: list[EvidenceChunk]) -> bool:
    steps = extract_step_lines(response)
    if not steps:
        return True
    joined = "\n".join(e.text for e in evidence[:6])
    for s in steps:
        if "escalat" in s.lower():
            continue
        if not lexical_overlap_ok(s, joined):
            return False
    return True
```

- [ ] **Step 2: Implement online composer (only when enabled)**

Create `code/agent/compose_online.py` with provider auto-detect:

```python
from __future__ import annotations

import os

from .types import EvidenceChunk


def can_enable_online() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))


def compose_with_llm(query: str, evidence: list[EvidenceChunk]) -> str:
    raise NotImplementedError("Online composer not implemented yet.")
```

- [ ] **Step 3: Wire into pipeline behind `--enable-online`**

In pipeline: only call online composer if:
- `cfg.enable_online` is True
- keys exist
- and the grounding validator passes; else fallback to offline.

- [ ] **Step 4: Commit**

```bash
git add code/agent/grounding_validator.py code/agent/compose_online.py code/agent/pipeline.py
git commit -m "feat: add opt-in online writer hooks with grounding validator"
```

---

## Task 13: Evaluation harness + threshold tuning (one-time, then freeze)

**Files:**
- Create: `code/eval.py`

- [ ] **Step 1: Implement eval runner**

Create `code/eval.py`:

```python
from __future__ import annotations

from pathlib import Path

from agent.io_csv import read_tickets
from agent.pipeline import build_state, triage_one
from agent.types import PipelineConfig


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    cfg = PipelineConfig(topk=8)
    state = build_state(repo_root, cfg)
    sample = repo_root / "support_tickets" / "sample_support_tickets.csv"
    tickets = read_tickets(sample)
    outs = [triage_one(state, t, cfg) for t in tickets]
    print(f"Ran {len(outs)} sample rows.")
    print("Manual review: inspect a few outputs for grounding and safety.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run eval**

Run:
- `python code/eval.py`

Expected: prints `Ran N sample rows.`

- [ ] **Step 3: Freeze thresholds**

After tuning thresholds once, update constants in `code/agent/evidence_strength.py` and do not change further.

- [ ] **Step 4: Commit**

```bash
git add code/eval.py code/agent/evidence_strength.py
git commit -m "chore: add evaluation harness and freeze thresholds"
```

---

## Final submission run

- [ ] **Step 1: Run agent on full tickets**

Run:
- `python code/main.py`

Expected:
- `support_tickets/output.csv` written with one row per input ticket and required columns/allowed values.

- [ ] **Step 2: Sanity-check the output**

Check:
- only `replied`/`escalated` in `status`
- only allowed request types
- `justification` includes `evidence=[...]` where applicable
- no requests for secrets/PII in responses

---

## Self-review checklist (run after writing plan)

1) **Spec coverage:** This plan covers offline deterministic baseline, BM25 retrieval, safety/escalation, canonical product_area, justification evidence paths, and optional opt-in online upgrades with a grounding validator.  
2) **Placeholder scan:** Online writer raises `NotImplementedError` until implemented in Task 12 (explicitly scoped).  
3) **Type consistency:** The plan uses the same allowed enums and output columns throughout.
