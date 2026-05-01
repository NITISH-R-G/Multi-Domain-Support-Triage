from __future__ import annotations

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from csv_io import (
    TicketCsvError,
    canonicalize_ticket_columns,
    read_tickets_csv,
    rename_prediction_columns,
)


def test_canonicalize_case_insensitive() -> None:
    df = pd.DataFrame(
        {
            "issue": ["a"],
            "SUBJECT": ["b"],
            "Company": ["HackerRank"],
        }
    )
    out = canonicalize_ticket_columns(df)
    assert list(out.columns[:3]) == ["Issue", "Subject", "Company"]


def test_canonicalize_missing_column() -> None:
    df = pd.DataFrame({"issue": [1]})
    with pytest.raises(TicketCsvError, match="Missing required"):
        canonicalize_ticket_columns(df)


def test_read_roundtrip_utf8_bom(tmp_path: Path) -> None:
    p = tmp_path / "t.csv"
    p.write_text(
        textwrap.dedent(
            """\
            Issue,Subject,Company
            a,b,Claude
            """
        ),
        encoding="utf-8-sig",
    )
    df = read_tickets_csv(p, label="t")
    assert len(df) == 1


def test_rename_prediction_columns() -> None:
    df = pd.DataFrame(
        {
            "Issue": [1],
            "Subject": [2],
            "Company": [3],
            "response": ["hi"],
            "STATUS": ["replied"],
        }
    )
    df2 = rename_prediction_columns(df)
    assert "Pred_Response" in df2.columns
    assert "Pred_Status" in df2.columns
