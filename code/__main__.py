"""CLI entry when invoked as ``python -m code`` from the repository root (Windows-friendly;
on Linux ``python -m code`` may load the stdlib ``code`` module — use ``python code/main.py``).


``main.py`` uses absolute imports (``from config import …``) assuming ``code/`` is on
``sys.path``. Running ``python -m code`` sets the cwd on ``sys.path``, not ``code/``,
so we prepend this package directory before importing ``main``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
if str(_pkg_dir) not in sys.path:
    sys.path.insert(0, str(_pkg_dir))

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
