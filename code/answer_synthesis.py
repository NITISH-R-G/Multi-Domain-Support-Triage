"""Offline answer shaping: convert retrieved markdown-ish text into short actionable guidance."""
from __future__ import annotations

import re

from retrieve import Retrieved


_BULLET_LINE = re.compile(r"(?m)^\s*(?:[-*•]|\d+\.)\s+(.*)$")

# Lines that usually aren't helpful as user-facing steps.
_NOISE_PREFIXES = (
    "last updated:",
    "_last updated",
    "note:",
    "important:",
    "warning:",
)


def _clean_line(line: str) -> str:
    s = line.strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _strip_heading_noise(text: str) -> str:
    # Remove markdown headings but keep their content lines handled separately.
    text = re.sub(r"(?m)^#+\s+.*$", "", text)
    return text


def extract_steps(text: str, *, max_steps: int = 8, max_chars_per_step: int = 260) -> list[str]:
    """Pull readable steps from support article bodies."""
    text = _strip_heading_noise(text)
    lines = [ln.rstrip() for ln in text.splitlines()]
    steps: list[str] = []

    # Prefer explicit bullets/numbered lists.
    for ln in lines:
        m = _BULLET_LINE.match(ln.strip())
        if not m:
            continue
        step = _clean_line(m.group(1))
        if not step:
            continue
        low = step.lower()
        if any(low.startswith(p) for p in _NOISE_PREFIXES):
            continue
        if len(step) > max_chars_per_step:
            step = step[: max_chars_per_step - 1] + "…"
        steps.append(step)
        if len(steps) >= max_steps:
            break

    # Fallback: split long paragraphs into sentences if no bullets exist.
    if not steps:
        blob = _clean_line(re.sub(r"\s+", " ", text))
        # naive sentence split (good enough for hackathon corpus text)
        parts = re.split(r"(?<=[.!?])\s+", blob)
        for p in parts:
            p = _clean_line(p)
            if len(p) < 40:
                continue
            low = p.lower()
            if any(low.startswith(pref) for pref in _NOISE_PREFIXES):
                continue
            if len(p) > max_chars_per_step:
                p = p[: max_chars_per_step - 1] + "…"
            steps.append(p)
            if len(steps) >= max_steps:
                break

    return steps[:max_steps]


def synthesize_reply_from_hits(hits: list[Retrieved], *, max_sources: int = 2) -> tuple[str, list[str]]:
    """Return (user_response, source_paths_used)."""
    if not hits:
        return "", []

    sources: list[str] = []
    blocks: list[str] = []

    for h in hits[:max_sources]:
        c = h.chunk
        sources.append(c.path)
        title = c.title.strip()
        steps = extract_steps(c.text)
        if not steps:
            # last resort small excerpt
            excerpt = re.sub(r"\s+", " ", c.text).strip()
            excerpt = excerpt[:700] + ("…" if len(excerpt) > 700 else "")
            blocks.append(f"From {title}:\n{excerpt}")
            continue

        rendered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
        blocks.append(f"From {title}:\n{rendered}")

    body = "\n\n".join(blocks).strip()
    body += "\n\nIf anything still doesn’t match what you’re seeing, please reach out via the official support channel for your product."
    return body, sources
