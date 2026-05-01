"""High-risk and policy-based escalation heuristics."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskHit:
    reason: str
    force_request_type: str | None = None


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
    # Broad outages — usually needs human incident handling.
    (
        re.compile(
            r"\b(site|website)\s+is\s+down\b|\bnone\s+of\s+the\s+pages\b|\b(all\s+requests|requests)\s+are\s+failing\b|\bstopped\s+working\s+completely\b",
            re.I,
        ),
        "possible widespread outage",
    ),
    # Fraud/identity theft and vulnerability reports.
    (
        re.compile(r"\bidentity\s+(?:has\s+been\s+)?stolen\b|\bidentity\s+theft\b", re.I),
        "identity theft / fraud-sensitive",
    ),
    (
        re.compile(r"\b(security\s+vulnerability|bug\s+bounty)\b", re.I),
        "security vulnerability disclosure — needs specialist routing",
    ),
    (
        re.compile(r"\b(i will sue|lawsuit|legal action|my lawyer)\b", re.I),
        "legal threat — route to specialist handling",
    ),
    (
        re.compile(r"\b(harm myself|kill myself|suicide)\b", re.I),
        "self-harm mention — escalated for human crisis routing",
    ),
]


def assess_risk(issue: str, subject: str) -> RiskHit | None:
    blob = f"{subject}\n{issue}".strip()
    for rx, reason in _PATTERNS:
        if rx.search(blob):
            if reason == "possible widespread outage":
                return RiskHit(reason=reason, force_request_type="bug")
            return RiskHit(reason=reason)
    return None
