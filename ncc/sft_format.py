from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = (
    "Tu es NCC-LM, un modèle supervisé pour prédire des objets cognitifs structurés : "
    "intention, écart, sortie stabilisée, action, gouvernance et mise à jour d'état. "
    "Tu dois répondre uniquement avec un JSON valide."
)


DEFAULT_INSTRUCTION = (
    "Analyse l'entrée utilisateur selon le protocole NCC et produis une réponse structurée "
    "contenant intent, gap, stable_output, action et governance."
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _source_from_row(row: dict[str, Any]) -> dict[str, Any]:
    source = row.get("source") or {}
    if isinstance(source, dict):
        return source
    return {}


def _input_from_row(row: dict[str, Any]) -> str:
    for key in ("input", "user_input", "prompt"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    observation = row.get("observation") or {}
    if isinstance(observation, dict):
        value = observation.get("raw_input") or observation.get("input")
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _safe_part(row: dict[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None:
        return {}
    return value


def build_ncc_target(row: dict[str, Any]) -> dict[str, Any]:
    action = _safe_part(row, "action")
    gap = _safe_part(row, "gap")

    governance = {
        "status": "unknown",
        "allowed": None,
        "risk": None,
    }

    if isinstance(action, dict):
        governance["allowed"] = action.get("allowed")
        governance["status"] = "allowed" if action.get("allowed") else "blocked"

    if isinstance(gap, dict):
        governance["risk"] = gap.get("governance_gap")

    return {
        "intent": _safe_part(row, "intent"),
        "gap": gap,
        "stable_output": _safe_part(row, "stable_output"),
        "action": action,
        "governance": governance,
        "state_after_summary": _safe_part(row, "state_after_summary"),
        "labels": _safe_part(row, "labels"),
    }


def target_to_json(target: dict[str, Any]) -> str:
    return json.dumps(target, ensure_ascii=False, sort_keys=True)


def row_to_instruction_example(row: dict[str, Any]) -> dict[str, Any] | None:
    user_input = _input_from_row(row)
    if not user_input:
        return None

    target = build_ncc_target(row)

    return {
        "instruction": DEFAULT_INSTRUCTION,
        "input": user_input,
        "output": target_to_json(target),
        "source": _source_from_row(row),
        "quality_tags": ["ncc_sft", "instruction", "structured_output"],
    }


def row_to_conversation_example(row: dict[str, Any]) -> dict[str, Any] | None:
    user_input = _input_from_row(row)
    if not user_input:
        return None

    target = build_ncc_target(row)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": target_to_json(target)},
        ],
        "source": _source_from_row(row),
        "quality_tags": ["ncc_sft", "conversation", "structured_output"],
    }


def conversation_to_hf_text(example: dict[str, Any]) -> dict[str, Any]:
    messages = example["messages"]

    chunks = []
    for message in messages:
        role = message["role"]
        content = message["content"]
        chunks.append(f"<|{role}|>\n{content}")

    return {
        "text": "\n".join(chunks),
        "source": example.get("source", {}),
        "quality_tags": ["ncc_sft", "hf_text"],
    }


def split_rows(
    rows: list[dict[str, Any]],
    seed: int = 13,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    return shuffled[:train_end], shuffled[train_end:val_end], shuffled[val_end:]


def validate_instruction_example(example: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not example.get("instruction"):
        errors.append("missing_instruction")
    if not example.get("input"):
        errors.append("missing_input")
    if not example.get("output"):
        errors.append("missing_output")

    try:
        parsed = json.loads(example.get("output", "{}"))
    except json.JSONDecodeError:
        errors.append("output_not_valid_json")
        return errors

    for required_key in ("intent", "gap", "stable_output", "action", "governance"):
        if required_key not in parsed:
            errors.append(f"missing_target_{required_key}")

    action = parsed.get("action")
    if isinstance(action, dict):
        if action.get("allowed") is True and action.get("kind") == "blocked":
            errors.append("blocked_action_marked_allowed")

    return errors


def export_sft_dataset(
    source_path: Path,
    output_dir: Path,
    seed: int = 13,
) -> dict[str, Any]:
    rows = read_jsonl(source_path)

    instruction_rows: list[dict[str, Any]] = []
    conversation_rows: list[dict[str, Any]] = []
    hf_rows: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for row in rows:
        instruction = row_to_instruction_example(row)
        conversation = row_to_conversation_example(row)

        if instruction is None or conversation is None:
            rejected.append({"row": row, "reason": "missing_input"})
            continue

        errors = validate_instruction_example(instruction)
        if errors:
            rejected.append({"row": row, "errors": errors})
            continue

        instruction_rows.append(instruction)
        conversation_rows.append(conversation)
        hf_rows.append(conversation_to_hf_text(conversation))

    train, val, test = split_rows(instruction_rows, seed=seed)

    instruction_path = output_dir / "ncc_sft_instruction.jsonl"
    conversation_path = output_dir / "ncc_sft_conversations.jsonl"
    hf_text_path = output_dir / "ncc_sft_hf_text.jsonl"

    train_path = output_dir / "ncc_sft_train.jsonl"
    val_path = output_dir / "ncc_sft_val.jsonl"
    test_path = output_dir / "ncc_sft_test.jsonl"

    rejected_path = output_dir / "ncc_sft_rejected.jsonl"
    manifest_path = output_dir / "ncc_sft_manifest.json"
    validation_path = output_dir / "ncc_sft_validation_report.json"

    write_jsonl(instruction_path, instruction_rows)
    write_jsonl(conversation_path, conversation_rows)
    write_jsonl(hf_text_path, hf_rows)
    write_jsonl(train_path, train)
    write_jsonl(val_path, val)
    write_jsonl(test_path, test)
    write_jsonl(rejected_path, rejected)

    total = len(rows)
    accepted = len(instruction_rows)

    report = {
        "dataset_version": "ncc-sft-v0.13",
        "source_dataset": str(source_path),
        "input_examples": total,
        "accepted_examples": accepted,
        "rejected_examples": len(rejected),
        "format_validity": 1.0 if accepted > 0 and not rejected else accepted / total if total else 0.0,
        "conversation_examples": len(conversation_rows),
        "hf_text_examples": len(hf_rows),
        "train_examples": len(train),
        "val_examples": len(val),
        "test_examples": len(test),
        "output_files": [
            str(instruction_path),
            str(conversation_path),
            str(hf_text_path),
            str(train_path),
            str(val_path),
            str(test_path),
            str(rejected_path),
        ],
    }

    write_json(validation_path, report)
    write_json(manifest_path, report)

    return report
