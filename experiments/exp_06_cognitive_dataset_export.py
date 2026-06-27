from pathlib import Path

from ncc.dataset_export import (
    export_cognitive_dataset,
    export_sft_dataset,
    export_multitask_dataset,
    write_manifest,
    write_datasheet,
)


REPORTS_DIR = Path("reports")
DATASETS_DIR = Path("datasets")
DATASETS_DIR.mkdir(exist_ok=True)


TRACE_FILES = [
    REPORTS_DIR / "exp_01_traces.jsonl",
    REPORTS_DIR / "exp_02_memory_reactivation_traces.jsonl",
    REPORTS_DIR / "exp_02b_memory_source_attribution_traces.jsonl",
    REPORTS_DIR / "exp_02c_pure_memory_reactivation_traces.jsonl",
    REPORTS_DIR / "exp_03_governance_block_traces.jsonl",
    REPORTS_DIR / "exp_04_feedback_consolidation_traces.jsonl",
    REPORTS_DIR / "exp_05_knowledge_memory_separation_traces.jsonl",
]


COGNITIVE_DATASET_PATH = DATASETS_DIR / "ncc_cognitive_dataset.jsonl"
SFT_DATASET_PATH = DATASETS_DIR / "ncc_sft_dataset.jsonl"
MULTITASK_DATASET_PATH = DATASETS_DIR / "ncc_multitask_dataset.jsonl"
MANIFEST_PATH = DATASETS_DIR / "ncc_dataset_manifest.json"
DATASHEET_PATH = DATASETS_DIR / "ncc_dataset_datasheet.md"
REPORT_PATH = REPORTS_DIR / "exp_06_cognitive_dataset_export_report.md"


def main():
    existing_trace_files = [path for path in TRACE_FILES if path.exists()]

    report = export_cognitive_dataset(
        trace_paths=existing_trace_files,
        output_path=COGNITIVE_DATASET_PATH,
    )

    export_sft_dataset(
        cognitive_dataset_path=COGNITIVE_DATASET_PATH,
        output_path=SFT_DATASET_PATH,
    )

    export_multitask_dataset(
        cognitive_dataset_path=COGNITIVE_DATASET_PATH,
        output_path=MULTITASK_DATASET_PATH,
    )

    report.output_files.extend([
        str(SFT_DATASET_PATH),
        str(MULTITASK_DATASET_PATH),
        str(MANIFEST_PATH),
        str(DATASHEET_PATH),
    ])

    write_manifest(report, MANIFEST_PATH)
    write_datasheet(report, DATASHEET_PATH)

    verdict_schema = "OK" if report.schema_validity >= 1.0 else "À améliorer"
    verdict_target = "OK" if report.target_completeness >= 0.9 else "À améliorer"
    verdict_layers = "OK" if report.layer_separation_integrity >= 0.9 else "À améliorer"

    md = f"""# EXP-06 — Cognitive Dataset Export Report

## Objectif

Exporter les traces NCC-V0 en dataset cognitif exploitable pour préparer NCC-LM.

## Entrées

```text
{[str(path) for path in existing_trace_files]}
```

## Sorties

```text
{report.output_files}
```

## Scores

```text
Schema Validity = {report.schema_validity}
Target Completeness = {report.target_completeness}
Layer Separation Integrity = {report.layer_separation_integrity}
```

## Verdicts

```text
Schema = {verdict_schema}
Targets = {verdict_target}
Layer Separation = {verdict_layers}
```

## Exemples

```text
Total examples = {report.total_examples}
Exported examples = {report.exported_examples}
Skipped examples = {report.skipped_examples}
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
"""

    REPORT_PATH.write_text(md, encoding="utf-8")

    print(f"Schema Validity: {report.schema_validity}")
    print(f"Target Completeness: {report.target_completeness}")
    print(f"Layer Separation Integrity: {report.layer_separation_integrity}")
    print(f"Exported examples: {report.exported_examples}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
