#!/usr/bin/env bash
set -e

echo "[NCC] Création environnement Python..."
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

echo "[NCC] Installation terminée."
echo "Active ensuite : source .venv/bin/activate"
echo "Puis lance : python -m ncc.cli demo"
