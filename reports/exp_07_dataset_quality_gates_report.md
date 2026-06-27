# EXP-07 — Dataset Quality Gates + Redaction Report

## Objectif

Vérifier, nettoyer et sécuriser le dataset NCC avant tout futur fine-tuning NCC-LM.

## Entrée

```text
datasets/ncc_cognitive_dataset.jsonl
```

## Sorties

```text
['datasets/clean/ncc_cognitive_dataset.clean.jsonl', 'datasets/clean/ncc_dataset_rejected.jsonl', 'datasets/clean/ncc_redaction_log.jsonl', 'datasets/clean/ncc_sft_dataset.clean.jsonl', 'datasets/clean/ncc_multitask_dataset.clean.jsonl', 'datasets/clean/ncc_quality_report.json', 'reports/exp_07_dataset_quality_gates_report.md']
```

## Scores

```text
Input examples = 27
Accepted examples = 27
Rejected examples = 0
Pass rate = 1.0
Average quality score = 1.0
Redacted findings = 0
PII findings = 0
Secret findings = 0
Unsafe action findings = 0
Malformed examples = 0
```

## Verdicts

```text
Quality = OK
Security = OK
Action Safety = OK
```

## Interprétation

Si `Pass rate >= 0.9`, le dataset est suffisamment propre pour servir de base expérimentale.

Si `Secret findings = 0`, aucun secret technique critique n’a été détecté.

Si `Unsafe action findings = 0`, aucune action destructive dangereuse n’est autorisée dans le dataset propre.

## Statut scientifique

EXP-07 ne prouve pas encore NCC-LM.
EXP-07 valide que les traces NCC peuvent être transformées en dataset cognitif filtré, anonymisé et gouverné.

Cette étape est nécessaire avant :

* fine-tuning ;
* génération synthétique ;
* benchmark interne ;
* apprentissage multitâche.
