"""Hybrid offline retrieval: BM25 candidate generation + TF-IDF cosine reranking."""
from __future__ import annotations

import math
import pickle
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from rank_bm25 import BM25Okapi

from config import (
    BM25_WEIGHT,
    CACHE_PATH,
    DATA_DIR,
    HYBRID_CANDIDATES,
    INDEX_VERSION,
    LOW_BM25_THRESHOLD,
    RERANK_BONUS_BRAND,
    RERANK_BONUS_TEAM,
    RERANK_BONUS_WORKSPACE,
    TFIDF_WEIGHT,
    TOP_K,
)
from corpus import Chunk, load_chunks, tokenize


Brand = Literal["hackerrank", "claude", "visa", "any"]


@dataclass
class Retrieved:
    chunk: Chunk
    score: float


def _tfidf_vectors(doc_tokens: list[list[str]]) -> tuple[list[dict[str, float]], list[float], dict[str, float]]:
    """Tiny TF-IDF implementation (no sklearn), cosine-normalized per doc."""
    n_docs = len(doc_tokens)
    df: Counter[str] = Counter()
    tfs: list[Counter[str]] = []
    for toks in doc_tokens:
        tf = Counter(toks)
        tfs.append(tf)
        df.update(set(tf.keys()))

    idf: dict[str, float] = {}
    for term, dfi in df.items():
        # sklearn-ish idf smoothing
        idf[term] = math.log((1.0 + n_docs) / (1.0 + float(dfi))) + 1.0

    vecs: list[dict[str, float]] = []
    norms: list[float] = []
    for tf in tfs:
        w: dict[str, float] = {}
        for term, freq in tf.items():
            # sublinear tf scaling
            tfidf = (1.0 + math.log(float(freq))) * idf.get(term, 0.0)
            if tfidf > 0:
                w[term] = float(tfidf)
        nrm = math.sqrt(sum(v * v for v in w.values())) or 1.0
        wn = {t: (val / nrm) for t, val in w.items()}
        vecs.append(wn)
        norms.append(nrm)
    return vecs, norms, idf


def _cosine_tfidf(q_terms: list[str], doc_vec: dict[str, float], q_idf: dict[str, float]) -> float:
    # normalize query vector similarly to docs
    qw: dict[str, float] = {}
    tf = Counter(q_terms)
    for term, freq in tf.items():
        if term not in q_idf:
            continue
        qw[term] = (1.0 + math.log(float(freq))) * q_idf[term]
    nrm = math.sqrt(sum(v * v for v in qw.values())) or 1.0
    qn = {t: (val / nrm) for t, val in qw.items()}

    # dot product on intersection
    if not qn or not doc_vec:
        return 0.0
    s = 0.0
    for t, qv in qn.items():
        dv = doc_vec.get(t)
        if dv is not None:
            s += qv * dv
    return float(s)


class HybridIndex:
    def __init__(
        self,
        chunks: list[Chunk],
        bm25: BM25Okapi,
        doc_tokens: list[list[str]],
        tfidf_docs: list[dict[str, float]],
        idf: dict[str, float],
    ) -> None:
        self.chunks = chunks
        self.bm25 = bm25
        self.doc_tokens = doc_tokens
        self.tfidf_docs = tfidf_docs
        self.idf = idf
        self._brand_mask = {b: np.array([c.brand == b for c in chunks], dtype=bool) for b in ("hackerrank", "claude", "visa")}

    @classmethod
    def build(cls, data_dir: Path) -> HybridIndex:
        chunks = load_chunks(data_dir)
        doc_tokens = [tokenize(f"{c.title} {' '.join(c.breadcrumbs)} {c.text}") for c in chunks]
        bm25 = BM25Okapi(doc_tokens)

        tfidf_docs, _norms, idf = _tfidf_vectors(doc_tokens)
        return cls(chunks, bm25, doc_tokens, tfidf_docs, idf)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(
                {
                    "v": INDEX_VERSION,
                    "chunks": self.chunks,
                    "doc_tokens": self.doc_tokens,
                    "tfidf_docs": self.tfidf_docs,
                    "idf": self.idf,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path, data_dir: Path) -> HybridIndex:
        if not path.is_file():
            idx = cls.build(data_dir)
            idx.save(path)
            return idx
        with path.open("rb") as f:
            blob = pickle.load(f)
        if not isinstance(blob, dict) or blob.get("v") != INDEX_VERSION:
            idx = cls.build(data_dir)
            idx.save(path)
            return idx

        chunks: list[Chunk] = blob["chunks"]
        doc_tokens: list[list[str]] = blob["doc_tokens"]
        tfidf_docs: list[dict[str, float]] = blob["tfidf_docs"]
        idf: dict[str, float] = blob["idf"]
        bm25 = BM25Okapi(doc_tokens)
        return cls(chunks, bm25, doc_tokens, tfidf_docs, idf)

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
        q_tok = tokenize(query)
        bm25_scores = np.array(self.bm25.get_scores(q_tok), dtype=float)
        if brand != "any":
            mask = self._brand_mask[brand]
            bm25_scores = np.where(mask, bm25_scores, -1.0)

        cand_k = min(HYBRID_CANDIDATES, len(self.chunks))
        cand_idx = np.argsort(bm25_scores)[::-1][:cand_k]
        raw_top = float(bm25_scores[cand_idx[0]]) if len(cand_idx) else 0.0

        if len(cand_idx) == 0:
            return [], raw_top

        sims = np.zeros(len(cand_idx), dtype=float)
        for j, gi in enumerate(cand_idx):
            sims[j] = _cosine_tfidf(q_tok, self.tfidf_docs[int(gi)], self.idf)
        b = bm25_scores[cand_idx]
        b_norm = (b - float(np.min(b))) / max(1e-6, float(np.max(b) - np.min(b)))
        fused = BM25_WEIGHT * b_norm + TFIDF_WEIGHT * sims

        order_local = np.argsort(fused)[::-1][:top_k]
        out: list[Retrieved] = []
        for li in order_local:
            gi = int(cand_idx[int(li)])
            out.append(Retrieved(self.chunks[gi], float(fused[int(li)])))

        return out, raw_top


# Backwards-compatible export name used by main.py
BM25Index = HybridIndex


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
        ct = c.text.lower()
        if "team" in ql and "team" in ct:
            bonus += RERANK_BONUS_TEAM
        if "workspace" in ql and "workspace" in ct:
            bonus += RERANK_BONUS_WORKSPACE
        if "visa" in ql and c.brand == "visa":
            bonus += RERANK_BONUS_BRAND
        if "hackerrank" in ql and c.brand == "hackerrank":
            bonus += RERANK_BONUS_BRAND
        if "claude" in ql and c.brand == "claude":
            bonus += RERANK_BONUS_BRAND
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
