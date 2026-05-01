from __future__ import annotations

from eval_metrics import compact_overlap_ratio, normalize_text, token_set_f1


def test_token_f1_identical() -> None:
    assert token_set_f1("reset your password in settings", "reset your password in settings") == 1.0


def test_token_f1_partial() -> None:
    s = token_set_f1("hello world support", "hello support team")
    assert 0.2 < s < 0.99


def test_normalize_collapses_space() -> None:
    assert normalize_text("  A  B  ") == "a b"


def test_compact_overlap() -> None:
    assert compact_overlap_ratio("abc", "abc") == 1.0
    assert compact_overlap_ratio("", "x") == 0.0
