# EXP-14 — Real HF Environment Doctor

## Objectif

Diagnostiquer l’environnement local requis pour exécuter le smoke test de fine-tuning causal HF du NCC.

## Statut

```text
READY
```

## Python

```json
{
  "executable": "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/.venv-hf/bin/python",
  "version": "3.11.12",
  "major": 3,
  "minor": 11,
  "micro": 12,
  "recommended": true,
  "reason": "Python version compatible with the NCC HF smoke-test target."
}
```

## Torch

```json
{
  "dependency": {
    "name": "torch",
    "installed": true,
    "version": "2.2.2",
    "error": null
  },
  "cuda_available": false,
  "mps_available": true,
  "selected_device": "mps",
  "device_reason": "Apple Silicon MPS is available."
}
```

## Dépendances HF

```json
{
  "transformers": {
    "name": "transformers",
    "installed": true,
    "version": "4.41.0",
    "error": null
  },
  "accelerate": {
    "name": "accelerate",
    "installed": true,
    "version": "1.14.0",
    "error": null
  },
  "safetensors": {
    "name": "safetensors",
    "installed": true,
    "version": "0.8.0",
    "error": null
  }
}
```

## Dataset

```json
{
  "path": "datasets/sft/ncc_sft_hf_text.jsonl",
  "exists": true,
  "line_count": 27,
  "error": null
}
```

## Modèle de base

```text
sshleifer/tiny-gpt2
```

## Notes

- HF environment is ready for the NCC local causal LM smoke test.
- Selected device: mps

## Commandes recommandées

```bash
python3.11 -m venv .venv-hf
source .venv-hf/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements-hf.txt
python experiments/exp_14_real_hf_environment_doctor.py
python experiments/exp_11_local_tiny_causal_lm_smoke_test.py
```

## Interprétation

Ce diagnostic ne prétend pas entraîner un modèle. Il vérifie si l’environnement local peut lancer le fine-tuning HF court introduit en V0.14. Si le statut est READY, le runner Python 3.11 peut exécuter EXP-11. Si le statut est BLOCKED ou SKIPPED, le rapport indique précisément la cause.
