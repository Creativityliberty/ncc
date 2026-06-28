# EXP-17 — Safety Repair SFT Merge

## Objectif

Fusionner le dataset SFT original avec les exemples de réparation sécurité issus de V0.19.

## Résumé

```json
{
  "base_examples": 27,
  "repair_examples": 1,
  "repair_repeat": 3,
  "merged_examples": 30,
  "repair_ratio": 0.1,
  "unsafe_assistant_findings": 0,
  "output_path": "datasets/sft/ncc_sft_hf_text_v0_20_safety_merged.jsonl",
  "verdict": "OK"
}
```

## Interprétation

Cette étape vérifie que les exemples de réparation sécurité peuvent être intégrés dans un dataset SFT HF-compatible sans introduire de réponse assistant dangereuse.

Le but n'est pas encore de prouver que le modèle est corrigé. Le but est de créer une base d'entraînement corrigée, traçable et mesurable pour un re-fine-tuning court.
