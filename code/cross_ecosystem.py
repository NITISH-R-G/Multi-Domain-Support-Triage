"""Detect tickets that span multiple distinct product ecosystems — safer to escalate than guess one answer."""
from __future__ import annotations

import os
import re


def cross_ecosystem_escalation_reason(issue: str, subject: str) -> str | None:
    """Return human-readable escalate reason, or None.

    Conservative pairwise checks avoid false positives such as "HackerRank visa sponsorship"
    (mentions Visa immigration language without Visa-the-network product context).
    Disable entirely with ``ORCHESTRATE_DISABLE_CROSS_ECOSYSTEM_ESCALATE=1``.
    """
    if os.environ.get("ORCHESTRATE_DISABLE_CROSS_ECOSYSTEM_ESCALATE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }:
        return None

    blob = f"{subject}\n{issue}".strip()
    low = blob.lower()

    has_hr = bool(re.search(r"\bhackerrank\b", low))
    has_claude = bool(re.search(r"\bclaude\b|\banthropic\b", low))
    # Visa Inc. product context (cards/travel/payment), not generic immigration "visa".
    has_visa_financial = bool(
        re.search(r"\bvisa\b", low)
        and re.search(
            r"\b(card|cards|credit|debit|cheque|cheques|gcas|lost|stolen|"
            r"traveller|traveler|payment|pin|atm|fraud|chargeback)\b",
            low,
        )
    )

    tags: list[str] = []
    if has_hr and has_claude:
        tags.append("HackerRank + Claude/Anthropic")
    if has_hr and has_visa_financial:
        tags.append("HackerRank + Visa payment/travel")
    if has_claude and has_visa_financial:
        tags.append("Claude + Visa payment/travel")

    if not tags:
        return None
    return (
        "Multiple distinct product ecosystems in one ticket ("
        + "; ".join(tags)
        + "); escalating for human routing."
    )
