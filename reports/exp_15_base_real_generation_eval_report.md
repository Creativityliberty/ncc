# EXP-15 — Real Generation Evaluation

## Source

```text
reports/exp_15_base_model_generations.jsonl
```

## Metrics

```json
{
  "total": 5,
  "average_score": 0.748,
  "unsafe_findings": 0,
  "used_fixtures": false,
  "verdict": "FAILED_LOW_SCORE",
  "by_task": {
    "intent": {
      "total": 1,
      "score_sum": 0.775,
      "average_score": 0.775
    },
    "governance": {
      "total": 3,
      "score_sum": 2.055,
      "average_score": 0.685
    },
    "general": {
      "total": 1,
      "score_sum": 0.91,
      "average_score": 0.91
    }
  }
}
```

## Verdict

```text
FAILED_LOW_SCORE
```

## Interprétation

Ce rapport évalue des générations réelles lorsque les fichiers EXP-11 existent. Le score mesure la structure minimale de sortie, les signaux cognitifs attendus et l’absence de génération dangereuse.
