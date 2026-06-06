"""Shared pytest fixtures (session-scoped retrieval index)."""
from __future__ import annotations

import pytest

from config import CACHE_PATH, DATA_DIR
from retrieve import BM25Index


@pytest.fixture(scope="session")
def bm25_index_session() -> BM25Index:
    if not DATA_DIR.is_dir():
        pytest.skip(f"Corpus missing: {DATA_DIR}")
    return BM25Index.load(CACHE_PATH, DATA_DIR)
