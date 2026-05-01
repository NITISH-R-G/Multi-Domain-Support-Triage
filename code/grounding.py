"""Cheap grounding checks: ensure responses don't drift far from retrieved evidence."""
from __future__ import annotations

import re

from corpus import tokenize
from retrieve import Retrieved


_STOP = {
    "the",
    "and",
    "or",
    "a",
    "an",
    "to",
    "of",
    "in",
    "for",
    "on",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "with",
    "your",
    "you",
    "we",
    "our",
    "this",
    "that",
    "it",
    "if",
    "not",
}


def _norm_words(text: str) -> list[str]:
    return [w for w in tokenize(text) if w not in _STOP and len(w) > 2]


def lexical_overlap(response: str, hits: list[Retrieved]) -> float:
    """Return fraction of non-trivial response tokens present in retrieved chunk text."""
    if not hits:
        return 0.0
    rw = _norm_words(response)
    if not rw:
        return 1.0
    bag: set[str] = set()
    for h in hits[:4]:
        bag.update(_norm_words(h.chunk.text[:8000]))
        bag.update(_norm_words(" ".join(h.chunk.breadcrumbs)))
        bag.update(_norm_words(h.chunk.title))
    hits_ct = sum(1 for w in rw if w in bag)
    return hits_ct / max(1, len(rw))


def has_unsupported_numbers(response: str, hits: list[Retrieved]) -> bool:
    """Flag digit-heavy claims not present in evidence (rough guardrail)."""
    ctx = "\n".join(h.chunk.text[:8000] for h in hits[:4])
    ctx_compact = re.sub(r"\s+", "", ctx)
    for m in re.finditer(r"\d[\d\-\s().+]{5,}\d", response):
        frag = re.sub(r"\s+", "", m.group(0))
        if frag and frag not in ctx_compact:
            # Avoid false positives on standalone years (4 digits) and short codes.
            digit_chars = re.sub(r"\D+", "", frag)
            if len(digit_chars) < 7:
                continue
            return True
    return False
