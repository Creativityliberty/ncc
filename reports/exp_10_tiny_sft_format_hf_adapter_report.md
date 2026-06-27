# EXP-10 — Tiny SFT Format + Local HF Adapter

## Objectif

Valider la conversion du dataset cognitif NCC en format SFT conversationnel compatible avec un futur fine-tuning local.

Cette expérience ne lance pas encore un entraînement lourd. Elle vérifie que les exemples NCC peuvent être transformés en paires instruction/réponse structurée, en conversations et en texte compatible avec un pipeline Hugging Face.

## Données

```text
Source dataset = /Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/clean/ncc_cognitive_dataset.clean.jsonl
Input examples = 27
Accepted examples = 27
Rejected examples = 0
Train examples = 18
Val examples = 4
Test examples = 5
```

## Métriques SFT

```json
{
  "dataset_version": "ncc-sft-v0.13",
  "source_dataset": "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/clean/ncc_cognitive_dataset.clean.jsonl",
  "input_examples": 27,
  "accepted_examples": 27,
  "rejected_examples": 0,
  "format_validity": 1.0,
  "conversation_examples": 27,
  "hf_text_examples": 27,
  "train_examples": 18,
  "val_examples": 4,
  "test_examples": 5,
  "output_files": [
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_instruction.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_conversations.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_hf_text.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_train.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_val.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_test.jsonl",
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_rejected.jsonl"
  ]
}
```

## Validation HF text

```json
{
  "path": "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/datasets/sft/ncc_sft_hf_text.jsonl",
  "total": 27,
  "malformed": 0,
  "empty_text": 0,
  "min_basic_tokens": 189,
  "max_basic_tokens": 212,
  "avg_basic_tokens": 195.667,
  "loadable": true
}
```

## Tokenizer optionnel

```json
{
  "enabled": false,
  "reason": "no_tokenizer_name_provided"
}
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
Tiny SFT Format + Local HF Adapter = OK
```

## Interprétation scientifique

V0.13 valide le passage du dataset cognitif NCC vers un format conversationnel standardisé. Le futur NCC-LM ne sera pas entraîné seulement à répondre naturellement, mais à produire une réponse structurée contenant l’intention, l’écart, la sortie stabilisée, l’action, la gouvernance et le résumé d’état.

Cette étape prépare le terrain pour une prochaine expérience de fine-tuning local léger.
