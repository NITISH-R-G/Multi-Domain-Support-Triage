from __future__ import annotations

from ticket_hints import ticket_may_span_multiple_topics


def test_also_triggers() -> None:
    t = "How do I log in? Also, my billing looks wrong for last month."
    assert ticket_may_span_multiple_topics(t)


def test_single_question_false() -> None:
    assert not ticket_may_span_multiple_topics("Where do I change my email address?")
