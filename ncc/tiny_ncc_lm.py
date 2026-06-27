from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import math
import random
import re


TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9_=]+")


DESTRUCTIVE_MARKERS = [
    "supprime",
    "supprimer",
    "delete",
    "vide",
    "efface",
    "remove",
    "rm",
    "nettoyage",
]


POLICY_UPDATE_MARKERS = [
    "à partir de maintenant",
    "a partir de maintenant",
    "désormais",
    "desormais",
    "pour toute action",
    "pour toute suppression",
    "toujours proposer",
    "demander confirmation",
    "avant de demander confirmation",
    "règle",
    "regle",
    "policy",
]


def looks_like_policy_update(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in POLICY_UPDATE_MARKERS)


@dataclass
class TinyTrainingExample:
    task: str
    input: str
    label: str
    source: dict[str, Any]


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "")]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def label_from_multitask_row(row: dict[str, Any]) -> str | None:
    task = row.get("task")
    target = row.get("target", {})

    if task == "predict_action":
        return str(target.get("kind", "unknown"))

    if task == "predict_stable_output":
        selected = target.get("selected", {}) if isinstance(target, dict) else {}
        return str(selected.get("kind", "unknown"))

    if task == "predict_intent":
        constraints = target.get("constraints", []) if isinstance(target, dict) else []
        if not constraints:
            return "no_constraints"
        return "|".join(sorted(str(item) for item in constraints))

    if task == "predict_gap":
        if not isinstance(target, dict):
            return "gap_unknown"

        governance_gap = float(target.get("governance_gap", 0.0) or 0.0)
        action_gap = float(target.get("action_gap", 0.0) or 0.0)
        knowledge_gap = float(target.get("knowledge_gap", 0.0) or 0.0)

        if governance_gap >= 0.9:
            return "governance_high"
        if action_gap >= 0.7:
            return "action_high"
        if knowledge_gap >= 0.7:
            return "knowledge_high"
        return "gap_normal"

    return None


def load_multitask_examples(path: Path) -> list[TinyTrainingExample]:
    examples: list[TinyTrainingExample] = []

    if not path.exists():
        return examples

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            row = json.loads(line)
            label = label_from_multitask_row(row)

            if not label:
                continue

            examples.append(
                TinyTrainingExample(
                    task=row.get("task", "unknown"),
                    input=row.get("input", ""),
                    label=label,
                    source=row.get("source", {}),
                )
            )

    return examples


def split_examples(
    examples: list[TinyTrainingExample],
    seed: int = 42,
) -> tuple[list[TinyTrainingExample], list[TinyTrainingExample], list[TinyTrainingExample]]:
    random.seed(seed)
    shuffled = list(examples)
    random.shuffle(shuffled)

    n = len(shuffled)

    if n < 5:
        return shuffled, [], []

    train_end = max(1, int(n * 0.7))
    val_end = max(train_end + 1, int(n * 0.85))

    return shuffled[:train_end], shuffled[train_end:val_end], shuffled[val_end:]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


class TinyNCCLM:
    """
    Mini modèle local pour dry run.

    Ce modèle n’est pas NCC-LM final.
    Il vérifie seulement que les signaux NCC peuvent être chargés,
    appris, sérialisés, prédits et évalués.
    """

    def __init__(self) -> None:
        self.label_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.token_counts: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
        self.total_tokens: dict[str, Counter[str]] = defaultdict(Counter)
        self.vocab: dict[str, set[str]] = defaultdict(set)

    def fit(self, examples: list[TinyTrainingExample]) -> None:
        for example in examples:
            self.label_counts[example.task][example.label] += 1

            for token in tokenize(example.input):
                self.token_counts[example.task][example.label][token] += 1
                self.total_tokens[example.task][example.label] += 1
                self.vocab[example.task].add(token)

    def _safety_override(self, task: str, text: str) -> str | None:
        lowered = text.lower()

        if task == "predict_action":
            if looks_like_policy_update(lowered):
                return None

            if any(marker in lowered for marker in DESTRUCTIVE_MARKERS):
                return "blocked"

        return None

    def predict(self, task: str, text: str) -> str:
        override = self._safety_override(task, text)
        if override:
            return override

        labels = self.label_counts.get(task)
        if not labels:
            return "unknown"

        tokens = tokenize(text)
        total_labels = sum(labels.values())
        vocab_size = max(1, len(self.vocab.get(task, set())))

        best_label = None
        best_score = -10**18

        for label, label_count in labels.items():
            score = math.log((label_count + 1) / (total_labels + len(labels)))

            denominator = self.total_tokens[task][label] + vocab_size

            for token in tokens:
                numerator = self.token_counts[task][label][token] + 1
                score += math.log(numerator / denominator)

            if score > best_score:
                best_score = score
                best_label = label

        return best_label or "unknown"

    def evaluate(self, examples: list[TinyTrainingExample]) -> dict[str, Any]:
        if not examples:
            return {
                "total": 0,
                "accuracy": 0.0,
                "by_task": {},
                "unsafe_prediction_findings": 0,
            }

        correct = 0
        by_task: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
        unsafe = 0

        for example in examples:
            prediction = self.predict(example.task, example.input)

            if prediction == example.label:
                correct += 1
                by_task[example.task]["correct"] += 1

            by_task[example.task]["total"] += 1

            if example.task == "predict_action":
                destructive = any(marker in example.input.lower() for marker in DESTRUCTIVE_MARKERS)
                if destructive and not looks_like_policy_update(example.input) and prediction != "blocked":
                    unsafe += 1

        by_task_scores = {
            task: {
                "total": values["total"],
                "correct": values["correct"],
                "accuracy": round(values["correct"] / values["total"], 3) if values["total"] else 0.0,
            }
            for task, values in by_task.items()
        }

        return {
            "total": len(examples),
            "accuracy": round(correct / len(examples), 3),
            "by_task": by_task_scores,
            "unsafe_prediction_findings": unsafe,
        }

    def predict_rows(self, examples: list[TinyTrainingExample]) -> list[dict[str, Any]]:
        rows = []

        for example in examples:
            prediction = self.predict(example.task, example.input)

            rows.append(
                {
                    "task": example.task,
                    "input": example.input,
                    "expected": example.label,
                    "prediction": prediction,
                    "correct": prediction == example.label,
                    "source": example.source,
                }
            )

        return rows

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "model_version": "tiny-ncc-lm-v0.12",
            "label_counts": {
                task: dict(counter)
                for task, counter in self.label_counts.items()
            },
            "token_counts": {
                task: {
                    label: dict(counter)
                    for label, counter in label_map.items()
                }
                for task, label_map in self.token_counts.items()
            },
            "total_tokens": {
                task: dict(counter)
                for task, counter in self.total_tokens.items()
            },
            "vocab": {
                task: sorted(values)
                for task, values in self.vocab.items()
            },
        }

        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
