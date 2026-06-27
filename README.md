# NCC-V0 — Local Cognitive Runtime for Mac

**NCC-V0** est la première version locale du laboratoire **Nümtema Cognitive Core**.

Le but n’est pas encore d’entraîner un nouveau grand modèle de langage. Le but est de construire un runtime cognitif minimal capable de produire des traces structurées : observation, intention, écart, transformation, mémoire, action, feedback et état suivant.

```text
NCC Runtime → NCC Traces → NCC Dataset → NCC Fine-Tuning → NCC-LM
```

## Vision

Un LLM classique produit principalement :

```text
texte → prédiction → réponse
```

NCC-V0 teste plutôt :

```text
observation → intention → écart → transformation → stabilisation → mémoire → raisonnement → gouvernance → action → feedback → consolidation
```

## Ce que contient cette V0

```text
ncc-v0/
  ncc/                 moteur Python minimal
  tests/               tests unitaires
  experiments/         scénarios expérimentaux
  data/scenarios/      cas d’usage JSON
  reports/             rapports générés
  docs/                documentation scientifique et protocole
  scripts/             scripts d’installation Mac
```

## Démarrage rapide Mac

```bash
chmod +x scripts/setup_mac.sh scripts/run_demo.sh
./scripts/setup_mac.sh
source .venv/bin/activate
python -m ncc.cli demo
pytest
python experiments/exp_01_intent_preservation.py
```

Les traces sont générées dans :

```text
reports/traces.jsonl
reports/exp_01_intent_preservation_report.md
```

## Lecture des résultats

Voir :

```text
docs/RESULTS_INTERPRETATION_GUIDE.md
```

## Principe scientifique

Cette V0 prouve seulement une chose : un cycle NCC borné, traçable et testable peut être exécuté localement. Elle ne prouve pas encore une convergence globale, une AGI, ni une supériorité empirique. Ces points devront être évalués par benchmark.
