# EXP-17b — Safety Repair Coverage Pack

## Résumé

```json
{
  "generated_records": 12,
  "destructive_records": 8,
  "policy_records": 4,
  "unsafe_findings": 0,
  "output_path": "datasets/sft/ncc_safety_repair_coverage_v0_20_1.jsonl",
  "verdict": "OK"
}
```

## Interprétation

Cette expérience élargit le dataset de réparation sécurité avec deux familles :

1. des demandes destructives qui doivent être bloquées ;
2. des instructions de politique de sécurité qui doivent être acceptées et non bloquées.

Le but est d'éviter deux erreurs opposées :

* laisser passer une action destructive formulée différemment ;
* bloquer à tort une règle de gouvernance légitime.
