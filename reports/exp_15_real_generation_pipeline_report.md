# EXP-15 — Real Generations Evaluation Pipeline

```json
{
  "base_generation_status": {
    "status": "OK",
    "output_path": "reports/exp_15_base_model_generations.jsonl",
    "count": 5,
    "device": "mps",
    "base_model": "sshleifer/tiny-gpt2"
  },
  "tuned_total": 3,
  "base_total": 5,
  "tuned_average_score": 0.765,
  "base_average_score": 0.748,
  "score_delta": 0.017,
  "relative_improvement": 0.023,
  "safety_regression": true,
  "verdict": "FAILED_SAFETY_REGRESSION"
}
```
