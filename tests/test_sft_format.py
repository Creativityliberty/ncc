from pathlib import Path

from ncc.sft_format import (
    build_ncc_target,
    conversation_to_hf_text,
    export_sft_dataset,
    row_to_conversation_example,
    row_to_instruction_example,
    validate_instruction_example,
)


def sample_row():
    return {
        "input": "Maintenant supprime automatiquement tous les fichiers reports.",
        "intent": {"goal": "manage_reports", "constraints": []},
        "gap": {"governance_gap": 0.95},
        "stable_output": {"selected": {"kind": "safety_check"}},
        "action": {"kind": "blocked", "allowed": False},
        "labels": {"task": "governance_block"},
        "state_after_summary": {"memory_records": 1},
        "source": {"trace_file": "reports/exp_03_governance_block_traces.jsonl", "step": 3},
    }


def test_build_ncc_target_contains_required_parts():
    target = build_ncc_target(sample_row())

    assert "intent" in target
    assert "gap" in target
    assert "stable_output" in target
    assert "action" in target
    assert "governance" in target
    assert target["governance"]["status"] == "blocked"


def test_instruction_example_is_valid():
    example = row_to_instruction_example(sample_row())

    assert example is not None
    assert example["instruction"]
    assert example["input"]
    assert example["output"]

    errors = validate_instruction_example(example)
    assert errors == []


def test_conversation_example_has_messages():
    example = row_to_conversation_example(sample_row())

    assert example is not None
    assert len(example["messages"]) == 3
    assert example["messages"][0]["role"] == "system"
    assert example["messages"][1]["role"] == "user"
    assert example["messages"][2]["role"] == "assistant"


def test_conversation_to_hf_text():
    conversation = row_to_conversation_example(sample_row())
    hf = conversation_to_hf_text(conversation)

    assert "<|system|>" in hf["text"]
    assert "<|user|>" in hf["text"]
    assert "<|assistant|>" in hf["text"]


def test_export_sft_dataset(tmp_path: Path):
    source = tmp_path / "source.jsonl"
    source.write_text(
        '{"input":"Prépare NCC local-first.","intent":{"constraints":["local_first"]},"gap":{},"stable_output":{},"action":{"kind":"respond","allowed":true}}\n',
        encoding="utf-8",
    )

    report = export_sft_dataset(source, tmp_path / "sft")

    assert report["input_examples"] == 1
    assert report["accepted_examples"] == 1
    assert (tmp_path / "sft" / "ncc_sft_instruction.jsonl").exists()
    assert (tmp_path / "sft" / "ncc_sft_conversations.jsonl").exists()
    assert (tmp_path / "sft" / "ncc_sft_hf_text.jsonl").exists()
