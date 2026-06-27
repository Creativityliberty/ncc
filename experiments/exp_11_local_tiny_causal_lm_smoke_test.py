from __future__ import annotations

import json
import os
from pathlib import Path

from ncc.local_causal_lm import LocalCausalLmConfig, run_local_causal_lm_smoke_test


REPORT_PATH = Path("reports/exp_11_local_tiny_causal_lm_smoke_test_report.md")


def write_report(metrics: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    status = metrics.get("status")
    skipped = status == "skipped"

    if skipped:
        verdict = "SKIPPED"
    else:
        verdict = "OK" if metrics.get("unsafe_generation_findings", 1) == 0 else "À améliorer"

    content = f"""# EXP-11 — Local Tiny Causal LM Fine-Tuning Smoke Test

## Objectif

Valider le premier smoke test local de fine-tuning causal sur le dataset SFT NCC.

Cette expérience ne prétend pas entraîner un vrai NCC-LM final. Elle vérifie que le format SFT généré en V0.13 peut être chargé par un petit modèle causal local, tokenisé, entraîné pendant quelques pas, sauvegardé, puis utilisé pour produire des générations de test.

## Statut

```text
Status = {status}
Verdict = {verdict}
```

## Métriques

```json
{json.dumps(metrics, ensure_ascii=False, indent=2)}
```

## Interprétation scientifique

V0.14 valide le passage du dataset SFT NCC vers un pipeline local minimal de fine-tuning causal. Le résultat ne doit pas être interprété comme une preuve de performance linguistique ou cognitive du modèle. La contribution de cette étape est d’ingénierie : elle démontre que le corpus NCC peut être utilisé par un modèle causal local, sauvegardé comme checkpoint et rejoué pour produire des sorties testables.

La prochaine étape sera d’améliorer le contrôle de génération, d’ajouter une évaluation structurée des sorties NCC, puis de comparer le modèle fine-tuné à un modèle non fine-tuné sur les mêmes prompts.
"""

    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    config = LocalCausalLmConfig(
        dataset_path=Path(os.getenv("NCC_SFT_HF_TEXT", "datasets/sft/ncc_sft_hf_text.jsonl")),
        model_name=os.getenv("NCC_BASE_MODEL", "sshleifer/tiny-gpt2"),
        output_dir=Path(os.getenv("NCC_CAUSAL_MODEL_DIR", "models/tiny_causal_ncc_lm_v0_14")),
        generations_path=Path(os.getenv("NCC_GENERATIONS_PATH", "reports/exp_11_tiny_causal_lm_generations.jsonl")),
        max_steps=int(os.getenv("NCC_TRAIN_MAX_STEPS", "5")),
        max_length=int(os.getenv("NCC_MAX_LENGTH", "256")),
    )

    metrics = run_local_causal_lm_smoke_test(config)
    write_report(metrics)

    print("=== EXP 11: Local Tiny Causal LM Fine-Tuning Smoke Test ===")
    print(f"Status: {metrics.get('status')}")
    print(f"Base model: {metrics.get('base_model')}")
    print(f"Train examples: {metrics.get('train_examples')}")
    print(f"Val examples:   {metrics.get('val_examples')}")
    print(f"Test examples:  {metrics.get('test_examples')}")
    print(f"Max steps:      {metrics.get('max_steps')}")
    print(f"Training loss:  {metrics.get('training_loss')}")
    print(f"Unsafe findings:{metrics.get('unsafe_generation_findings')}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
