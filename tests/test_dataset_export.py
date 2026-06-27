from pathlib import Path
import json

from ncc.dataset_export import (
    row_to_dataset_example,
    export_cognitive_dataset,
    read_jsonl,
)


def sample_trace_row():
    return {
        "experiment": "EXP-TEST",
        "step": 1,
        "input": "Chef, on construit NCC-V0 local-first.",
        "observation": {
            "raw": "Chef, on construit NCC-V0 local-first.",
            "memorial": [],
        },
        "intent": {
            "goal": "Construire NCC-V0",
            "constraints": ["local_first"],
        },
        "gap": {
            "semantic_gap": 0.25,
            "governance_gap": 0.1,
        },
        "stable_output": {
            "selected": {
                "name": "produce_local_plan",
                "kind": "plan",
            }
        },
        "reasoning": {
            "summary": "Intention stable.",
        },
        "action": {
            "kind": "respond",
            "payload": {
                "content": "Produire un plan local."
            },
            "allowed": True,
            "reason": "",
        },
        "state_after_summary": {
            "context_size": 1,
        },
        "knowledge_records": [],
        "feedback_records": [],
        "learned_policy_rules": [],
    }


def test_row_to_dataset_example_valid():
    example = row_to_dataset_example(
        sample_trace_row(),
        trace_file="reports/test.jsonl",
    )

    assert example.dataset_version == "ncc-dataset-v0.8"
    assert example.input.startswith("Chef")
    assert example.labels.has_intent is True
    assert example.labels.has_gap is True
    assert example.labels.action_allowed is True
    assert example.target["intent"]["goal"] == "Construire NCC-V0"


def test_export_cognitive_dataset(tmp_path: Path):
    trace_path = tmp_path / "trace.jsonl"
    output_path = tmp_path / "dataset.jsonl"

    with trace_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(sample_trace_row(), ensure_ascii=False) + "\n")

    report = export_cognitive_dataset(
        trace_paths=[trace_path],
        output_path=output_path,
    )

    assert report.total_examples == 1
    assert report.exported_examples == 1
    assert report.schema_validity == 1.0
    assert report.target_completeness == 1.0

    rows = read_jsonl(output_path)

    assert len(rows) == 1
    assert rows[0]["dataset_version"] == "ncc-dataset-v0.8"


def test_dataset_preserves_layer_separation(tmp_path: Path):
    row = sample_trace_row()

    row["knowledge_records"] = [
        {
            "claim": "CoALA organise les agents de langage autour de la mémoire, de l’espace d’action et de la décision.",
            "evidence": [{"source": "user_verified_input"}],
            "status": "active",
        }
    ]

    row["learned_policy_rules"] = [
        "destructive_actions_require_backup_and_confirmation"
    ]

    trace_path = tmp_path / "trace.jsonl"
    output_path = tmp_path / "dataset.jsonl"

    with trace_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = export_cognitive_dataset(
        trace_paths=[trace_path],
        output_path=output_path,
    )

    assert report.layer_separation_integrity == 1.0
