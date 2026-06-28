# experiments/exp_17b_safety_repair_coverage.py

from __future__ import annotations

from pathlib import Path

from ncc.safety_repair_coverage import build_coverage_dataset, write_report


OUTPUT = Path("datasets/sft/ncc_safety_repair_coverage_v0_20_1.jsonl")
REPORT_JSON = Path("reports/exp_17b_safety_repair_coverage_report.json")
REPORT_MD = Path("reports/exp_17b_safety_repair_coverage_report.md")


def main() -> None:
    report = build_coverage_dataset(OUTPUT)

    write_report(
        report=report,
        json_path=REPORT_JSON,
        md_path=REPORT_MD,
    )

    print("=== EXP 17b: Safety Repair Coverage Pack ===")
    print(f"Generated records:   {report.generated_records}")
    print(f"Destructive records: {report.destructive_records}")
    print(f"Policy records:      {report.policy_records}")
    print(f"Unsafe findings:     {report.unsafe_findings}")
    print(f"Verdict:             {report.verdict}")
    print(f"Report written to:   {REPORT_MD}")

    if report.verdict != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
