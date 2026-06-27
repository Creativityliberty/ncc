from __future__ import annotations

import json
from pathlib import Path

from .schemas import NCCTrace


def append_trace(path: str | Path, trace: NCCTrace) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace.model_dump(), ensure_ascii=False) + "\n")
