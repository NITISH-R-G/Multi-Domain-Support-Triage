"""Golden routing assertions vs bundled sample_support_tickets.csv (offline LLM)."""
from __future__ import annotations

import os

import pandas as pd
import pytest

from config import REPO_ROOT
from csv_io import canonicalize_ticket_columns, read_tickets_csv
from main import process_row

SAMPLE_PATH = REPO_ROOT / "support_tickets" / "sample_support_tickets.csv"


def _norm_status(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip().lower()
    if s in {"replied", "reply"}:
        return "replied"
    if s in {"escalated", "escalate"}:
        return "escalated"
    return s


def _norm_rt(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x).strip().lower()


def _norm_pa(x: object) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    return str(x).strip().lower()


@pytest.fixture
def offline_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORCHESTRATE_DISABLE_LLM", "1")


def test_sample_support_routing_matches_golden(bm25_index_session: object, offline_llm: None) -> None:
    """Every sample row: status, request_type, product_area must match labels when LLM is disabled."""
    df = read_tickets_csv(SAMPLE_PATH, label="sample")
    df = canonicalize_ticket_columns(df)
    assert len(df) >= 1

    for idx, row in df.iterrows():
        pred = process_row(row, bm25_index_session)
        gold_st = _norm_status(row.get("Status"))
        gold_rt = _norm_rt(row.get("Request Type"))
        gold_pa = _norm_pa(row.get("Product Area"))

        pr_st = _norm_status(pred.get("status"))
        pr_rt = _norm_rt(pred.get("request_type"))
        pr_pa = _norm_pa(pred.get("product_area"))

        assert pr_st == gold_st, (
            f"row idx={idx} status pred={pr_st!r} gold={gold_st!r} "
            f"subject={str(row.get('Subject'))[:80]!r}"
        )
        assert pr_rt == gold_rt, (
            f"row idx={idx} request_type pred={pr_rt!r} gold={gold_rt!r} "
            f"subject={str(row.get('Subject'))[:80]!r}"
        )
        assert pr_pa == gold_pa, (
            f"row idx={idx} product_area pred={pr_pa!r} gold={gold_pa!r} "
            f"subject={str(row.get('Subject'))[:80]!r}"
        )
