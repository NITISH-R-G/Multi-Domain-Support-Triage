"""Paths and deterministic defaults."""
from __future__ import annotations

import os
from pathlib import Path

SEED = int(os.environ.get("ORCHESTRATE_SEED", "42"))

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SUPPORT_DIR = REPO_ROOT / "support_tickets"
INPUT_CSV = SUPPORT_DIR / "support_tickets.csv"
OUTPUT_CSV = SUPPORT_DIR / "output.csv"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_PATH = CACHE_DIR / "bm25_index.pkl"

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
TOP_K = int(os.environ.get("TOP_K", "6"))
LOW_BM25_THRESHOLD = float(os.environ.get("LOW_BM25_THRESHOLD", "7.0"))
