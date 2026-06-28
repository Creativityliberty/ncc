#!/usr/bin/env bash
set -euo pipefail

echo "=== NCC HF Python 3.11 Training Runner ==="

if [ ! -d ".venv-hf" ]; then
  echo ".venv-hf introuvable."
  echo "Lance d'abord :"
  echo "  bash scripts/setup_hf_py311.sh"
  exit 1
fi

source .venv-hf/bin/activate

PYTHONPATH=. python experiments/exp_14_real_hf_environment_doctor.py
PYTHONPATH=. python experiments/exp_14_py311_training_runner.py
