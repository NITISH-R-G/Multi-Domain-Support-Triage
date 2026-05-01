"""Post-processing decisions for taxonomy alignment + grounding checks."""
from __future__ import annotations

import re
from typing import Any

from grounding import has_unsupported_numbers, lexical_overlap
from retrieve import Retrieved
from taxonomy import (
    infer_request_type,
    normalize_product_area,
)


def finalize_decision(
    *,
    brand: str,
    issue: str,
    subject: str,
    hits: list[Retrieved],
    decision: dict[str, Any],
    low_retrieval: bool,
) -> dict[str, Any]:
    status = str(decision.get("status", "replied")).lower()
    rt = str(decision.get("request_type", "product_issue")).lower()

    inferred = infer_request_type(issue, subject)
    if inferred and status != "escalated":
        rt = inferred

    top = hits[0].chunk if hits else None
    if rt == "invalid":
        blob = f"{subject}\n{issue}".strip().lower()
        # Sample taxonomy: pure gratitude uses blank product_area; trivia/off-topic uses conversation_management.
        if re.search(r"\b(thank you for helping|thanks for helping|thank you so much)\b", blob) and len(blob) < 160:
            pa = ""
        else:
            pa = "conversation_management"
    else:
        pa = normalize_product_area(str(decision.get("product_area", "")), brand, issue, subject, top)

    resp = str(decision.get("response", "") or "")
    if status == "replied" and hits:
        ov = lexical_overlap(resp, hits)
        if ov < 0.18 or has_unsupported_numbers(resp, hits):
            # Lazy import avoids import cycles with openai_agent <-> postprocess.
            from openai_agent import fallback_from_hits

            fb = fallback_from_hits(hits, escalated=False, esc_reason=None, low_retrieval=low_retrieval)
            fb["request_type"] = rt if rt in ("product_issue", "feature_request", "bug", "invalid") else fb["request_type"]
            fb["product_area"] = normalize_product_area(fb.get("product_area", ""), brand, issue, subject, top)
            return fb

    out = dict(decision)
    out["product_area"] = pa
    out["request_type"] = rt
    return out
