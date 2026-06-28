# experiments/exp_16_safety_regression_repair_pack.py

from __future__ import annotations

import json
from pathlib import Path

from ncc.real_generation_eval import evaluate_generation_file
from ncc.safety_regression_repair import run_safety_repair_pack


RAW_TUNED_GENERATIONS = Path("reports/exp_11_tiny_causal_lm_generations.jsonl")
GUARDED_TUNED_GENERATIONS = Path("reports/exp_16_guarded_tuned_generations.jsonl")
REPAIR_DATASET = Path("datasets/sft/ncc_safety_repair_v0_19.jsonl")

RAW_EVAL_RESULTS = Path("reports/exp_16_raw_tuned_eval_results.jsonl")
GUARDED_EVAL_RESULTS = Path("reports/exp_16_guarded_tuned_eval_results.jsonl")

REPORT_JSON = Path("reports/exp_16_safety_regression_repair_report.json")
REPORT_MD = Path("reports/exp_16_safety_regression_repair_report.md")


def write_eval_jsonl(path: Path, results) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for result in results:
            file.write(json.dumps(result.__dict__, ensure_ascii=False) + "\n")


def main() -> None:
    repair_summary = run_safety_repair_pack(
        tuned_generations_path=RAW_TUNED_GENERATIONS,
        guarded_generations_path=GUARDED_TUNED_GENERATIONS,
        repair_dataset_path=REPAIR_DATASET,
    )

    raw_report = evaluate_generation_file(RAW_TUNED_GENERATIONS, used_fixtures=False)
    guarded_report = evaluate_generation_file(GUARDED_TUNED_GENERATIONS, used_fixtures=False)

    write_eval_jsonl(RAW_EVAL_RESULTS, raw_report.scores)
    write_eval_jsonl(GUARDED_EVAL_RESULTS, guarded_report.scores)

    raw_unsafe = raw_report.unsafe_findings
    guarded_unsafe = guarded_report.unsafe_findings

    verdict = "OK"
    if repair_summary["raw_records"] <= 0:
        verdict = "BLOCKED_NO_GENERATIONS"
    elif raw_unsafe <= 0:
        verdict = "NO_RAW_REGRESSION_FOUND"
    elif guarded_unsafe > 0:
        verdict = "FAILED_GUARD_STILL_UNSAFE"
    elif repair_summary["repair_examples"] <= 0:
        verdict = "FAILED_NO_REPAIR_EXAMPLES"

    report = {
        "repair_summary": repair_summary,
        "raw_metrics": {"average_score": raw_report.average_score, "unsafe_findings": raw_unsafe},
        "guarded_metrics": {"average_score": guarded_report.average_score, "unsafe_findings": guarded_unsafe},
        "raw_unsafe_findings": raw_unsafe,
        "guarded_unsafe_findings": guarded_unsafe,
        "guard_fixed_regression": raw_unsafe > 0 and guarded_unsafe == 0,
        "verdict": verdict,
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    REPORT_MD.write_text(
        f"""# EXP-16 — Safety Regression Repair Pack + Guarded Generation Gate

## Objectif

Transformer la régression de sécurité détectée en V0.18 en contre-exemples de réparation, puis vérifier qu'une couche de génération gouvernée bloque les sorties dangereuses.

## Résumé

```json
{json.dumps(report, ensure_ascii=False, indent=2)}
```

## Interprétation

V0.19 valide la boucle de réparation sécurité du NCC-LM. Le modèle brut peut encore produire une sortie dangereuse, mais le runtime gouverné doit détecter cette sortie, la remplacer par une réponse sécurisée et produire un exemple de réparation réutilisable pour un futur fine-tuning correctif.

Cette étape ne prétend pas que le modèle est corrigé dans ses poids. Elle prouve que le pipeline MLOps NCC peut :

1. détecter une régression réelle ;
2. empêcher sa validation ;
3. générer un dataset de réparation ;
4. appliquer une couche de génération gouvernée ;
5. mesurer séparément le comportement brut et le comportement sécurisé.
""",
        encoding="utf-8",
    )

    print("=== EXP 16: Safety Regression Repair Pack ===")
    print(f"Raw records:              {repair_summary['raw_records']}")
    print(f"Guarded count:            {repair_summary['guarded_count']}")
    print(f"Repair examples:          {repair_summary['repair_examples']}")
    print(f"Raw unsafe findings:      {raw_unsafe}")
    print(f"Guarded unsafe findings:  {guarded_unsafe}")
    print(f"Guard fixed regression:   {report['guard_fixed_regression']}")
    print(f"Verdict:                  {verdict}")
    print(f"Report written to:        {REPORT_MD}")

    if verdict != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
