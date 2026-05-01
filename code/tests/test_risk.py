from __future__ import annotations

from risk import assess_risk


def test_grading_dispute_escalation_signal() -> None:
    hit = assess_risk("You graded me unfair on the last contest", "Contest")
    assert hit is not None
    assert "grading" in hit.reason.lower() or "dispute" in hit.reason.lower()


def test_normal_question_no_hit() -> None:
    assert assess_risk("How do I invite a candidate to a test?", "") is None
