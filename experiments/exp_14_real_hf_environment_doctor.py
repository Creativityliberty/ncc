from __future__ import annotations

from pathlib import Path

from ncc.hf_env_doctor import build_hf_environment_report, write_hf_environment_report


JSON_PATH = Path("reports/exp_14_hf_environment_doctor.json")
REPORT_PATH = Path("reports/exp_14_hf_environment_doctor_report.md")


def main() -> None:
    report = build_hf_environment_report()

    write_hf_environment_report(
        report=report,
        json_path=JSON_PATH,
        markdown_path=REPORT_PATH,
    )

    print("=== EXP 14: Real HF Environment Doctor ===")
    print(f"Status:        {report.status}")
    print(f"Python:        {report.python.version}")
    print(f"Python OK:     {report.python.recommended}")
    print(f"Torch:         {report.torch.dependency.installed}")
    print(f"Transformers:  {report.transformers.installed}")
    print(f"Accelerate:    {report.accelerate.installed}")
    print(f"Safetensors:   {report.safetensors.installed}")
    print(f"Device:        {report.torch.selected_device}")
    print(f"Dataset:       {report.dataset.path}")
    print(f"Dataset exists:{report.dataset.exists}")
    print(f"Dataset lines: {report.dataset.line_count}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
