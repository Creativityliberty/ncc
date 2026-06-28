# ncc/base_generation_runner.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ncc.real_generation_eval import (
    BASE_GENERATIONS_PATH,
    SFT_TEXT_PATH,
    TUNED_GENERATIONS_PATH,
    read_jsonl,
    write_jsonl,
)


DEFAULT_BASE_MODEL = "sshleifer/tiny-gpt2"


def _extract_prompt(row: dict[str, Any]) -> str:
    for key in ["prompt", "input", "instruction", "text", "source_prompt"]:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if isinstance(row.get("messages"), list):
        parts = []
        for msg in row["messages"]:
            if isinstance(msg, dict) and msg.get("role") in {"system", "user"}:
                content = msg.get("content")
                if isinstance(content, str):
                    parts.append(content)
        return "\n".join(parts).strip()

    return ""


def collect_prompts(
    tuned_generations_path: str | Path = TUNED_GENERATIONS_PATH,
    fallback_sft_path: str | Path = SFT_TEXT_PATH,
    limit: int = 5,
) -> list[str]:
    prompts: list[str] = []

    for source_path in [Path(tuned_generations_path), Path(fallback_sft_path)]:
        rows = read_jsonl(source_path)
        for row in rows:
            prompt = _extract_prompt(row)
            if prompt and prompt not in prompts:
                prompts.append(prompt)
            if len(prompts) >= limit:
                return prompts

    return prompts


def generate_base_model_outputs(
    output_path: str | Path = BASE_GENERATIONS_PATH,
    base_model: str = DEFAULT_BASE_MODEL,
    max_new_tokens: int = 96,
    limit: int = 5,
) -> dict[str, Any]:
    prompts = collect_prompts(limit=limit)

    if not prompts:
        return {
            "status": "FAILED_NO_PROMPTS",
            "output_path": str(output_path),
            "count": 0,
        }

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:
        return {
            "status": "SKIPPED_HF_DEPENDENCIES_MISSING",
            "error": str(exc),
            "output_path": str(output_path),
            "count": 0,
        }

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(base_model)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"

    model.to(device)
    model.eval()

    rows: list[dict[str, Any]] = []

    for index, prompt in enumerate(prompts, start=1):
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        if generated_text.startswith(prompt):
            generation = generated_text[len(prompt):].strip()
        else:
            generation = generated_text.strip()

        rows.append(
            {
                "model": base_model,
                "kind": "base",
                "index": index,
                "prompt": prompt,
                "generation": generation,
            }
        )

    write_jsonl(output_path, rows)

    return {
        "status": "OK",
        "output_path": str(output_path),
        "count": len(rows),
        "device": device,
        "base_model": base_model,
    }


def ensure_base_generations(path: str | Path = BASE_GENERATIONS_PATH) -> dict[str, Any]:
    path = Path(path)

    if path.exists() and path.stat().st_size > 0:
        return {
            "status": "EXISTS",
            "output_path": str(path),
            "count": len(read_jsonl(path)),
        }

    return generate_base_model_outputs(output_path=path)
