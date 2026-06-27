from pathlib import Path

from ncc.dataset_quality import (
    process_dataset,
    read_jsonl,
    write_jsonl,
    write_quality_report_json,
)


DATASETS_DIR = Path("datasets")
CLEAN_DIR = DATASETS_DIR / "clean"
REPORTS_DIR = Path("reports")

COGNITIVE_INPUT = DATASETS_DIR / "ncc_cognitive_dataset.jsonl"
SFT_INPUT = DATASETS_DIR / "ncc_sft_dataset.jsonl"
MULTITASK_INPUT = DATASETS_DIR / "ncc_multitask_dataset.jsonl"

COGNITIVE_CLEAN = CLEAN_DIR / "ncc_cognitive_dataset.clean.jsonl"
SFT_CLEAN = CLEAN_DIR / "ncc_sft_dataset.clean.jsonl"
MULTITASK_CLEAN = CLEAN_DIR / "ncc_multitask_dataset.clean.jsonl"

REJECTED = CLEAN_DIR / "ncc_dataset_rejected.jsonl"
REDACTION_LOG = CLEAN_DIR / "ncc_redaction_log.jsonl"
QUALITY_JSON = CLEAN_DIR / "ncc_quality_report.json"

REPORT_MD = REPORTS_DIR / "exp_07_dataset_quality_gates_report.md"


def filter_related_sft_and_multitask() -> None:
    """
    Pour V0.9 simple :
    - on garde SFT et multitask redacted ;
    - le filtrage principal est fait sur le cognitive dataset.
    """
    for input_path, output_path in [
        (SFT_INPUT, SFT_CLEAN),
        (MULTITASK_INPUT, MULTITASK_CLEAN),
    ]:
        rows = read_jsonl(input_path)
        write_jsonl(output_path, rows)


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    report = process_dataset(
        input_path=COGNITIVE_INPUT,
        clean_path=COGNITIVE_CLEAN,
        rejected_path=REJECTED,
        redaction_log_path=REDACTION_LOG,
    )

    filter_related_sft_and_multitask()

    report.output_files.extend([
        str(SFT_CLEAN),
        str(MULTITASK_CLEAN),
        str(QUALITY_JSON),
        str(REPORT_MD),
    ])

    write_quality_report_json(report, QUALITY_JSON)

    verdict_quality = "OK" if report.pass_rate >= 0.9 else "À améliorer"
    verdict_security = "OK" if report.secret_findings == 0 else "À vérifier"
    verdict_safety = "OK" if report.unsafe_action_findings == 0 else "À corriger"

    md = f"""# EXP-07 — Dataset Quality Gates + Redaction Report

## Objectif

Vérifier, nettoyer et sécuriser le dataset NCC avant tout futur fine-tuning NCC-LM.

## Entrée

```text
{COGNITIVE_INPUT}
```

## Sorties

```text
{report.output_files}
```

## Scores

```text
Input examples = {report.input_examples}
Accepted examples = {report.accepted_examples}
Rejected examples = {report.rejected_examples}
Pass rate = {report.pass_rate}
Average quality score = {report.average_quality_score}
Redacted findings = {report.redacted_findings}
PII findings = {report.pii_findings}
Secret findings = {report.secret_findings}
Unsafe action findings = {report.unsafe_action_findings}
Malformed examples = {report.malformed_examples}
```

## Verdicts

```text
Quality = {verdict_quality}
Security = {verdict_security}
Action Safety = {verdict_safety}
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
"""

    REPORT_MD.write_text(md, encoding="utf-8")

    print(f"Pass rate: {report.pass_rate}")
    print(f"Average quality score: {report.average_quality_score}")
    print(f"Accepted examples: {report.accepted_examples}")
    print(f"Rejected examples: {report.rejected_examples}")
    print(f"Redacted findings: {report.redacted_findings}")
    print(f"Unsafe action findings: {report.unsafe_action_findings}")
    print(f"Report written to: {REPORT_MD}")


if __name__ == "__main__":
    main()
