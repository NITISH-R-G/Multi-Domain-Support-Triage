from __future__ import annotations

from ticket_hints import maybe_append_multi_topic_justification, ticket_may_span_multiple_topics


def test_also_triggers() -> None:
    t = "How do I log in? Also, my billing looks wrong for last month."
    assert ticket_may_span_multiple_topics(t)


def test_single_question_false() -> None:
    assert not ticket_may_span_multiple_topics("Where do I change my email address?")


def test_maybe_append_adds_note_when_multi_topic() -> None:
    issue = (
        "When should I create a variant versus a different test? "
        "What are the advantages and disadvantages of using variants?"
    )
    d = {
        "status": "replied",
        "justification": "Based on community docs.",
        "response": "Hello",
    }
    out = maybe_append_multi_topic_justification(d, issue=issue, subject="Variants")
    assert "multiple topics" in out["justification"].lower()


def test_maybe_append_skips_escalated() -> None:
    d = {"status": "escalated", "justification": "Risk"}
    assert maybe_append_multi_topic_justification(
        d,
        issue="Also tell me about billing? Second question here?",
        subject="x",
    ) == d
