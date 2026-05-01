"""Lightweight ticket shape helpers (multi-topic detection + optional justification note)."""
from __future__ import annotations

import re
from typing import Any


_MULTI_NOTE = "Ticket may include multiple topics; this reply addresses the primary request."


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


def maybe_append_multi_topic_justification(
    decision: dict[str, Any],
    *,
    issue: str,
    subject: str,
) -> dict[str, Any]:
    """Append a transparency note to justification only (does not change response body)."""
    if str(decision.get("status", "")).lower() != "replied":
        return decision
    blob = f"{subject}\n{issue}"
    if not ticket_may_span_multiple_topics(blob):
        return decision
    j = str(decision.get("justification", "") or "")
    if _MULTI_NOTE in j:
        return decision
    out = dict(decision)
    out["justification"] = f"{j}; {_MULTI_NOTE}".strip("; ")
    return out
