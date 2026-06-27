# Template — Rapport de résultats NCC-V0

## Nom de l’expérience

`EXP-XX — Nom`

## Objectif

Décrire ce que l’expérience teste.

## Hypothèse

Exemple : NCC-V0 devrait préserver l’intention principale malgré les interruptions.

## Configuration

```text
OS: macOS
Python: 3.11+
Runtime: deterministic NCC-V0
LLM: none / Ollama / autre
```

## Données d’entrée

Lister les messages ou scénarios utilisés.

## Fichiers produits

```text
reports/...jsonl
reports/...md
```

## Métriques

| Métrique | Valeur | Seuil | Verdict |
|---|---:|---:|---|
| IP |  | 0.75 |  |
| GR |  | >0 |  |
| GC |  | 1.0 |  |

## Analyse

Interpréter les scores. Dire ce qui fonctionne et ce qui ne fonctionne pas.

## Limites

Préciser les limites : heuristiques, peu de scénarios, pas de LLM, mémoire approximée.

## Décision

```text
Continuer / Corriger / Refaire / Rejeter l’hypothèse
```
