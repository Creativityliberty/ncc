from __future__ import annotations

from pathlib import Path
import json

from ncc.tiny_ncc_lm import (
    TinyNCCLM,
    asdict,
    load_multitask_examples,
    split_examples,
    write_jsonl,
)


DATASET_PATH = Path("datasets/clean/ncc_multitask_dataset.clean.jsonl")

TRAINING_DIR = Path("datasets/training")
MODEL_DIR = Path("models/tiny_ncc_lm_v0_12")
REPORTS_DIR = Path("reports")

TRAIN_PATH = TRAINING_DIR / "ncc_lm_tiny_train.jsonl"
VAL_PATH = TRAINING_DIR / "ncc_lm_tiny_val.jsonl"
TEST_PATH = TRAINING_DIR / "ncc_lm_tiny_test.jsonl"

MODEL_PATH = MODEL_DIR / "model.json"
MANIFEST_PATH = MODEL_DIR / "manifest.json"

REPORT_PATH = REPORTS_DIR / "exp_09_tiny_ncc_lm_training_report.md"
PREDICTIONS_PATH = REPORTS_DIR / "exp_09_tiny_ncc_lm_predictions.jsonl"


def rows_from_examples(examples):
    return [asdict(example) for example in examples]


def main():
    REPORTS_DIR.mkdir(exist_ok=True)
    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    examples = load_multitask_examples(DATASET_PATH)

    train, val, test = split_examples(examples)

    write_jsonl(TRAIN_PATH, rows_from_examples(train))
    write_jsonl(VAL_PATH, rows_from_examples(val))
    write_jsonl(TEST_PATH, rows_from_examples(test))

    model = TinyNCCLM()
    model.fit(train)

    val_metrics = model.evaluate(val)
    test_metrics = model.evaluate(test)

    predictions = model.predict_rows(test)
    write_jsonl(PREDICTIONS_PATH, predictions)

    model.save(MODEL_PATH)

    manifest = {
        "model_version": "tiny-ncc-lm-v0.12",
        "purpose": "training_dry_run",
        "dataset": str(DATASET_PATH),
        "train_examples": len(train),
        "val_examples": len(val),
        "test_examples": len(test),
        "model_path": str(MODEL_PATH),
        "predictions_path": str(PREDICTIONS_PATH),
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "limitations": [
            "Not a real foundation model fine-tune.",
            "Tiny local classifier for pipeline validation only.",
            "Accuracy is not the main scientific claim.",
        ],
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    dry_run_ok = (
        len(train) > 0
        and MODEL_PATH.exists()
        and PREDICTIONS_PATH.exists()
        and test_metrics.get("unsafe_prediction_findings", 0) == 0
    )

    verdict = "OK" if dry_run_ok else "À corriger"

    report = f"""# EXP-09 — Tiny NCC-LM Training Dry Run

## Objectif

Valider le premier pipeline local d’apprentissage NCC-LM.

Ce dry run ne prétend pas entraîner un vrai grand modèle de langage. Il vérifie que les datasets NCC propres peuvent être chargés, séparés, appris par un mini-modèle, sérialisés, évalués et utilisés pour produire des prédictions cognitives.

## Données

```text
Source dataset = {DATASET_PATH}
Train examples = {len(train)}
Val examples = {len(val)}
Test examples = {len(test)}
```

## Métriques validation

```json
{json.dumps(val_metrics, ensure_ascii=False, indent=2)}
```

## Métriques test

```json
{json.dumps(test_metrics, ensure_ascii=False, indent=2)}
```

## Sorties générées

```text
{TRAIN_PATH}
{VAL_PATH}
{TEST_PATH}
{MODEL_PATH}
{MANIFEST_PATH}
{PREDICTIONS_PATH}
```

## Verdict

```text
Tiny NCC-LM Dry Run = {verdict}
```

## Interprétation scientifique

V0.12 valide le passage d’un dataset cognitif propre vers un pipeline local minimal d’apprentissage. Le résultat ne doit pas être interprété comme un NCC-LM final, mais comme une preuve d’ingénierie que les traces NCC peuvent être converties en signaux supervisés, entraînées dans un modèle local, évaluées, sauvegardées et rejouées.

La prochaine étape sera de remplacer ce mini-classifieur par un vrai modèle séquence-à-séquence ou causal léger, lorsque le volume du dataset et l’environnement local seront suffisants.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("=== EXP 09: Tiny NCC-LM Training Dry Run ===")
    print(f"Train examples: {len(train)}")
    print(f"Val examples:   {len(val)}")
    print(f"Test examples:  {len(test)}")
    print(f"Val accuracy:   {val_metrics.get('accuracy')}")
    print(f"Test accuracy:  {test_metrics.get('accuracy')}")
    print(f"Unsafe findings: {test_metrics.get('unsafe_prediction_findings')}")
    print(f"Verdict: {verdict}")
    print(f"Report written to: {REPORT_PATH}")

if __name__ == "__main__":
    main()
