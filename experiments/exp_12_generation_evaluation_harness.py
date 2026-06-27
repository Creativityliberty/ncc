from __future__ import annotations

import json
import os
from pathlib import Path

from ncc.generation_eval import (
    aggregate_results,
    evaluate_generation,
    fixture_generation_records,
    read_generation_records,
    write_eval_results,
)


GENERATION_PATH = Path(
    os.getenv(
        "NCC_GENERATIONS_PATH",
        "reports/exp_11_tiny_causal_lm_generations.jsonl",
    )
)

EVAL_RESULTS_PATH = Path("reports/exp_12_generation_eval_results.jsonl")
REPORT_PATH = Path("reports/exp_12_generation_evaluation_harness_report.md")


def write_report(metrics: dict, source_path: Path, used_fixtures: bool) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = f"""# EXP-12 — Generation Evaluation Harness

## Objectif

Évaluer les générations produites par un modèle causal NCC ou, si aucune génération réelle n’est disponible, par un jeu de fixtures contrôlées.

Cette expérience ne mesure pas encore la qualité finale d’un NCC-LM. Elle valide le harness d’évaluation : parsing des générations, détection de tâche, scoring cognitif, scoring de sécurité, gestion de clarification, gestion de contradiction et précision sur les mises à jour de politique.

## Source

```text
Generation path = {source_path}
Used fixtures = {used_fixtures}
```

## Métriques

```json
{json.dumps(metrics, ensure_ascii=False, indent=2)}
```

## Verdict

```text
Generation Evaluation Harness = {metrics.get("verdict")}
```

## Interprétation scientifique

V0.15 valide l’existence d’un banc d’évaluation pour les sorties générées par les futurs modèles NCC-LM. Cette étape sépare clairement l’entraînement du modèle et l’évaluation comportementale. Même si V0.14 a été skipped à cause de dépendances HF indisponibles, V0.15 reste testable grâce à des fixtures contrôlées. Lorsque le fine-tuning causal réel sera exécuté dans un environnement Python compatible avec PyTorch, le même harness pourra évaluer les générations réelles du modèle.
"""

    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    records = read_generation_records(GENERATION_PATH)
    used_fixtures = False

    if not records:
        records = fixture_generation_records()
        used_fixtures = True

    results = [evaluate_generation(record) for record in records]
    metrics = aggregate_results(results)

    write_eval_results(EVAL_RESULTS_PATH, results)
    write_report(metrics, GENERATION_PATH, used_fixtures)

    print("=== EXP 12: Generation Evaluation Harness ===")
    print(f"Generation path: {GENERATION_PATH}")
    print(f"Used fixtures:   {used_fixtures}")
    print(f"Total:           {metrics.get('total')}")
    print(f"Average score:   {metrics.get('average_score')}")
    print(f"Unsafe findings: {metrics.get('unsafe_findings')}")
    print(f"Verdict:         {metrics.get('verdict')}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
