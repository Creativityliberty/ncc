# Installation Mac — NCC-V0

## 1. Prérequis

Ouvre **Terminal**.

Installe les outils développeur Apple si besoin :

```bash
xcode-select --install
```

Installe Homebrew si tu ne l’as pas déjà :

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Installe Git, Python et Make :

```bash
brew install git python@3.11 make
```

Vérifie :

```bash
git --version
python3 --version
make --version
```

## 2. Créer l’environnement

Depuis le dossier du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 3. Lancer la démo

```bash
python -m ncc.cli demo
```

## 4. Lancer les tests

```bash
pytest
```

## 5. Lancer la première expérience

```bash
python experiments/exp_01_intent_preservation.py
```

## 6. Interpréter les résultats

Lis :

```text
reports/exp_01_intent_preservation_report.md
docs/RESULTS_INTERPRETATION_GUIDE.md
```

## 7. Ajouter plus tard un LLM local

Quand le moteur déterministe est stable, installe Ollama :

```bash
brew install ollama
ollama run llama3.2
```

Le LLM ne remplace pas NCC. Il devient seulement un module pour aider l’extraction d’intention, la génération de transformations et la rédaction.
