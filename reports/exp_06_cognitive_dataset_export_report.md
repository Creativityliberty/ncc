# EXP-06 — Cognitive Dataset Export Report

## Objectif

Exporter les traces NCC-V0 en dataset cognitif exploitable pour préparer NCC-LM.

## Entrées

```text
['reports/exp_01_traces.jsonl', 'reports/exp_02_memory_reactivation_traces.jsonl', 'reports/exp_02b_memory_source_attribution_traces.jsonl', 'reports/exp_02c_pure_memory_reactivation_traces.jsonl', 'reports/exp_03_governance_block_traces.jsonl', 'reports/exp_04_feedback_consolidation_traces.jsonl', 'reports/exp_05_knowledge_memory_separation_traces.jsonl']
```

## Sorties

```text
['datasets/ncc_cognitive_dataset.jsonl', 'datasets/ncc_sft_dataset.jsonl', 'datasets/ncc_multitask_dataset.jsonl', 'datasets/ncc_dataset_manifest.json', 'datasets/ncc_dataset_datasheet.md']
```

## Scores

```text
Schema Validity = 1.0
Target Completeness = 1.0
Layer Separation Integrity = 1.0
```

## Verdicts

```text
Schema = OK
Targets = OK
Layer Separation = OK
```

## Exemples

```text
Total examples = 42
Exported examples = 27
Skipped examples = 15
```

## Interprétation

Si Schema Validity = 1.0, chaque ligne exportée respecte le schéma `CognitiveDatasetExample`.

Si Target Completeness >= 0.9, le dataset contient suffisamment de cibles cognitives pour entraîner les sous-tâches :

* intention ;
* écart ;
* transformation stabilisée ;
* action ;
* état futur.

Si Layer Separation Integrity >= 0.9, les couches mémoire / connaissance / politique restent propres dans le dataset.

## Statut scientifique

EXP-06 ne prouve pas encore NCC-LM.
EXP-06 valide que NCC-V0 produit des traces convertibles en dataset cognitif structuré.
