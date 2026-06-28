#!/usr/bin/env bash
set -euo pipefail

echo "=== NCC HF Python 3.11 Setup ==="

if ! command -v python3.11 >/dev/null 2>&1; then
  echo "python3.11 introuvable."
  echo "Installe Python 3.11 puis relance ce script."
  echo "Exemples possibles :"
  echo "  brew install python@3.11"
  echo "ou"
  echo "  pyenv install 3.11.9"
  exit 1
fi

python3.11 -m venv .venv-hf
source .venv-hf/bin/activate

python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements-hf.txt

PYTHONPATH=. python experiments/exp_14_real_hf_environment_doctor.py
