"""BM25 retrieval over offline corpus chunks."""
from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from rank_bm25 import BM25Okapi

from config import CACHE_DIR, CACHE_PATH, DATA_DIR, LOW_BM25_THRESHOLD, TOP_K
from corpus import Chunk, load_chunks, tokenize


Brand = Literal["hackerrank", "claude", "visa", "any"]


@dataclass
class Retrieved:
    chunk: Chunk
    score: float


class BM25Index:
    def __init__(self, chunks: list[Chunk], bm25: BM25Okapi, doc_tokens: list[list[str]]) -> None:
        self.chunks = chunks
        self.bm25 = bm25
        self.doc_tokens = doc_tokens
        self._brand_mask = {b: np.array([c.brand == b for c in chunks], dtype=bool) for b in ("hackerrank", "claude", "visa")}

    @classmethod
    def build(cls, data_dir: Path) -> BM25Index:
        chunks = load_chunks(data_dir)
        doc_tokens = [tokenize(f"{c.title} {' '.join(c.breadcrumbs)} {c.text}") for c in chunks]
        bm25 = BM25Okapi(doc_tokens)
        return cls(chunks, bm25, doc_tokens)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump({"chunks": self.chunks, "doc_tokens": self.doc_tokens}, f)

    @classmethod
    def load(cls, path: Path, data_dir: Path) -> BM25Index:
        if not path.is_file():
            idx = cls.build(data_dir)
            idx.save(path)
            return idx
        with path.open("rb") as f:
            blob = pickle.load(f)
        chunks: list[Chunk] = blob["chunks"]
        doc_tokens: list[list[str]] = blob["doc_tokens"]
        bm25 = BM25Okapi(doc_tokens)
        return cls(chunks, bm25, doc_tokens)

    def infer_brand(self, query: str) -> str:
        q = tokenize(query)
        scores = self.bm25.get_scores(q)
        best: tuple[str, float] = ("hackerrank", -1.0)
        for brand in ("hackerrank", "claude", "visa"):
            mask = self._brand_mask[brand]
            if not mask.any():
                continue
            mx = float(np.max(np.where(mask, scores, -1e9)))
            if mx > best[1]:
                best = (brand, mx)
        return best[0]

    def search(self, query: str, brand: Brand, top_k: int = TOP_K) -> tuple[list[Retrieved], float]:
        q = tokenize(query)
        scores = np.array(self.bm25.get_scores(q), dtype=float)
        if brand != "any":
            mask = self._brand_mask[brand]
            scores = np.where(mask, scores, -1.0)
        order = np.argsort(scores)[::-1][:top_k]
        rel = max(float(scores[order[0]]), 0.0) if len(order) else 0.0
        out = [Retrieved(self.chunks[int(i)], float(scores[int(i)])) for i in order if scores[int(i)] > 0]
        return out, rel


def rerank_hits(query: str, hits: list[Retrieved]) -> list[Retrieved]:
    """Lexical overlap rerank on top of BM25 scores."""
    if not hits:
        return hits
    qset = set(tokenize(query))
    scored: list[tuple[float, Retrieved]] = []
    for h in hits:
        c = h.chunk
        bag = tokenize(c.title + " " + " ".join(c.breadcrumbs) + " " + c.text[:1500])
        overlap = len(qset.intersection(set(bag)))
        bonus = 0.0
        ql = query.lower()
        if "team" in ql and "team" in c.text.lower():
            bonus += 5
        if "workspace" in ql and "workspace" in c.text.lower():
            bonus += 5
        if "visa" in ql and c.brand == "visa":
            bonus += 3
        if "hackerrank" in ql and c.brand == "hackerrank":
            bonus += 3
        if "claude" in ql and c.brand == "claude":
            bonus += 3
        combined = h.score + overlap * 1.2 + bonus
        scored.append((combined, Retrieved(chunk=c, score=combined)))
    scored.sort(key=lambda x: -x[0])
    return [x[1] for x in scored]


def format_context(hits: list[Retrieved]) -> str:
    blocks = []
    for h in hits:
        c = h.chunk
        crumbs = " > ".join(c.breadcrumbs) if c.breadcrumbs else ""
        blocks.append(
            f"[score={h.score:.2f} brand={c.brand} path={c.path}]\n"
            f"Title: {c.title}\n"
            f"Breadcrumbs: {crumbs}\n"
            f"---\n{c.text[:6000]}"
        )
    return "\n\n".join(blocks)


def should_escalate_low_retrieval(top_score: float) -> bool:
    return top_score < LOW_BM25_THRESHOLD
