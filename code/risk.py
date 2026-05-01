"""High-risk and policy-based escalation heuristics."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskHit:
    reason: str


_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Prompt injection / exfiltration
    (
        re.compile(
            r"(display|show|reveal|dump)\s+(.{0,40})?(internal|rules|documents|logic|prompt)",
            re.I | re.S,
        ),
        "requests disclosure of internal rules or logic",
    ),
    (
        re.compile(r"\bexact\s+(logic|rules|prompt)\b", re.I),
        "requests exact internal decision logic",
    ),
    # Payments / disputes demanding outcomes (policy-sensitive)
    (
        re.compile(r"\b(ban\s+the\s+seller|refund\s+me\s+today|make\s+visa\s+refund)", re.I),
        "demands irreversible payment or merchant enforcement action",
    ),
    (
        re.compile(r"\b(unfair|graded\s+me\s+unfair|increase\s+my\s+score|review\s+my\s+answers)\b", re.I),
        "grading dispute / outcome manipulation request",
    ),
    # Malicious intent
    (
        re.compile(r"\b(delete\s+all\s+files|format\s+the\s+disk|ransomware)\b", re.I),
        "malicious or destructive intent",
    ),
    (
        re.compile(r"\b(exploit|zero[- ]day|sql\s+injection)\b", re.I),
        "security exploit discussion",
    ),
]


def assess_risk(issue: str, subject: str) -> RiskHit | None:
    blob = f"{subject}\n{issue}".strip()
    for rx, reason in _PATTERNS:
        if rx.search(blob):
            return RiskHit(reason=reason)
    return None
