"""Grounded LLM decisioning with strict JSON outputs."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Literal

from pathlib import Path

from dotenv import load_dotenv

from answer_synthesis import synthesize_reply_from_hits
from config import OPENAI_MODEL
from retrieve import Retrieved, format_context

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

Status = Literal["replied", "escalated"]
RequestType = Literal["product_issue", "feature_request", "bug", "invalid"]


def _slug_area(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_]+", "_", s)
    return s[:max_len].strip("_") or "general_support"


def fallback_from_hits(
    hits: list[Retrieved],
    *,
    escalated: bool,
    esc_reason: str | None,
    low_retrieval: bool,
) -> dict[str, Any]:
    if escalated:
        return {
            "status": "escalated",
            "product_area": "",
            "response": "This request needs to be reviewed by a human specialist. Please contact official support through the appropriate channel for your product.",
            "justification": esc_reason or "Escalated per policy.",
            "request_type": "product_issue",
        }
    if not hits:
        return {
            "status": "escalated",
            "product_area": "",
            "response": "We could not locate matching guidance in the offline support library for this request.",
            "justification": "No retrieval hits above threshold." + (" Low retrieval scores." if low_retrieval else ""),
            "request_type": "product_issue",
        }
    top = hits[0].chunk
    crumbs = list(top.breadcrumbs)
    area_src = crumbs[-1] if crumbs else top.title
    product_area = _slug_area(area_src)
    reply, srcs = synthesize_reply_from_hits(hits)
    return {
        "status": "replied",
        "product_area": product_area,
        "response": reply,
        "justification": (
            f"Offline synthesis from {top.path} (retrieval score={hits[0].score:.2f}). "
            f"Sources: {', '.join(srcs[:3])}"
        ),
        "request_type": "product_issue",
    }


SCHEMA_HINT = """Respond with a single JSON object only (no markdown), keys exactly:
{"status":"replied"|"escalated","product_area":"string","response":"string","justification":"string","request_type":"product_issue"|"feature_request"|"bug"|"invalid"}
Rules:
- status=escalated for fraud, legal threats, account takeover, grading disputes, bug bounty reports needing security team, or when CONTEXT lacks needed facts.
- product_area: short snake_case like sample outputs (e.g. screen, community, privacy, travel_support). Prefer last breadcrumb or doc topic from CONTEXT.
- request_type: bug if outage/errors; feature_request for new capability; invalid for spam/thanks/off-topic; else product_issue.
- response: concise, user-facing, only facts supported by CONTEXT. If status=replied, no fabricated steps.
- response length: keep it short (aim <= 180 words). Use numbered steps when possible.
- justification: include 1-3 source article titles or paths from CONTEXT you relied on.
"""


def decide_with_openai(
    issue: str,
    subject: str,
    company_line: str,
    hits: list[Retrieved],
    *,
    force_escalate_reason: str | None,
    low_retrieval: bool,
) -> dict[str, Any]:
    # Allow forcing offline-only mode even if OPENAI_API_KEY exists.
    if os.environ.get("ORCHESTRATE_DISABLE_LLM", "").strip().lower() in {"1", "true", "yes", "y"}:
        return fallback_from_hits(
            hits,
            escalated=bool(force_escalate_reason) or low_retrieval,
            esc_reason=force_escalate_reason,
            low_retrieval=low_retrieval,
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return fallback_from_hits(
            hits,
            escalated=bool(force_escalate_reason) or low_retrieval,
            esc_reason=force_escalate_reason,
            low_retrieval=low_retrieval,
        )

    # Import only when needed so offline mode doesn't emit OpenAI/Pydantic warnings on newer Python versions.
    from openai import OpenAI  # type: ignore

    ctx = format_context(hits) if hits else "(no retrieval context)"
    user = f"""Company field from ticket (may be wrong or None): {company_line!r}

Subject: {subject}

Issue:
{issue}

Retrieved CONTEXT (authoritative; do not contradict):
{ctx}

Notes:
- If force_escalate_reason is set, you MUST set status to escalated and explain briefly.
- force_escalate_reason: {force_escalate_reason!r}
- low_retrieval_flag: {low_retrieval}

Writing constraints:
- Prefer actionable numbered steps.
- Do NOT invent URLs/phone numbers/policy details not present in CONTEXT.
- If CONTEXT doesn't contain enough detail to answer safely, set status=escalated.
"""

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.1,
            seed=42,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SCHEMA_HINT},
                {"role": "user", "content": user},
            ],
        )
        raw = resp.choices[0].message.content or "{}"
    except Exception as e:
        # Never fail the whole run due to transient API issues (rate limit/quota/network).
        msg = f"LLM call failed ({type(e).__name__}). Falling back to offline answer."
        return fallback_from_hits(
            hits,
            escalated=bool(force_escalate_reason) or low_retrieval,
            esc_reason=(force_escalate_reason or msg),
            low_retrieval=low_retrieval,
        )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Prefer escalation when we already lack confidence in retrieval context.
        escalate = bool(low_retrieval) or not hits
        out = fallback_from_hits(
            hits,
            escalated=escalate,
            esc_reason=("LLM produced invalid JSON; escalating for human review." if escalate else None),
            low_retrieval=low_retrieval,
        )
        if not escalate:
            prev = str(out.get("justification", "") or "")
            out["justification"] = f"LLM produced invalid JSON; using offline synthesis. {prev}".strip()
        return out

    for key in ("status", "product_area", "response", "justification", "request_type"):
        data.setdefault(key, "")
    if force_escalate_reason:
        data["status"] = "escalated"
        data["justification"] = f"{force_escalate_reason}; {data.get('justification','')}".strip("; ")
    if low_retrieval and data.get("status") == "replied" and not hits:
        data["status"] = "escalated"
        data["justification"] = (f"Low retrieval confidence; {data.get('justification', '')}").strip()
    return data
