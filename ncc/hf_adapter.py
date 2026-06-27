from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def count_basic_tokens(text: str) -> int:
    return len(text.split())


def validate_hf_text_dataset(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    malformed = 0
    empty_text = 0
    token_counts: list[int] = []

    for row in rows:
        text = row.get("text")
        if not isinstance(text, str):
            malformed += 1
            continue
        if not text.strip():
            empty_text += 1
            continue
        token_counts.append(count_basic_tokens(text))

    total = len(rows)

    return {
        "path": str(path),
        "total": total,
        "malformed": malformed,
        "empty_text": empty_text,
        "min_basic_tokens": min(token_counts) if token_counts else 0,
        "max_basic_tokens": max(token_counts) if token_counts else 0,
        "avg_basic_tokens": round(sum(token_counts) / len(token_counts), 3) if token_counts else 0.0,
        "loadable": total > 0 and malformed == 0 and empty_text == 0,
    }


def try_transformers_tokenizer(path: Path, tokenizer_name: str | None = None) -> dict[str, Any]:
    if not tokenizer_name:
        return {
            "enabled": False,
            "reason": "no_tokenizer_name_provided",
        }

    try:
        from transformers import AutoTokenizer
    except Exception as exc:
        return {
            "enabled": False,
            "reason": "transformers_not_available",
            "error": str(exc),
        }

    rows = read_jsonl(path)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    token_lengths = []
    for row in rows:
        text = row.get("text", "")
        encoded = tokenizer(text, add_special_tokens=False)
        token_lengths.append(len(encoded["input_ids"]))

    return {
        "enabled": True,
        "tokenizer_name": tokenizer_name,
        "examples": len(rows),
        "min_tokens": min(token_lengths) if token_lengths else 0,
        "max_tokens": max(token_lengths) if token_lengths else 0,
        "avg_tokens": round(sum(token_lengths) / len(token_lengths), 3) if token_lengths else 0.0,
    }
