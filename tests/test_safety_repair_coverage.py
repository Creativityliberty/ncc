# tests/test_safety_repair_coverage.py

from __future__ import annotations

from pathlib import Path

from ncc.safety_repair_coverage import (
    build_coverage_dataset,
    generate_safety_repair_coverage,
    unsafe_assistant_findings,
)


def test_generate_safety_repair_coverage_has_destructive_and_policy_examples():
    records = generate_safety_repair_coverage()

    assert records

    tags = [tag for row in records for tag in row.get("quality_tags", [])]

    assert "destructive_action_guard" in tags
    assert "safe_policy_rule" in tags
    assert "negative_policy_disambiguation" in tags


def test_safety_repair_coverage_records_are_safe():
    records = generate_safety_repair_coverage()

    findings = []

    for record in records:
        findings.extend(unsafe_assistant_findings(record))

    assert findings == []


def test_build_coverage_dataset(tmp_path: Path):
    output = tmp_path / "coverage.jsonl"

    report = build_coverage_dataset(output)

    assert report.verdict == "OK"
    assert report.generated_records > 0
    assert report.destructive_records > 0
    assert report.policy_records > 0
    assert report.unsafe_findings == 0
    assert output.exists()
