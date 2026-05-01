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

# Retrieval fusion (BM25 + offline TF-IDF). Weights are applied after per-candidate normalization.
INDEX_VERSION = int(os.environ.get("ORCHESTRATE_INDEX_VERSION", "2"))
HYBRID_CANDIDATES = int(os.environ.get("HYBRID_CANDIDATES", "160"))
BM25_WEIGHT = float(os.environ.get("BM25_WEIGHT", "0.55"))
TFIDF_WEIGHT = float(os.environ.get("TFIDF_WEIGHT", "0.45"))

# Lexical rerank bonuses (query term appears in chunk); tunable without editing code.
RERANK_BONUS_TEAM = float(os.environ.get("ORCHESTRATE_RERANK_BONUS_TEAM", "5.0"))
RERANK_BONUS_WORKSPACE = float(os.environ.get("ORCHESTRATE_RERANK_BONUS_WORKSPACE", "5.0"))
RERANK_BONUS_BRAND = float(os.environ.get("ORCHESTRATE_RERANK_BONUS_BRAND", "3.0"))

# Grounding: replace LLM/offline draft when overlap with retrieved text is too low or numeric guard fires.
# Lower min_overlap = fewer silent rewrites (more trust in the generator).
GROUNDING_MIN_OVERLAP = float(os.environ.get("ORCHESTRATE_GROUNDING_MIN_OVERLAP", "0.12"))
# resynthesize: offline synthesis from hits; escalate: human handoff when check fails.
GROUNDING_FAIL_MODE = os.environ.get("ORCHESTRATE_GROUNDING_FAIL_MODE", "resynthesize").strip().lower()
