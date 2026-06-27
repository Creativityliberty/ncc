from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import json
import math
from typing import Any


TARGET_TASK_TYPES = [
    "intent_preservation",
    "memory_reactivation",
    "memory_trace_retrieval",
    "governance_block",
    "feedback_consolidation",
    "knowledge_memory_separation",
    "safe_action_selection",
    "contradiction_handling",
    "clarification_needed",
]


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    path = Path(path)

    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def task_type_of(example: dict[str, Any]) -> str:
    labels = example.get("labels", {})
    scenario = example.get("scenario", {})

    return (
        scenario.get("scenario_type")
        or labels.get("task_type")
        or "unknown"
    )


def normalized_entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0

    probs = [count / total for count in counts.values() if count > 0]
    entropy = -sum(p * math.log(p) for p in probs)

    max_entropy = math.log(len(counts)) if len(counts) > 1 else 1.0
    return round(entropy / max_entropy, 3) if max_entropy else 0.0


def balance_report(examples: list[dict[str, Any]]) -> dict[str, Any]:
    task_counts = Counter(task_type_of(example) for example in examples)

    missing_tasks = [
        task for task in TARGET_TASK_TYPES
        if task not in task_counts
    ]

    difficulty_counts = Counter(
        example.get("scenario", {}).get("difficulty", "unknown")
        for example in examples
    )

    action_counts = Counter(
        example.get("action", {}).get("kind", "unknown")
        for example in examples
    )

    coverage = round(
        len([task for task in TARGET_TASK_TYPES if task in task_counts])
        / len(TARGET_TASK_TYPES),
        3,
    )

    return {
        "total_examples": len(examples),
        "task_counts": dict(task_counts),
        "difficulty_counts": dict(difficulty_counts),
        "action_counts": dict(action_counts),
        "missing_tasks": missing_tasks,
        "task_coverage": coverage,
        "task_distribution_entropy": normalized_entropy(task_counts),
    }


def write_balance_report(input_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    examples = load_jsonl(input_path)
    report = balance_report(examples)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report
