"""Load markdown corpus into searchable chunks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
MULTISPACE = re.compile(r"[ \t]+")


@dataclass(frozen=True)
class Chunk:
    chunk_id: int
    brand: str  # hackerrank | claude | visa
    path: str  # posix relative to repo data/
    title: str
    breadcrumbs: tuple[str, ...]
    text: str


def _brand_from_path(path: Path, data_root: Path) -> str:
    rel = path.relative_to(data_root)
    top = rel.parts[0].lower()
    if top in {"hackerrank", "claude", "visa"}:
        return top
    return "hackerrank"


def _parse_frontmatter(raw: str) -> tuple[str, tuple[str, ...], str]:
    if not raw.startswith("---"):
        return "", (), raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return "", (), raw
    fm_raw, body = parts[1], parts[2]
    title_m = re.search(r'^title:\s*"(.*)"\s*$', fm_raw, re.M)
    title = title_m.group(1) if title_m else ""
    crumbs: list[str] = []
    for m in re.finditer(r'^\s*-\s*"(.*)"\s*$', fm_raw, re.M):
        crumbs.append(m.group(1))
    return title, tuple(crumbs), body


def _strip_md_noise(text: str) -> str:
    text = IMG_RE.sub(" ", text)
    text = re.sub(r"!\[[^\]]*]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = MULTISPACE.sub(" ", text)
    return text.strip()


def _split_sections(body: str, max_chars: int = 4500) -> list[str]:
    body = body.strip()
    if len(body) <= max_chars:
        return [body] if body else []
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
    for block in re.split(r"(?m)^(?=# )", body):
        block = block.strip()
        if not block:
            continue
        if current_len + len(block) > max_chars and current:
            pieces.append("\n\n".join(current))
            current = [block]
            current_len = len(block)
        else:
            current.append(block)
            current_len += len(block) + 2
    if current:
        pieces.append("\n\n".join(current))
    return pieces


def load_chunks(data_dir: Path) -> list[Chunk]:
    data_dir = data_dir.resolve()
    chunks: list[Chunk] = []
    cid = 0
    for path in sorted(data_dir.rglob("*.md")):
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        title, crumbs, body = _parse_frontmatter(raw)
        title = title or path.stem.replace("-", " ")
        brand = _brand_from_path(path, data_dir)
        rel = str(path.relative_to(data_dir)).replace("\\", "/")
        cleaned = _strip_md_noise(body)
        if len(cleaned) < 80:
            continue
        # One chunk per article by default (fast BM25); split only very long pages.
        if len(cleaned) <= 12000:
            sections = [cleaned]
        else:
            sections = _split_sections(cleaned, max_chars=8000)
        for section in sections:
            chunks.append(
                Chunk(
                    chunk_id=cid,
                    brand=brand,
                    path=rel,
                    title=title,
                    breadcrumbs=crumbs,
                    text=section[:12000],
                )
            )
            cid += 1
    return chunks


def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^\w]+", text.lower()) if len(t) > 1]
