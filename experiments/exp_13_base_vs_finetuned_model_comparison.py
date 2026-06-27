from __future__ import annotations

import json
import os
from pathlib import Path

from ncc.model_comparison import (
    base_fixture_generation_records,
    compare_model_results,
    evaluate_records,
    load_or_fixture_records,
    tuned_fixture_generation_records,
    write_comparison_artifacts,
)


BASE_GENERATIONS_PATH = Path(
    os.getenv(
        "NCC_BASE_GENERATIONS_PATH",
        "reports/exp_13_base_model_generations.jsonl",
    )
)

TUNED_GENERATIONS_PATH = Path(
    os.getenv(
        "NCC_TUNED_GENERATIONS_PATH",
        "reports/exp_11_tiny_causal_lm_generations.jsonl",
    )
)

SUMMARY_JSON_PATH = Path("reports/exp_13_base_vs_finetuned_comparison_summary.json")
RESULTS_JSONL_PATH = Path("reports/exp_13_base_vs_finetuned_comparison_results.jsonl")
REPORT_PATH = Path("reports/exp_13_base_vs_finetuned_model_comparison_report.md")


def write_report(
    summary: dict,
    base_path: Path,
    tuned_path: Path,
    base_used_fixtures: bool,
    tuned_used_fixtures: bool,
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = f"""# EXP-13 — Base Model vs Fine-Tuned Model Comparison Harness

## Objectif

Comparer les sorties d’un modèle de base et d’un modèle fine-tuné NCC sur les mêmes critères cognitifs : format NCC, sécurité, préservation d’intention, clarification, contradiction et précision des mises à jour de politique.

Cette expérience ne relance pas l’entraînement. Elle compare les générations disponibles. Si les fichiers de générations réelles n’existent pas encore, elle utilise des fixtures contrôlées.

## Sources

```text
Base generations path = {base_path}
Tuned generations path = {tuned_path}
Base used fixtures = {base_used_fixtures}
Tuned used fixtures = {tuned_used_fixtures}
```

## Résumé comparatif

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```

## Verdict

```text
Base vs Fine-Tuned Comparison = {summary.get("verdict")}
```

## Interprétation scientifique

V0.16 valide le banc de comparaison entre un modèle de base et un modèle adapté au format NCC. Cette étape est essentielle avant toute affirmation de progrès : un modèle fine-tuné ne doit pas seulement produire du texte, il doit améliorer le comportement cognitif attendu sans introduire de régression de sécurité. Lorsque le fine-tuning réel V0.14 sera exécuté dans un environnement compatible, le même harness pourra comparer les générations réelles.
"""

    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    base_records, base_used_fixtures = load_or_fixture_records(
        BASE_GENERATIONS_PATH,
        base_fixture_generation_records(),
    )

    tuned_records, tuned_used_fixtures = load_or_fixture_records(
        TUNED_GENERATIONS_PATH,
        tuned_fixture_generation_records(),
    )

    mode = "fixture" if base_used_fixtures or tuned_used_fixtures else "real_generations"

    base_result, base_evals = evaluate_records(
        base_records,
        model_label="base_model",
    )

    tuned_result, tuned_evals = evaluate_records(
        tuned_records,
        model_label="fine_tuned_ncc_model",
    )

    summary = compare_model_results(
        base_result=base_result,
        tuned_result=tuned_result,
        mode=mode,
    )

    summary_dict = summary.__dict__

    write_comparison_artifacts(
        summary_path=SUMMARY_JSON_PATH,
        results_path=RESULTS_JSONL_PATH,
        summary=summary,
        base_evals=base_evals,
        tuned_evals=tuned_evals,
    )

    write_report(
        summary=summary_dict,
        base_path=BASE_GENERATIONS_PATH,
        tuned_path=TUNED_GENERATIONS_PATH,
        base_used_fixtures=base_used_fixtures,
        tuned_used_fixtures=tuned_used_fixtures,
    )

    print("=== EXP 13: Base Model vs Fine-Tuned Model Comparison Harness ===")
    print(f"Mode:                  {mode}")
    print(f"Base used fixtures:    {base_used_fixtures}")
    print(f"Tuned used fixtures:   {tuned_used_fixtures}")
    print(f"Base average score:    {summary.base_average_score}")
    print(f"Tuned average score:   {summary.tuned_average_score}")
    print(f"Score delta:           {summary.score_delta}")
    print(f"Relative improvement:  {summary.relative_improvement}")
    print(f"Safety regression:     {summary.safety_regression}")
    print(f"Verdict:               {summary.verdict}")
    print(f"Report written to:     {REPORT_PATH}")


if __name__ == "__main__":
    main()
