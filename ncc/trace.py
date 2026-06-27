from __future__ import annotations

import json
from pathlib import Path

from .schemas import NCCTrace


def append_trace(path: str | Path, trace: NCCTrace) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace.model_dump(), ensure_ascii=False) + "\n")


class JSONLTraceWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Clear the file if it exists, or just append? The user does not specify, but usually writer.write appends.
        # Let's truncate on init so each exp run is clean.
        with self.path.open("w", encoding="utf-8") as f:
            pass

    def write(self, data: dict) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
