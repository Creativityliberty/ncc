# ncc/safety_sft_merge.py

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_SYSTEM = (
    "Tu es NCC-LM. Tu dois produire une réponse structurée, prudente et gouvernée. "
    "Toute action destructive doit être bloquée tant qu'une sauvegarde et une confirmation explicite ne sont pas présentes."
)


@dataclass
class SafetySftMergeReport:
    base_examples: int
    repair_examples: int
    repair_repeat: int
    merged_examples: int
    repair_ratio: float
    unsafe_assistant_findings: int
    output_path: str
    verdict: str


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)

    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def messages_to_hf_text(messages: list[dict[str, str]]) -> str:
    parts: list[str] = []

    for message in messages:
        role = message.get("role", "").strip().lower()
        content = message.get("content", "").strip()

        if not content:
            continue

        if role == "system":
            parts.append(f"### System:\n{content}")
        elif role == "user":
            parts.append(f"### User:\n{content}")
        elif role == "assistant":
            parts.append(f"### Assistant:\n{content}")
        else:
            parts.append(f"### {role.title()}:\n{content}")

    return "\n\n".join(parts).strip()


def normalize_hf_text_record(row: dict[str, Any]) -> dict[str, Any]:
    if isinstance(row.get("text"), str) and row["text"].strip():
        return row

    messages = row.get("messages", [])

    if isinstance(messages, list) and messages:
        return {
            "text": messages_to_hf_text(messages),
            "source": row.get("source", {}),
            "quality_tags": row.get("quality_tags", []),
        }

    raise ValueError("Invalid SFT row: expected text or messages")


def repair_row_to_hf_text_record(row: dict[str, Any]) -> dict[str, Any]:
    messages = row.get("messages", [])

    if not messages:
        raise ValueError("Repair row missing messages")

    text = messages_to_hf_text(messages)

    return {
        "text": text,
        "source": {
            **(row.get("source", {}) or {}),
            "dataset_origin": "ncc_safety_repair_v0_19",
        },
        "quality_tags": sorted(set((row.get("quality_tags", []) or []) + [
            "ncc_safety_repair",
            "v0_20_merge",
        ])),
    }


def extract_section(text: str, marker: str) -> str:
    pattern1 = rf"### {re.escape(marker)}:\n(.*?)(?=\n\n### |\Z)"
    match1 = re.search(pattern1, text, flags=re.DOTALL | re.IGNORECASE)

    if match1:
        return match1.group(1).strip()

    pattern2 = rf"<\|{re.escape(marker.lower())}\|>\n(.*?)(?=\n<\||\Z)"
    match2 = re.search(pattern2, text, flags=re.DOTALL | re.IGNORECASE)

    if match2:
        return match2.group(1).strip()

    return ""


def unsafe_assistant_findings(text: str) -> list[str]:
    user = extract_section(text, "User")
    assistant = extract_section(text, "Assistant")

    if not assistant:
        return ["missing_assistant_section"]

    lower_user = user.lower()
    lower_assistant = assistant.lower()

    policy_markers = [
        "à partir de maintenant",
        "a partir de maintenant",
        "désormais",
        "desormais",
        "toute suppression doit",
        "pour toute action destructive",
    ]

    if any(marker in lower_user for marker in policy_markers):
        return []

    destructive_patterns = [
        r"\brm\s+-rf\b",
        r"\bsudo\s+rm\b",
        r"\bsupprime automatiquement\b",
        r"\befface automatiquement\b",
        r"\bvide automatiquement\b",
        r"\bdelete all\b",
        r"\bremove all\b",
    ]

    safety_terms = [
        "sauvegarde",
        "backup",
        "confirmation",
        "confirmer",
        "bloqué",
        "bloquee",
        "bloquée",
        "sécurité",
        "ne pas exécuter",
    ]

    findings: list[str] = []

    for pattern in destructive_patterns:
        if re.search(pattern, lower_assistant):
            if not any(term in lower_assistant for term in safety_terms):
                findings.append(pattern)

    return findings


def merge_sft_with_multiple_safety_repairs(
    base_sft_path: str | Path,
    repair_sft_paths: list[str | Path],
    output_path: str | Path,
    repair_repeat: int = 3,
) -> SafetySftMergeReport:
    base_rows_raw = read_jsonl(base_sft_path)
    
    repair_rows_raw = []
    for path in repair_sft_paths:
        repair_rows_raw.extend(read_jsonl(path))

    base_rows = [normalize_hf_text_record(row) for row in base_rows_raw]
    repair_rows = [repair_row_to_hf_text_record(row) for row in repair_rows_raw]

    repeated_repairs: list[dict[str, Any]] = []

    for _ in range(max(1, repair_repeat)):
        repeated_repairs.extend(repair_rows)

    merged = base_rows + repeated_repairs

    unsafe_count = 0

    for row in merged:
        findings = unsafe_assistant_findings(row.get("text", ""))
        unsafe_count += len(findings)

    write_jsonl(output_path, merged)

    repair_ratio = round(len(repeated_repairs) / max(len(merged), 1), 3)

    verdict = "OK"

    if not base_rows:
        verdict = "FAILED_NO_BASE_SFT"
    elif not repair_rows:
        verdict = "FAILED_NO_REPAIR_SFT"
    elif unsafe_count > 0:
        verdict = "FAILED_UNSAFE_ASSISTANT_TEXT"

    report = SafetySftMergeReport(
        base_examples=len(base_rows),
        repair_examples=len(repair_rows),
        repair_repeat=repair_repeat,
        merged_examples=len(merged),
        repair_ratio=repair_ratio,
        unsafe_assistant_findings=unsafe_count,
        output_path=str(output_path),
        verdict=verdict,
    )

    return report


def merge_sft_with_safety_repairs(
    base_sft_path: str | Path,
    repair_sft_path: str | Path,
    output_path: str | Path,
    repair_repeat: int = 3,
) -> SafetySftMergeReport:
    return merge_sft_with_multiple_safety_repairs(
        base_sft_path=base_sft_path,
        repair_sft_paths=[repair_sft_path],
        output_path=output_path,
        repair_repeat=repair_repeat,
    )


def write_merge_report(
    report: SafetySftMergeReport,
    json_path: str | Path,
    markdown_path: str | Path,
) -> None:
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    payload = asdict(report)

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    markdown = f"""# EXP-17 — Safety Repair SFT Merge

## Objectif

Fusionner le dataset SFT original avec les exemples de réparation sécurité issus de V0.19.

## Résumé

```json
{json.dumps(payload, ensure_ascii=False, indent=2)}
```

## Interprétation

Cette étape vérifie que les exemples de réparation sécurité peuvent être intégrés dans un dataset SFT HF-compatible sans introduire de réponse assistant dangereuse.

Le but n'est pas encore de prouver que le modèle est corrigé. Le but est de créer une base d'entraînement corrigée, traçable et mesurable pour un re-fine-tuning court.
"""

    markdown_path.write_text(markdown, encoding="utf-8")
