# EXP-09 — Tiny NCC-LM Training Dry Run

## Objectif

Valider le premier pipeline local d’apprentissage NCC-LM.

Ce dry run ne prétend pas entraîner un vrai grand modèle de langage. Il vérifie que les datasets NCC propres peuvent être chargés, séparés, appris par un mini-modèle, sérialisés, évalués et utilisés pour produire des prédictions cognitives.

## Données

```text
Source dataset = datasets/clean/ncc_multitask_dataset.clean.jsonl
Train examples = 75
Val examples = 16
Test examples = 17
```

## Métriques validation

```json
{
  "total": 16,
  "accuracy": 0.625,
  "by_task": {
    "predict_intent": {
      "total": 3,
      "correct": 2,
      "accuracy": 0.667
    },
    "predict_action": {
      "total": 4,
      "correct": 2,
      "accuracy": 0.5
    },
    "predict_gap": {
      "total": 8,
      "correct": 5,
      "accuracy": 0.625
    },
    "predict_stable_output": {
      "total": 1,
      "correct": 1,
      "accuracy": 1.0
    }
  },
  "unsafe_prediction_findings": 0
}
```

## Métriques test

```json
{
  "total": 17,
  "accuracy": 0.824,
  "by_task": {
    "predict_intent": {
      "total": 3,
      "correct": 2,
      "accuracy": 0.667
    },
    "predict_stable_output": {
      "total": 4,
      "correct": 3,
      "accuracy": 0.75
    },
    "predict_action": {
      "total": 6,
      "correct": 6,
      "accuracy": 1.0
    },
    "predict_gap": {
      "total": 4,
      "correct": 3,
      "accuracy": 0.75
    }
  },
  "unsafe_prediction_findings": 0
}
```

## Sorties générées

```text
datasets/training/ncc_lm_tiny_train.jsonl
datasets/training/ncc_lm_tiny_val.jsonl
datasets/training/ncc_lm_tiny_test.jsonl
models/tiny_ncc_lm_v0_12/model.json
models/tiny_ncc_lm_v0_12/manifest.json
reports/exp_09_tiny_ncc_lm_predictions.jsonl
```

## Verdict

```text
Tiny NCC-LM Dry Run = OK
```

## Interprétation scientifique

V0.12 valide le passage d’un dataset cognitif propre vers un pipeline local minimal d’apprentissage. Le résultat ne doit pas être interprété comme un NCC-LM final, mais comme une preuve d’ingénierie que les traces NCC peuvent être converties en signaux supervisés, entraînées dans un modèle local, évaluées, sauvegardées et rejouées.

La prochaine étape sera de remplacer ce mini-classifieur par un vrai modèle séquence-à-séquence ou causal léger, lorsque le volume du dataset et l’environnement local seront suffisants.
