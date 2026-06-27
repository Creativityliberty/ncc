from __future__ import annotations

import json
from pathlib import Path

from ncc.hf_adapter import try_transformers_tokenizer, validate_hf_text_dataset
from ncc.sft_format import export_sft_dataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "datasets" / "clean" / "ncc_cognitive_dataset.clean.jsonl"
OUTPUT_DIR = ROOT / "datasets" / "sft"
REPORT_PATH = ROOT / "reports" / "exp_10_tiny_sft_format_hf_adapter_report.md"


def write_markdown_report(
    sft_report: dict,
    hf_report: dict,
    tokenizer_report: dict,
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    verdict = "OK"
    if sft_report["accepted_examples"] <= 0:
        verdict = "À corriger"
    if not hf_report["loadable"]:
        verdict = "À corriger"
    if sft_report["format_validity"] < 0.95:
        verdict = "À améliorer"

    content = f"""# EXP-10 — Tiny SFT Format + Local HF Adapter

## Objectif

Valider la conversion du dataset cognitif NCC en format SFT conversationnel compatible avec un futur fine-tuning local.

Cette expérience ne lance pas encore un entraînement lourd. Elle vérifie que les exemples NCC peuvent être transformés en paires instruction/réponse structurée, en conversations et en texte compatible avec un pipeline Hugging Face.

## Données

```text
Source dataset = {sft_report["source_dataset"]}
Input examples = {sft_report["input_examples"]}
Accepted examples = {sft_report["accepted_examples"]}
Rejected examples = {sft_report["rejected_examples"]}
Train examples = {sft_report["train_examples"]}
Val examples = {sft_report["val_examples"]}
Test examples = {sft_report["test_examples"]}
```

## Métriques SFT

```json
{json.dumps(sft_report, ensure_ascii=False, indent=2)}
```

## Validation HF text

```json
{json.dumps(hf_report, ensure_ascii=False, indent=2)}
```

## Tokenizer optionnel

```json
{json.dumps(tokenizer_report, ensure_ascii=False, indent=2)}
```

## Sorties générées

```text
datasets/sft/ncc_sft_instruction.jsonl
datasets/sft/ncc_sft_conversations.jsonl
datasets/sft/ncc_sft_hf_text.jsonl
datasets/sft/ncc_sft_train.jsonl
datasets/sft/ncc_sft_val.jsonl
datasets/sft/ncc_sft_test.jsonl
datasets/sft/ncc_sft_manifest.json
datasets/sft/ncc_sft_validation_report.json
```

## Verdict

```text
Tiny SFT Format + Local HF Adapter = {verdict}
```

## Interprétation scientifique

V0.13 valide le passage du dataset cognitif NCC vers un format conversationnel standardisé. Le futur NCC-LM ne sera pas entraîné seulement à répondre naturellement, mais à produire une réponse structurée contenant l’intention, l’écart, la sortie stabilisée, l’action, la gouvernance et le résumé d’état.

Cette étape prépare le terrain pour une prochaine expérience de fine-tuning local léger.
"""

    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    sft_report = export_sft_dataset(SOURCE_PATH, OUTPUT_DIR)

    hf_path = OUTPUT_DIR / "ncc_sft_hf_text.jsonl"
    hf_report = validate_hf_text_dataset(hf_path)

    tokenizer_report = try_transformers_tokenizer(hf_path, tokenizer_name=None)

    write_markdown_report(sft_report, hf_report, tokenizer_report)

    print("=== EXP 10: Tiny SFT Format + Local HF Adapter ===")
    print(f"Input examples:     {sft_report['input_examples']}")
    print(f"Accepted examples:  {sft_report['accepted_examples']}")
    print(f"Rejected examples:  {sft_report['rejected_examples']}")
    print(f"Format validity:    {sft_report['format_validity']}")
    print(f"HF loadable:        {hf_report['loadable']}")
    print(f"Report written to:  {REPORT_PATH}")


if __name__ == "__main__":
    main()
