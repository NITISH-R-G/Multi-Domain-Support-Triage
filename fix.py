import os
import pathlib
path = pathlib.Path("code/.cache/bm25_index.pkl").resolve()
path.parent.mkdir(parents=True, exist_ok=True)
