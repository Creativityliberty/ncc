# experiments/exp_17_safety_repair_sft_merge_refinetune.py

from __future__ import annotations

import json
import os
from pathlib import Path

from ncc.generation_eval import aggregate_results, evaluate_generation, read_generation_records
from ncc.local_causal_lm import LocalCausalLmConfig, run_local_causal_lm_smoke_test
from ncc.safety_regression_repair import guard_generation, guarded_records_to_generation_jsonl
from ncc.safety_sft_merge import (
    merge_sft_with_safety_repairs,
    read_jsonl,
    write_jsonl,
    write_merge_report,
)


BASE_SFT = Path("datasets/sft/ncc_sft_hf_text.jsonl")
REPAIR_SFT = Path("datasets/sft/ncc_safety_repair_v0_19.jsonl")
MERGED_SFT = Path("datasets/sft/ncc_sft_hf_text_v0_20_safety_merged.jsonl")

MODEL_DIR = Path("models/tiny_causal_ncc_lm_v0_20")
RAW_GENERATIONS = Path("reports/exp_17_tiny_causal_lm_generations.jsonl")
GUARDED_GENERATIONS = Path("reports/exp_17_guarded_tiny_causal_lm_generations.jsonl")

MERGE_REPORT_JSON = Path("reports/exp_17_safety_repair_sft_merge_report.json")
MERGE_REPORT_MD = Path("reports/exp_17_safety_repair_sft_merge_report.md")

FINAL_REPORT_JSON = Path("reports/exp_17_refinetune_smoke_report.json")
FINAL_REPORT_MD = Path("reports/exp_17_refinetune_smoke_report.md")


def evaluate_generations(path: Path) -> dict:
    records = read_generation_records(path)

    if not records:
        return {
            "records": 0,
            "unsafe_findings": None,
            "average_score": None,
            "status": "no_generations",
        }

    results = [evaluate_generation(record) for record in records]
    metrics = aggregate_results(results)
    metrics["records"] = len(records)
    metrics["status"] = "ok"

    return metrics


def main() -> None:
    merge_report = merge_sft_with_safety_repairs(
        base_sft_path=BASE_SFT,
        repair_sft_path=REPAIR_SFT,
        output_path=MERGED_SFT,
        repair_repeat=int(os.getenv("NCC_SAFETY_REPAIR_REPEAT", "3")),
    )

    write_merge_report(
        report=merge_report,
        json_path=MERGE_REPORT_JSON,
        markdown_path=MERGE_REPORT_MD,
    )

    training_metrics = {
        "status": "skipped",
        "reason": "merge_not_ok",
    }

    if merge_report.verdict == "OK":
        config = LocalCausalLmConfig(
            dataset_path=MERGED_SFT,
            model_name=os.getenv("NCC_BASE_MODEL", "sshleifer/tiny-gpt2"),
            output_dir=MODEL_DIR,
            generations_path=RAW_GENERATIONS,
            max_steps=int(os.getenv("NCC_TRAIN_MAX_STEPS", "8")),
            max_length=int(os.getenv("NCC_MAX_LENGTH", "256")),
        )

        training_metrics = run_local_causal_lm_smoke_test(config)

    raw_eval = evaluate_generations(RAW_GENERATIONS)

    raw_records = read_jsonl(RAW_GENERATIONS)
    guarded = [guard_generation(record) for record in raw_records]

    write_jsonl(
        GUARDED_GENERATIONS,
        guarded_records_to_generation_jsonl(guarded),
    )

    guarded_eval = evaluate_generations(GUARDED_GENERATIONS)

    raw_unsafe = raw_eval.get("unsafe_findings")
    guarded_unsafe = guarded_eval.get("unsafe_findings")

    verdict = "OK"

    if merge_report.verdict != "OK":
        verdict = "FAILED_MERGE"
    elif training_metrics.get("status") == "skipped":
        verdict = "SKIPPED_TRAINING"
    elif raw_eval.get("records", 0) <= 0:
        verdict = "FAILED_NO_GENERATIONS"
    elif guarded_unsafe not in (0, None):
        verdict = "FAILED_GUARDED_UNSAFE"
    elif raw_unsafe not in (0, None):
        verdict = "OK_WITH_RAW_MODEL_STILL_UNSAFE"

    report = {
        "merge_report": merge_report.__dict__,
        "training_metrics": training_metrics,
        "raw_eval": raw_eval,
        "guarded_eval": guarded_eval,
        "raw_model_learned_safety": raw_unsafe == 0,
        "guarded_runtime_safe": guarded_unsafe == 0,
        "verdict": verdict,
    }

    FINAL_REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    FINAL_REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    FINAL_REPORT_MD.write_text(
        f"""# EXP-17 — Safety Repair SFT Merge + Re-Fine-Tuning Smoke Test

## Objectif

Fusionner les exemples de réparation sécurité issus de V0.19 dans le dataset SFT, relancer un fine-tuning court, produire de nouvelles générations, puis évaluer le comportement brut et le comportement gouverné.

## Résumé

```json
{json.dumps(report, ensure_ascii=False, indent=2)}
```

## Interprétation

V0.20 vérifie si les contre-exemples de sécurité générés en V0.19 peuvent être réinjectés dans le corpus SFT pour améliorer le comportement du modèle.

Deux résultats doivent rester séparés :

1. `raw_model_learned_safety` indique si le modèle re-fine-tuné produit déjà des sorties sûres sans guard.
2. `guarded_runtime_safe` indique si le runtime gouverné bloque encore toute sortie dangereuse.

Le verdict `OK_WITH_RAW_MODEL_STILL_UNSAFE` n'est pas un échec complet. Il signifie que le guard protège correctement, mais que le modèle doit recevoir davantage de données de réparation ou un entraînement plus robuste.
""",
        encoding="utf-8",
    )

    print("=== EXP 17: Safety Repair SFT Merge + Re-Fine-Tuning Smoke Test ===")
    print(f"Merge verdict:           {merge_report.verdict}")
    print(f"Base examples:           {merge_report.base_examples}")
    print(f"Repair examples:         {merge_report.repair_examples}")
    print(f"Merged examples:         {merge_report.merged_examples}")
    print(f"Training status:         {training_metrics.get('status')}")
    print(f"Raw unsafe findings:     {raw_unsafe}")
    print(f"Guarded unsafe findings: {guarded_unsafe}")
    print(f"Verdict:                 {verdict}")
    print(f"Report written to:       {FINAL_REPORT_MD}")

    if verdict.startswith("FAILED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
