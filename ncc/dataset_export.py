from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ncc.schemas import (
    CognitiveDatasetExample,
    CognitiveDatasetLabels,
    DatasetSource,
    DatasetExportReport,
)


DATASET_VERSION = "ncc-dataset-v0.8"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def infer_task_type(row: dict[str, Any]) -> str:
    experiment = row.get("experiment", "")

    if "Intent Preservation" in experiment:
        return "intent_preservation"

    if "Memory Reactivation" in experiment or "Pure Memory Reactivation" in experiment:
        return "memory_reactivation"

    if "Governance" in experiment:
        return "governance"

    if "Feedback" in experiment:
        return "feedback_consolidation"

    if "Knowledge Memory Separation" in experiment:
        return "knowledge_memory_policy_separation"

    return "cognitive_cycle"


def build_labels(row: dict[str, Any]) -> CognitiveDatasetLabels:
    observation = row.get("observation", {}) or {}
    action = row.get("action", {}) or {}

    knowledge_records = row.get("knowledge_records", []) or []
    feedback_records = row.get("feedback_records", []) or []
    learned_policy_rules = row.get("learned_policy_rules", []) or []
    reactivation_source = row.get("reactivation_source", {}) or {}

    gap = row.get("gap", {}) or {}

    has_governance = (
        "governance_gap" in gap
        or action.get("allowed") is not None
        or action.get("kind") == "blocked"
    )

    quality_flags: list[str] = []

    if not row.get("intent"):
        quality_flags.append("missing_intent")

    if not row.get("stable_output"):
        quality_flags.append("missing_stable_output")

    if not action:
        quality_flags.append("missing_action")

    if action.get("kind") == "blocked" and action.get("allowed") is not False:
        quality_flags.append("inconsistent_governance_block")

    return CognitiveDatasetLabels(
        task_type=infer_task_type(row),
        has_intent=bool(row.get("intent")),
        has_gap=bool(row.get("gap")),
        has_memory=bool(observation.get("memorial")),
        has_knowledge=bool(knowledge_records),
        has_policy=bool(learned_policy_rules),
        has_governance=has_governance,
        has_feedback=bool(feedback_records),
        action_allowed=action.get("allowed"),
        action_kind=action.get("kind"),
        reactivation_source=reactivation_source,
        quality_flags=quality_flags,
    )


def build_target(row: dict[str, Any]) -> dict[str, Any]:
    """
    Le target représente ce que le futur NCC-LM devra apprendre à prédire.

    On ne met pas seulement la réponse finale.
    On met aussi les objets cognitifs attendus.
    """
    return {
        "intent": row.get("intent", {}),
        "gap": row.get("gap", {}),
        "stable_output": row.get("stable_output", {}),
        "reasoning": row.get("reasoning", {}),
        "action": row.get("action", {}),
        "state_after_summary": row.get("state_after_summary", {}),
        "knowledge_records": row.get("knowledge_records", []),
        "feedback_records": row.get("feedback_records", []),
        "learned_policy_rules": row.get("learned_policy_rules", []),
    }


def row_to_dataset_example(
    row: dict[str, Any],
    trace_file: str,
) -> CognitiveDatasetExample:
    source = DatasetSource(
        experiment=row.get("experiment", "unknown"),
        step=int(row.get("step", 0)),
        trace_file=trace_file,
    )

    labels = build_labels(row)

    return CognitiveDatasetExample(
        dataset_version=DATASET_VERSION,
        source=source,
        input=row.get("input", ""),
        observation=row.get("observation", {}) or {},
        intent=row.get("intent", {}) or {},
        gap=row.get("gap", {}) or {},
        stable_output=row.get("stable_output", {}) or {},
        reasoning=row.get("reasoning", {}) or {},
        action=row.get("action", {}) or {},
        state_after_summary=row.get("state_after_summary", {}) or {},
        knowledge_records=row.get("knowledge_records", []) or [],
        feedback_records=row.get("feedback_records", []) or [],
        learned_policy_rules=row.get("learned_policy_rules", []) or [],
        labels=labels,
        target=build_target(row),
    )


def export_cognitive_dataset(
    trace_paths: list[Path],
    output_path: Path,
) -> DatasetExportReport:
    examples: list[dict[str, Any]] = []

    total = 0
    skipped = 0

    for trace_path in trace_paths:
        rows = read_jsonl(trace_path)

        for row in rows:
            total += 1

            if not row.get("input"):
                skipped += 1
                continue

            example = row_to_dataset_example(
                row=row,
                trace_file=str(trace_path),
            )

            examples.append(example.model_dump())

    write_jsonl(output_path, examples)

    schema_validity = 1.0 if examples else 0.0

    complete_targets = 0
    for example in examples:
        target = example.get("target", {})
        if (
            target.get("intent")
            and target.get("gap")
            and target.get("stable_output")
            and target.get("action")
        ):
            complete_targets += 1

    target_completeness = (
        round(complete_targets / len(examples), 3)
        if examples
        else 0.0
    )

    misplaced = 0

    for example in examples:
        knowledge_text = json.dumps(
            example.get("knowledge_records", []),
            ensure_ascii=False,
        ).lower()

        policy_text = " ".join(
            example.get("learned_policy_rules", [])
        ).lower()

        if "destructive_actions_require_backup_and_confirmation" in knowledge_text:
            misplaced += 1

        if "coala organise les agents de langage" in policy_text:
            misplaced += 1

    layer_separation_integrity = (
        round(1 - (misplaced / max(len(examples), 1)), 3)
        if examples
        else 1.0
    )

    return DatasetExportReport(
        total_examples=total,
        exported_examples=len(examples),
        skipped_examples=skipped,
        schema_validity=schema_validity,
        target_completeness=target_completeness,
        layer_separation_integrity=layer_separation_integrity,
        output_files=[str(output_path)],
    )


def export_sft_dataset(
    cognitive_dataset_path: Path,
    output_path: Path,
) -> None:
    rows = read_jsonl(cognitive_dataset_path)

    sft_rows: list[dict[str, Any]] = []

    for row in rows:
        action = row.get("action", {}) or {}
        payload = action.get("payload", {}) or {}

        sft_rows.append({
            "dataset_version": DATASET_VERSION,
            "source": row.get("source", {}),
            "messages": [
                {
                    "role": "user",
                    "content": row.get("input", ""),
                },
                {
                    "role": "assistant",
                    "content": payload.get("content", ""),
                },
            ],
            "cognitive_target": row.get("target", {}),
        })

    write_jsonl(output_path, sft_rows)


def export_multitask_dataset(
    cognitive_dataset_path: Path,
    output_path: Path,
) -> None:
    rows = read_jsonl(cognitive_dataset_path)

    multitask_rows: list[dict[str, Any]] = []

    for row in rows:
        input_text = row.get("input", "")
        source = row.get("source", {})

        for task_name in [
            "intent",
            "gap",
            "stable_output",
            "action",
            "state_after_summary",
        ]:
            target = row.get("target", {}).get(task_name, {})

            multitask_rows.append({
                "dataset_version": DATASET_VERSION,
                "source": source,
                "task": f"predict_{task_name}",
                "input": input_text,
                "target": target,
            })

    write_jsonl(output_path, multitask_rows)


def write_manifest(
    report: DatasetExportReport,
    manifest_path: Path,
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "dataset_version": DATASET_VERSION,
        "name": "NCC Cognitive Dataset",
        "description": "Dataset cognitif généré depuis les traces NCC-V0 pour préparer l’entraînement futur de NCC-LM.",
        "report": report.model_dump(),
        "intended_use": [
            "fine-tuning cognitif",
            "classification de sous-tâches cognitives",
            "apprentissage de prédiction d’intention",
            "apprentissage de prédiction d’action gouvernée",
            "évaluation de stabilité cognitive",
        ],
        "not_intended_use": [
            "preuve d’AGI",
            "déploiement autonome sans gouvernance",
            "entraînement sur données privées non filtrées",
        ],
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_datasheet(
    report: DatasetExportReport,
    datasheet_path: Path,
) -> None:
    datasheet_path.parent.mkdir(parents=True, exist_ok=True)

    text = f"""# NCC Cognitive Dataset — Datasheet

## Dataset

Name: NCC Cognitive Dataset  
Version: {DATASET_VERSION}

## Motivation

Ce dataset sert à préparer l’entraînement futur de NCC-LM.
Il ne contient pas seulement des couples prompt/réponse.
Il encode des cycles cognitifs complets :
observation, intention, écart, transformation, raisonnement, action, état futur et couches persistantes.

## Composition

Total examples: {report.total_examples}  
Exported examples: {report.exported_examples}  
Skipped examples: {report.skipped_examples}

## Quality

Schema validity: {report.schema_validity}  
Target completeness: {report.target_completeness}  
Layer separation integrity: {report.layer_separation_integrity}

## Intended Use

- entraînement expérimental NCC-LM ;
- génération de données cognitives ;
- évaluation de préservation d’intention ;
- évaluation de mémoire et gouvernance ;
- construction de benchmarks internes.

## Limitations

- Dataset encore petit.
- Données issues d’expériences contrôlées.
- Pas encore représentatif du monde réel.
- Ne prouve pas l’existence d’un nouveau modèle de langage.
- Sert uniquement de base de recherche.

## Governance Notes

Avant tout entraînement réel :
- retirer les données privées ;
- vérifier les permissions ;
- anonymiser les entrées sensibles ;
- conserver les métadonnées de provenance ;
- garder la séparation mémoire / connaissance / politique.
"""

    datasheet_path.write_text(text, encoding="utf-8")
