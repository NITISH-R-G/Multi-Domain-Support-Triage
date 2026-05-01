"""Canonical labels + mapping from retrieved corpus evidence to evaluator-friendly areas."""
from __future__ import annotations

import re
from dataclasses import dataclass

from corpus import Chunk

# Canonical labels shared across brands (must stay stable for CSV evaluation).
CANONICAL_PRODUCT_AREAS: tuple[str, ...] = (
    "screen",
    "community",
    "privacy",
    "travel_support",
    "general_support",
    "conversation_management",
)


@dataclass(frozen=True)
class LabelRule:
    label: str
    brand: str | None  # None = any
    path_rx: re.Pattern[str] | None = None
    text_rx: re.Pattern[str] | None = None


def _rx(pat: str, flags: int = re.I) -> re.Pattern[str]:
    return re.compile(pat, flags)


RULES: list[LabelRule] = [
    # HackerRank — broad "product UI / workflows" bucket used heavily in sample as `screen`
    LabelRule("screen", "hackerrank", _rx(r"(^|/)hackerrank/(?!hackerrank_community/)")),
    LabelRule("community", "hackerrank", _rx(r"/hackerrank_community/|/community/")),
    LabelRule("community", "hackerrank", _rx(r"\b(community account|hackerrank community)\b")),
    # Claude privacy / conversations
    LabelRule("privacy", "claude", _rx(r"/privacy\.|/privacy/|privacy\.claude|safeguard")),
    LabelRule("privacy", "claude", _rx(r"\b(delete|remove)\b.*\b(conversation|chat)\b")),
    LabelRule("privacy", "claude", _rx(r"\b(temporary chat|private)\b")),
    # Visa — travel vs general support
    LabelRule("travel_support", "visa", _rx(r"traveller|traveler|travel\-support|travel_support|exchange rate|exchange\-rate")),
    LabelRule("general_support", "visa", _rx(r"lost|stolen|block|card|emergency|customer assistance|gcas|dispute|merchant")),
]


def infer_request_type(issue: str, subject: str) -> str | None:
    blob = f"{subject}\n{issue}".lower()
    # Long tickets may include "Thanks," signatures — don't classify as invalid solely due to that.
    if len(blob) < 170 and re.search(r"\b(thank you for helping(\s+me)?|thanks for helping|thank you so much)\b", blob):
        return "invalid"
    if looks_like_invalid_small_talk(subject, issue):
        return "invalid"
    if re.search(r"\bsite\b.*\bdown\b|\b503\b|\berror\b.*\bpage\b|\bnot accessible\b", blob):
        return "bug"
    if re.search(r"\bfeature request\b|\bplease add\b|\bcan you implement\b|\bnew feature\b", blob):
        return "feature_request"
    return None


def looks_like_off_topic_general_knowledge(subject: str, issue: str) -> bool:
    """Entertainment / trivia / general-knowledge questions unlikely to be product support."""
    blob = f"{subject}\n{issue}".strip()
    if len(blob) > 260:
        return False
    low = blob.lower()
    return bool(
        re.search(
            r"\b(who played|name of the actor|which actor|actor in\b|"
            r"actor in (a |the )?(movie|film)|"
            r"what movie (won|is)|which film (won|is)|oscar for best (picture|actor))\b",
            low,
        )
    )


def looks_like_invalid_small_talk(subject: str, issue: str) -> bool:
    blob = f"{subject}\n{issue}".strip()
    low = blob.lower()
    if len(blob) < 160 and re.search(r"^\s*(thanks|thank you|thx|ty)\b", low):
        return True
    if len(blob) < 160 and re.search(r"\bthank you for helping\b", low):
        return True
    if len(blob) < 140 and re.fullmatch(r"\s*(thank you for helping me|thanks for helping|thank you so much)\s*\.?\s*", low):
        return True
    if looks_like_off_topic_general_knowledge(subject, issue):
        return True
    return False


def map_product_area(brand: str, issue: str, subject: str, top: Chunk | None) -> str:
    """Map evidence to one of CANONICAL_PRODUCT_AREAS when possible."""
    blob = f"{subject}\n{issue}".lower()
    path = (top.path if top else "").replace("\\", "/").lower()

    # Highest priority: brand-specific intent inferred from the ticket itself (beats noisy retrieval paths).
    if brand == "visa":
        # Traveller's cheques are categorized as travel support even if stolen/lost appears in the message.
        if re.search(r"\btraveller|traveler|cheque\b", blob):
            return "travel_support"
        if re.search(r"\blost\b|\bstolen\b|\bblock\b|\bcard\b|\bgcas\b|\bemergency\b|\breport\b|\bindia\b", blob):
            return "general_support"
        if re.search(r"\btravel\b", blob):
            return "travel_support"
        return "general_support"

    # Explicit routing by corpus location/topic rules
    if top:
        for rule in RULES:
            if rule.brand and rule.brand != brand:
                continue
            if rule.path_rx and rule.path_rx.search(path):
                return rule.label
            hay = f"{top.title}\n{path}\n{top.text[:1200]}".lower()
            if rule.text_rx and rule.text_rx.search(hay):
                return rule.label

    # Claude defaults
    if brand == "claude":
        if re.search(r"\bprivacy\b|\bconversation\b|\bdelete\b", blob):
            return "privacy"
        return "conversation_management"

    # HackerRank defaults (most FAQ-like articles align to sample's `screen`)
    if brand == "hackerrank":
        if "community" in blob or "hackerrank community" in blob:
            return "community"
        return "screen"

    return "conversation_management"


def normalize_product_area(raw: str, brand: str, issue: str, subject: str, top: Chunk | None) -> str:
    s = (raw or "").strip().lower()
    if s in CANONICAL_PRODUCT_AREAS:
        return s
    return map_product_area(brand, issue, subject, top)
