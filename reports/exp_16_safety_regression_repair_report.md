# EXP-16 — Safety Regression Repair Pack + Guarded Generation Gate

## Objectif

Transformer la régression de sécurité détectée en V0.18 en contre-exemples de réparation, puis vérifier qu'une couche de génération gouvernée bloque les sorties dangereuses.

## Résumé

```json
{
  "repair_summary": {
    "raw_records": 3,
    "guarded_records": 3,
    "guarded_count": 1,
    "repair_examples": 1,
    "guarded_generations_path": "reports/exp_16_guarded_tuned_generations.jsonl",
    "repair_dataset_path": "datasets/sft/ncc_safety_repair_v0_19.jsonl"
  },
  "raw_metrics": {
    "average_score": 0.765,
    "unsafe_findings": 1
  },
  "guarded_metrics": {
    "average_score": 0.97,
    "unsafe_findings": 0
  },
  "raw_unsafe_findings": 1,
  "guarded_unsafe_findings": 0,
  "guard_fixed_regression": true,
  "verdict": "OK"
}
```

## Interprétation

V0.19 valide la boucle de réparation sécurité du NCC-LM. Le modèle brut peut encore produire une sortie dangereuse, mais le runtime gouverné doit détecter cette sortie, la remplacer par une réponse sécurisée et produire un exemple de réparation réutilisable pour un futur fine-tuning correctif.

Cette étape ne prétend pas que le modèle est corrigé dans ses poids. Elle prouve que le pipeline MLOps NCC peut :

1. détecter une régression réelle ;
2. empêcher sa validation ;
3. générer un dataset de réparation ;
4. appliquer une couche de génération gouvernée ;
5. mesurer séparément le comportement brut et le comportement sécurisé.
