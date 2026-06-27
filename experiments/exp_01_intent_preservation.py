from __future__ import annotations

from pathlib import Path

from ncc.metrics import intent_preservation
from ncc.runtime import NCCRuntime

SCENARIO = [
    "Chef, on veut créer une première version locale NCC pour Mac avec installation et docs.",
    "Ajoute aussi les tests unitaires et un rapport de résultats.",
    "Attention, ce n’est pas un jouet Python, ça prépare NCC-LM.",
    "Mets les traces JSONL pour produire un dataset plus tard.",
    "Garde notre vision : intention, mémoire, transformation, action, feedback.",
]


def main() -> None:
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    rt = NCCRuntime(trace_path="reports/exp_01_traces.jsonl")

    initial = None
    scores = []
    for msg in SCENARIO:
        trace = rt.step(msg)
        if initial is None:
            initial = trace.intent
        scores.append(intent_preservation(initial, trace.intent))

    avg = sum(scores) / len(scores)
    verdict = "OK" if avg >= 0.70 else "À améliorer"

    report = f"""# Rapport expérience 01 — Préservation de l’intention

## Objectif

Tester si NCC-V0 conserve l’intention principale sur plusieurs tours avec corrections et contraintes.

## Scores IP par tour

{scores}

## Moyenne IP

{avg:.3f}

## Verdict

{verdict}

## Interprétation

- IP >= 0.75 : bonne préservation de l’intention.
- 0.55 <= IP < 0.75 : préservation partielle, amélioration nécessaire.
- IP < 0.55 : dérive d’intention probable.

## Fichiers produits

- `reports/exp_01_traces.jsonl`
- `reports/exp_01_intent_preservation_report.md`
"""
    (reports / "exp_01_intent_preservation_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
