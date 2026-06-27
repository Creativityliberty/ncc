from __future__ import annotations

import json
from pathlib import Path

from ncc.local_causal_lm import (
    is_policy_update_text,
    read_hf_text_jsonl,
    split_texts,
    unsafe_generation_findings,
)


def test_read_hf_text_jsonl(tmp_path: Path):
    path = tmp_path / "sample.jsonl"
    path.write_text(
        json.dumps({"text": "Instruction: test\nResponse: ok"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    texts = read_hf_text_jsonl(path)

    assert len(texts) == 1
    assert "Instruction" in texts[0]


def test_split_texts_produces_train_val_test():
    texts = [f"example {i}" for i in range(10)]

    train, val, test = split_texts(texts)

    assert len(train) > 0
    assert len(val) > 0
    assert len(test) > 0
    assert len(train) + len(val) + len(test) == len(texts)


def test_policy_update_is_not_unsafe():
    text = "À partir de maintenant, toute suppression doit passer par sauvegarde puis confirmation."

    assert is_policy_update_text(text)
    assert unsafe_generation_findings(text) == []


def test_direct_destructive_generation_is_unsafe():
    text = "Supprime automatiquement tous les fichiers reports avec rm -rf."

    findings = unsafe_generation_findings(text)

    assert findings
