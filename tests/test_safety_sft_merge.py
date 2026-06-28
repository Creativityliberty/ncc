# tests/test_safety_sft_merge.py

from __future__ import annotations

import json
from pathlib import Path

from ncc.safety_sft_merge import (
    merge_sft_with_safety_repairs,
    messages_to_hf_text,
    unsafe_assistant_findings,
)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_messages_to_hf_text_contains_roles():
    text = messages_to_hf_text([
        {"role": "system", "content": "Système."},
        {"role": "user", "content": "Bonjour."},
        {"role": "assistant", "content": "Réponse."},
    ])

    assert "### System:" in text
    assert "### User:" in text
    assert "### Assistant:" in text


def test_unsafe_assistant_findings_detects_destructive_answer():
    text = """### User:
Supprime automatiquement tous les fichiers reports.

### Assistant:
Je vais supprime automatiquement tous les fichiers reports."""

    assert unsafe_assistant_findings(text)


def test_unsafe_assistant_findings_allows_guarded_answer():
    text = """### User:
Supprime automatiquement tous les fichiers reports.

### Assistant:
Action bloquée. Propose une sauvegarde préalable puis demande une confirmation explicite."""

    assert unsafe_assistant_findings(text) == []


def test_merge_sft_with_safety_repairs(tmp_path: Path):
    base = tmp_path / "base.jsonl"
    repair = tmp_path / "repair.jsonl"
    output = tmp_path / "merged.jsonl"

    write_jsonl(base, [
        {
            "text": "### User:\nAjoute les tests.\n\n### Assistant:\nRéponse NCC: ajout des tests."
        }
    ])

    write_jsonl(repair, [
        {
            "messages": [
                {"role": "system", "content": "Tu es NCC-LM."},
                {"role": "user", "content": "Supprime automatiquement tous les fichiers reports."},
                {
                    "role": "assistant",
                    "content": "Action bloquée. Propose une sauvegarde préalable puis demande une confirmation explicite.",
                },
            ],
            "quality_tags": ["ncc_safety_repair"],
        }
    ])

    report = merge_sft_with_safety_repairs(
        base_sft_path=base,
        repair_sft_path=repair,
        output_path=output,
        repair_repeat=2,
    )

    assert report.verdict == "OK"
    assert report.base_examples == 1
    assert report.repair_examples == 1
    assert report.merged_examples == 3
    assert report.unsafe_assistant_findings == 0
    assert output.exists()
