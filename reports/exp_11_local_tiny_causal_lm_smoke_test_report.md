# EXP-11 — Local Tiny Causal LM Fine-Tuning Smoke Test

## Objectif

Valider le premier smoke test local de fine-tuning causal sur le dataset SFT NCC.

Cette expérience ne prétend pas entraîner un vrai NCC-LM final. Elle vérifie que le format SFT généré en V0.13 peut être chargé par un petit modèle causal local, tokenisé, entraîné pendant quelques pas, sauvegardé, puis utilisé pour produire des générations de test.

## Statut

```text
Status = ok
Verdict = À améliorer
```

## Métriques

```json
{
  "model_version": "tiny-causal-ncc-lm-v0.14",
  "purpose": "local_tiny_causal_lm_finetuning_smoke_test",
  "base_model": "sshleifer/tiny-gpt2",
  "dataset_path": "datasets/sft/ncc_sft_hf_text.jsonl",
  "output_dir": "models/tiny_causal_ncc_lm_v0_14",
  "generations_path": "reports/exp_11_tiny_causal_lm_generations.jsonl",
  "total_examples": 27,
  "train_examples": 21,
  "val_examples": 3,
  "test_examples": 3,
  "max_steps": 5,
  "max_length": 256,
  "training_loss": 10.827506637573242,
  "generation_non_empty_rate": 1.0,
  "unsafe_generation_findings": 1,
  "status": "ok",
  "limitations": [
    "Smoke test only.",
    "Not a real NCC-LM final model.",
    "Tiny causal model used to validate the local fine-tuning pipeline.",
    "Generation quality is not the main claim."
  ]
}
```

## Interprétation scientifique

V0.14 valide le passage du dataset SFT NCC vers un pipeline local minimal de fine-tuning causal. Le résultat ne doit pas être interprété comme une preuve de performance linguistique ou cognitive du modèle. La contribution de cette étape est d’ingénierie : elle démontre que le corpus NCC peut être utilisé par un modèle causal local, sauvegardé comme checkpoint et rejoué pour produire des sorties testables.

La prochaine étape sera d’améliorer le contrôle de génération, d’ajouter une évaluation structurée des sorties NCC, puis de comparer le modèle fine-tuné à un modèle non fine-tuné sur les mêmes prompts.
