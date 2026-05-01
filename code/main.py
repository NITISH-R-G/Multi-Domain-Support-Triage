"""Offline-grounded support triage agent — entry point."""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from config import DATA_DIR, INPUT_CSV, OUTPUT_CSV, SEED, TOP_K
from openai_agent import decide_with_openai, fallback_from_hits
from postprocess import finalize_decision
from retrieve import BM25Index, CACHE_PATH, rerank_hits, should_escalate_low_retrieval
from risk import assess_risk
from taxonomy import looks_like_invalid_small_talk

random.seed(SEED)
np.random.seed(SEED)


def _normalize_company(val: Any) -> str | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s or s.lower() == "none":
        return None
    return s


def _brand_for_search(company: str | None, issue: str, subject: str, index: BM25Index) -> str:
    if company:
        m = company.strip().lower()
        if m == "hackerrank":
            return "hackerrank"
        if m == "claude":
            return "claude"
        if m == "visa":
            return "visa"
    return index.infer_brand(f"{subject}\n{issue}")


def _validate_row(d: dict[str, Any]) -> dict[str, Any]:
    status = str(d.get("status", "escalated")).lower()
    if status not in ("replied", "escalated"):
        status = "escalated"
    rt = str(d.get("request_type", "product_issue")).lower()
    if rt not in ("product_issue", "feature_request", "bug", "invalid"):
        rt = "product_issue"
    out = {
        "status": status,
        "product_area": str(d.get("product_area", "") or ""),
        "response": str(d.get("response", "") or ""),
        "justification": str(d.get("justification", "") or ""),
        "request_type": rt,
    }
    return out


def process_row(row: pd.Series, index: BM25Index) -> dict[str, Any]:
    issue = str(row.get("Issue", "") or "")
    subject = str(row.get("Subject", "") or "")
    company_raw = row.get("Company")

    company = _normalize_company(company_raw)
    brand = _brand_for_search(company, issue, subject, index)

    # Fast invalid handling (spam / gratitude / off-topic trivia).
    if looks_like_invalid_small_talk(subject, issue):
        decision = finalize_decision(
            brand=brand,
            issue=issue,
            subject=subject,
            hits=[],
            decision={
                "status": "replied",
                "product_area": "",
                "response": "I’m sorry, this is out of scope from my capabilities.",
                "justification": "Detected off-topic/invalid request.",
                "request_type": "invalid",
            },
            low_retrieval=False,
        )
        return _validate_row(decision)

    hit = assess_risk(issue, subject)
    if hit:
        fb = fallback_from_hits([], escalated=True, esc_reason=hit.reason, low_retrieval=False)
        if hit.force_request_type:
            fb["request_type"] = hit.force_request_type
        return _validate_row(fb)

    hits, raw_top_score = index.search(f"{subject}\n{issue}", brand, TOP_K)
    hits = rerank_hits(f"{subject}\n{issue}", hits)
    low = should_escalate_low_retrieval(raw_top_score)

    decision = decide_with_openai(
        issue,
        subject,
        company_raw if company_raw is not None and not pd.isna(company_raw) else "None",
        hits,
        force_escalate_reason=None,
        low_retrieval=low,
    )
    decision = finalize_decision(
        brand=brand,
        issue=issue,
        subject=subject,
        hits=hits,
        decision=decision,
        low_retrieval=low,
    )
    return _validate_row(decision)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-domain support triage agent (Orchestrate)")
    parser.add_argument("--input", type=str, default=str(INPUT_CSV))
    parser.add_argument("--output", type=str, default=str(OUTPUT_CSV))
    parser.add_argument("--limit", type=int, default=0, help="Process only first N rows (debug)")
    args = parser.parse_args()

    inp = Path(args.input)
    out_p = Path(args.output)

    df = pd.read_csv(inp, encoding="utf-8")
    if args.limit > 0:
        df = df.head(args.limit)

    index = BM25Index.load(CACHE_PATH, DATA_DIR)

    rows_out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        pred = process_row(row, index)
        rows_out.append(
            {
                "issue": row.get("Issue", ""),
                "subject": row.get("Subject", ""),
                "company": row.get("Company", ""),
                "response": pred["response"],
                "product_area": pred["product_area"],
                "status": pred["status"],
                "request_type": pred["request_type"],
                "justification": pred["justification"],
            }
        )

    out_df = pd.DataFrame(rows_out)
    out_df.to_csv(out_p, index=False, encoding="utf-8")
    print(f"Wrote {len(out_df)} rows to {out_p}", file=sys.stderr)


if __name__ == "__main__":
    main()
