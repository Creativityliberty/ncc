# EXP-13 — Base Model vs Fine-Tuned Model Comparison Harness

## Objectif

Comparer les sorties d’un modèle de base et d’un modèle fine-tuné NCC sur les mêmes critères cognitifs : format NCC, sécurité, préservation d’intention, clarification, contradiction et précision des mises à jour de politique.

Cette expérience ne relance pas l’entraînement. Elle compare les générations disponibles. Si les fichiers de générations réelles n’existent pas encore, elle utilise des fixtures contrôlées.

## Sources

```text
Base generations path = reports/exp_13_base_model_generations.jsonl
Tuned generations path = reports/exp_11_tiny_causal_lm_generations.jsonl
Base used fixtures = True
Tuned used fixtures = True
```

## Résumé comparatif

```json
{
  "mode": "fixture",
  "base_model_label": "base_model",
  "tuned_model_label": "fine_tuned_ncc_model",
  "base_average_score": 0.769,
  "tuned_average_score": 0.957,
  "score_delta": 0.188,
  "relative_improvement": 0.244,
  "base_unsafe_findings": 0,
  "tuned_unsafe_findings": 0,
  "safety_regression": false,
  "task_deltas": {
    "clarification_needed": 0.179,
    "contradiction_handling": 0.179,
    "intent_preservation": 0.25,
    "policy_update": 0.143,
    "safe_destructive_handling": 0.193
  },
  "verdict": "OK"
}
```

## Verdict

```text
Base vs Fine-Tuned Comparison = OK
```

## Interprétation scientifique

V0.16 valide le banc de comparaison entre un modèle de base et un modèle adapté au format NCC. Cette étape est essentielle avant toute affirmation de progrès : un modèle fine-tuné ne doit pas seulement produire du texte, il doit améliorer le comportement cognitif attendu sans introduire de régression de sécurité. Lorsque le fine-tuning réel V0.14 sera exécuté dans un environnement compatible, le même harness pourra comparer les générations réelles.
