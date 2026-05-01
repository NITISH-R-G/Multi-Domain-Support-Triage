"""Shared CSV loading and schema validation for ticket pipelines."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_KEYS = frozenset({"issue", "subject", "company"})


class TicketCsvError(ValueError):
    """User-fixable CSV / path issues (exit code 2)."""


def read_tickets_csv(path: Path | str, *, label: str = "CSV") -> pd.DataFrame:
    """Read UTF-8 / UTF-8-BOM; raise clear errors for missing path or encoding."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"{label} not found: {p}")
    last_err: UnicodeDecodeError | None = None
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return pd.read_csv(p, encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
            continue
        except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
            raise TicketCsvError(f"{label} could not be parsed as CSV ({p}): {e}") from e
    assert last_err is not None
    raise TicketCsvError(
        f"{label} is not valid UTF-8 (or UTF-8 with BOM). Save the file as UTF-8 and retry. ({p})"
    ) from last_err


def rename_prediction_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Case-insensitive rename of agent output columns to Pred_* names for gold merges."""
    lower = {str(c).strip().lower(): c for c in df.columns}
    renames: dict[str, str] = {}
    for key, new in (
        ("response", "Pred_Response"),
        ("product_area", "Pred_Product Area"),
        ("status", "Pred_Status"),
        ("request_type", "Pred_Request Type"),
        ("justification", "Pred_Justification"),
    ):
        if key in lower:
            renames[lower[key]] = new
    return df.rename(columns=renames)


def canonicalize_ticket_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Issue / Subject / Company column names (case-insensitive)."""
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    missing = sorted(REQUIRED_KEYS - set(lower_map.keys()))
    if missing:
        raise TicketCsvError(
            f"Missing required columns {missing}. Need Issue, Subject, Company (any casing). "
            f"Found columns: {list(df.columns)}"
        )
    rename = {
        lower_map["issue"]: "Issue",
        lower_map["subject"]: "Subject",
        lower_map["company"]: "Company",
    }
    return df.rename(columns=rename)
