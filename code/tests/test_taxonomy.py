from __future__ import annotations

from taxonomy import (
    looks_like_off_topic_general_knowledge,
    looks_like_invalid_small_talk,
    map_product_area,
)
from corpus import Chunk


def test_off_topic_movie_trivia_detected() -> None:
    assert looks_like_off_topic_general_knowledge(
        "Urgent, please help",
        "What is the name of the actor in Iron Man?",
    )


def test_support_question_not_off_topic() -> None:
    assert not looks_like_off_topic_general_knowledge(
        "Password",
        "How do I reset my password on HackerRank?",
    )


def test_thanks_short_invalid() -> None:
    assert looks_like_invalid_small_talk("Thanks", "Thank you for helping me.")


def test_visa_travel_from_blob() -> None:
    ch = Chunk(
        chunk_id=1,
        brand="visa",
        path="visa/travel/foo.md",
        title="Travel",
        breadcrumbs=("Visa", "Travel"),
        text="Exchange rates for travellers",
    )
    assert (
        map_product_area(
            "visa",
            "I need exchange rates for traveller cheques",
            "Travel",
            ch,
        )
        == "travel_support"
    )
