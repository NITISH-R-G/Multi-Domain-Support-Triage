"""Lightweight ticket shape helpers (documentation + tests; no default behavior change)."""
from __future__ import annotations

import re


def ticket_may_span_multiple_topics(text: str) -> bool:
    """Heuristic: message might bundle several distinct asks (no NLP; best-effort)."""
    t = (text or "").strip()
    if len(t) < 50:
        return False
    if re.search(r"\b(also|another question|second (issue|question)|in addition|additionally)\b", t, re.I):
        return True
    if t.count("?") >= 2 and len(t) > 100:
        return True
    if re.search(r"(?m)^\s*\d+[\).]\s+.+", t):
        return True
    return False
