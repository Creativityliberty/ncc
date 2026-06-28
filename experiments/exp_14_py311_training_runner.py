from __future__ import annotations

from ncc.hf_training_runner import run_training_if_ready, write_training_runner_report


def main() -> None:
    result = run_training_if_ready()
    write_training_runner_report(result)

    print("=== EXP 14: Python 3.11 HF Training Runner ===")
    print(f"Doctor status: {result.doctor_status}")
    print(f"Launched:      {result.launched}")
    print(f"Return code:   {result.returncode}")
    print(f"Verdict:       {result.verdict}")
    print("Report written to: reports/exp_14_hf_training_runner_report.md")


if __name__ == "__main__":
    main()
