"""Cheap text metrics for regression checks against labeled sample CSVs."""
from __future__ import annotations

import re
from collections import Counter


def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def token_set_f1(reference: str, hypothesis: str) -> float:
    """Token-overlap F1 (bag of words; labels normalized)."""
    def _tok(x: str) -> set[str]:
        return {t for t in re.findall(r"[a-z0-9]+", x.lower()) if len(t) > 1}

    r = _tok(reference)
    h = _tok(hypothesis)
    if not r and not h:
        return 1.0
    if not r or not h:
        return 0.0
    inter = len(r & h)
    prec = inter / len(h) if h else 0.0
    rec = inter / len(r) if r else 0.0
    if prec + rec <= 0:
        return 0.0
    return 2.0 * prec * rec / (prec + rec)


def compact_overlap_ratio(a: str, b: str) -> float:
    """Dice-like overlap on character bags (cheap fuzzy signal vs exact match)."""
    ca = re.sub(r"\s+", "", (a or "").lower())
    cb = re.sub(r"\s+", "", (b or "").lower())
    if not ca or not cb:
        return 0.0
    sa, sb = Counter(ca), Counter(cb)
    inter = sum((sa & sb).values())
    return 2.0 * inter / (len(ca) + len(cb))
