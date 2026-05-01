"""Cross-ecosystem escalation: multi-brand tickets should route to humans."""
from __future__ import annotations

import os

import pytest

from cross_ecosystem import cross_ecosystem_escalation_reason


def test_no_escalation_single_brand_hackerrank() -> None:
    r = cross_ecosystem_escalation_reason(
        "How do I add a candidate to a test?",
        "Invites",
    )
    assert r is None


def test_escalation_hackerrank_plus_claude() -> None:
    r = cross_ecosystem_escalation_reason(
        "My HackerRank test errored and I also cannot log in to Claude Pro.",
        "Multi product",
    )
    assert r is not None
    assert "HackerRank + Claude" in (r or "")


def test_escalation_claude_plus_visa_card() -> None:
    r = cross_ecosystem_escalation_reason(
        "Claude logged me out and my Visa card was charged twice today.",
        "Billing",
    )
    assert r is not None


def test_no_false_positive_visa_sponsorship_only_hackerrank() -> None:
    """Immigration 'visa' language without Visa-network product signals."""
    r = cross_ecosystem_escalation_reason(
        "Does HackerRank sponsor work visas for onsite interviews?",
        "HR policy",
    )
    assert r is None


def test_disable_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORCHESTRATE_DISABLE_CROSS_ECOSYSTEM_ESCALATE", "1")
    # reload module to pick up env... cross_ecosystem reads env at call time, not import
    r = cross_ecosystem_escalation_reason(
        "HackerRank and Claude issues combined.",
        "x",
    )
    assert r is None
