#!/usr/bin/env bash
set -e
source .venv/bin/activate
python -m ncc.cli demo
pytest
python experiments/exp_01_intent_preservation.py
