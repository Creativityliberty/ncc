# EXP-15 — Real Base vs Tuned Comparison

## Metrics

```json
{
  "base_path": "reports/exp_15_base_model_generations.jsonl",
  "tuned_path": "reports/exp_11_tiny_causal_lm_generations.jsonl",
  "base_average_score": 0.748,
  "tuned_average_score": 0.765,
  "score_delta": 0.017,
  "relative_improvement": 0.023,
  "base_unsafe_findings": 0,
  "tuned_unsafe_findings": 1,
  "safety_regression": true,
  "verdict": "FAILED_SAFETY_REGRESSION"
}
```

## Verdict

```text
FAILED_SAFETY_REGRESSION
```

## Interprétation

Cette comparaison mesure si les générations du modèle fine-tuné NCC obtiennent un score cognitif supérieur à celles du modèle de base, sans régression de sécurité. Ce n’est pas encore une preuve de performance générale, mais un test expérimental local sur le corpus NCC actuel.
