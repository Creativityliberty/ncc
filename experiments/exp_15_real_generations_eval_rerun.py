# experiments/exp_15_real_generations_eval_rerun.py

from __future__ import annotations

import json
from pathlib import Path

from ncc.base_generation_runner import ensure_base_generations
from ncc.real_generation_eval import (
    BASE_GENERATIONS_PATH,
    TUNED_GENERATIONS_PATH,
    compare_generation_reports,
    evaluate_generation_file,
    write_generation_eval_report,
    write_model_comparison_report,
)


PIPELINE_REPORT_PATH = Path("reports/exp_15_real_generation_pipeline_report.md")


def main() -> None:
    print("=== EXP 15: Real Generations Evaluation + Base-vs-Tuned Re-run ===")

    if not TUNED_GENERATIONS_PATH.exists():
        raise SystemExit(
            f"Missing tuned generations: {TUNED_GENERATIONS_PATH}. "
            "Run V0.17 / EXP-11 real training first."
        )

    base_status = ensure_base_generations(BASE_GENERATIONS_PATH)

    tuned_report = evaluate_generation_file(TUNED_GENERATIONS_PATH, used_fixtures=False)
    base_report = evaluate_generation_file(BASE_GENERATIONS_PATH, used_fixtures=False)

    write_generation_eval_report(
        tuned_report,
        json_path="reports/exp_15_tuned_real_generation_eval.json",
        markdown_path="reports/exp_15_tuned_real_generation_eval_report.md",
    )

    write_generation_eval_report(
        base_report,
        json_path="reports/exp_15_base_real_generation_eval.json",
        markdown_path="reports/exp_15_base_real_generation_eval_report.md",
    )

    comparison = compare_generation_reports(base_report, tuned_report)

    write_model_comparison_report(
        comparison,
        json_path="reports/exp_15_real_base_vs_tuned_comparison.json",
        markdown_path="reports/exp_15_real_base_vs_tuned_comparison_report.md",
    )

    pipeline_summary = {
        "base_generation_status": base_status,
        "tuned_total": tuned_report.total,
        "base_total": base_report.total,
        "tuned_average_score": tuned_report.average_score,
        "base_average_score": base_report.average_score,
        "score_delta": comparison.score_delta,
        "relative_improvement": comparison.relative_improvement,
        "safety_regression": comparison.safety_regression,
        "verdict": comparison.verdict,
    }

    PIPELINE_REPORT_PATH.write_text(
        "# EXP-15 — Real Generations Evaluation Pipeline\n\n"
        "```json\n"
        + json.dumps(pipeline_summary, ensure_ascii=False, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )

    print(f"Base generation status: {base_status['status']}")
    print(f"Base average score:     {base_report.average_score}")
    print(f"Tuned average score:    {tuned_report.average_score}")
    print(f"Score delta:            {comparison.score_delta}")
    print(f"Relative improvement:   {comparison.relative_improvement}")
    print(f"Safety regression:      {comparison.safety_regression}")
    print(f"Verdict:                {comparison.verdict}")
    print(f"Report written to:      {PIPELINE_REPORT_PATH}")

    if comparison.verdict != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
