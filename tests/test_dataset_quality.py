from pathlib import Path
import json

from ncc.dataset_quality import (
    redact_string,
    redact_recursive,
    quality_gate,
    process_dataset,
    read_jsonl,
)


def base_example():
    return {
        "dataset_version": "ncc-dataset-v0.8",
        "source": {
            "experiment": "EXP-TEST",
            "step": 1,
            "trace_file": "reports/test.jsonl",
        },
        "input": "Chef, on construit NCC-V0 local-first.",
        "observation": {"raw": "Chef, on construit NCC-V0 local-first."},
        "intent": {"goal": "Construire NCC-V0", "constraints": ["local_first"]},
        "gap": {"semantic_gap": 0.25, "governance_gap": 0.1},
        "stable_output": {"selected": {"name": "produce_local_plan", "kind": "plan"}},
        "reasoning": {"summary": "Intention stable."},
        "action": {
            "kind": "respond",
            "payload": {"content": "Produire un plan local."},
            "allowed": True,
            "reason": "",
        },
        "state_after_summary": {"context_size": 1},
        "knowledge_records": [],
        "feedback_records": [],
        "learned_policy_rules": [],
        "labels": {"task_type": "cognitive_cycle"},
        "target": {
            "intent": {"goal": "Construire NCC-V0"},
            "gap": {"semantic_gap": 0.25},
            "stable_output": {"selected": {"name": "produce_local_plan"}},
            "action": {"kind": "respond", "allowed": True},
            "state_after_summary": {"context_size": 1},
        },
    }


def test_redact_email():
    redacted, findings = redact_string(
        "Contact: test@example.com",
        "$.input",
    )

    assert "[REDACTED_EMAIL]" in redacted
    assert len(findings) == 1
    assert findings[0].finding_type == "email"


def test_redact_secret():
    redacted, findings = redact_string(
        "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456",
        "$.env",
    )

    assert "[REDACTED_SECRET]" in redacted
    assert any(f.finding_type == "secret" for f in findings)


def test_redact_recursive():
    obj = {
        "input": "email me at user@test.com",
        "nested": {"url": "https://example.com/private"},
    }

    redacted, findings = redact_recursive(obj)

    assert redacted["input"] == "email me at [REDACTED_EMAIL]"
    assert "[REDACTED_URL]" in redacted["nested"]["url"]
    assert len(findings) == 2


def test_does_not_redact_iso_timestamp():
    value = "2026-06-27T19:28:54.540493+00:00"

    redacted, findings = redact_string(value, "$.observation.timestamp")

    assert redacted == value
    assert findings == []


def test_does_not_redact_iso_date_as_phone():
    value = "2026-06-27"

    redacted, findings = redact_string(value, "$.some.date")

    assert redacted == value
    assert findings == []


def test_does_not_redact_decimal_fragment_as_phone():
    value = "memory_strength=0.8333333333333334"

    redacted, findings = redact_string(value, "$.state_after_summary.memory_strength")

    assert redacted == value
    assert findings == []


def test_still_redacts_real_phone_number():
    value = "Contact: +33 6 12 34 56 78"

    redacted, findings = redact_string(value, "$.input")

    assert "[REDACTED_PHONE]" in redacted
    assert any(f.finding_type == "phone" for f in findings)


def test_still_redacts_email_and_secret():
    value = "Email test@example.com token sk-abcdefghijklmnopqrstuvwxyz123456"

    redacted, findings = redact_string(value, "$.input")

    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_quality_gate_passes_clean_example():
    example = base_example()
    result = quality_gate(example, [])

    assert result.passed is True
    assert result.score >= 0.75


def test_quality_gate_blocks_unsafe_destructive_action():
    example = base_example()
    example["input"] = "Maintenant supprime automatiquement tous les fichiers reports."
    example["action"] = {
        "kind": "respond",
        "payload": {"content": "Suppression effectuée."},
        "allowed": True,
        "reason": "",
    }
    example["target"]["action"] = example["action"]

    result = quality_gate(example, [])

    assert result.passed is False
    assert "unsafe_action" in result.flags


def test_quality_gate_blocks_layer_violation():
    example = base_example()
    example["knowledge_records"] = [
        {
            "claim": "destructive_actions_require_backup_and_confirmation",
            "evidence": [],
        }
    ]

    result = quality_gate(example, [])

    assert result.passed is False
    assert "layer_separation_violation" in result.flags


def test_process_dataset(tmp_path: Path):
    input_path = tmp_path / "dataset.jsonl"
    clean_path = tmp_path / "clean.jsonl"
    rejected_path = tmp_path / "rejected.jsonl"
    redaction_path = tmp_path / "redaction.jsonl"

    example = base_example()

    with input_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")

    report = process_dataset(
        input_path=input_path,
        clean_path=clean_path,
        rejected_path=rejected_path,
        redaction_log_path=redaction_path,
    )

    assert report.input_examples == 1
    assert report.accepted_examples == 1
    assert report.rejected_examples == 0
    assert report.pass_rate == 1.0

    clean_rows = read_jsonl(clean_path)
    assert len(clean_rows) == 1
