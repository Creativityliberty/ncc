from __future__ import annotations

from ncc.model_comparison import (
    base_fixture_generation_records,
    compare_model_results,
    evaluate_records,
    tuned_fixture_generation_records,
)


def test_finetuned_fixture_beats_base_fixture():
    base_result, _ = evaluate_records(
        base_fixture_generation_records(),
        model_label="base_model",
    )

    tuned_result, _ = evaluate_records(
        tuned_fixture_generation_records(),
        model_label="fine_tuned_ncc_model",
    )

    summary = compare_model_results(
        base_result=base_result,
        tuned_result=tuned_result,
        mode="fixture",
    )

    assert summary.tuned_average_score >= summary.base_average_score
    assert summary.score_delta >= 0
    assert summary.tuned_unsafe_findings == 0
    assert not summary.safety_regression
    assert summary.verdict == "OK"


def test_safety_regression_detected():
    base_result, _ = evaluate_records(
        tuned_fixture_generation_records(),
        model_label="base_model",
    )

    tuned_result, _ = evaluate_records(
        base_fixture_generation_records(),
        model_label="fine_tuned_ncc_model",
    )

    summary = compare_model_results(
        base_result=base_result,
        tuned_result=tuned_result,
        mode="fixture",
    )

    assert summary.verdict in {"SAFETY_REGRESSION", "À améliorer"}
    assert summary.score_delta <= 0


def test_task_deltas_are_computed():
    base_result, _ = evaluate_records(
        base_fixture_generation_records(),
        model_label="base_model",
    )

    tuned_result, _ = evaluate_records(
        tuned_fixture_generation_records(),
        model_label="fine_tuned_ncc_model",
    )

    summary = compare_model_results(
        base_result=base_result,
        tuned_result=tuned_result,
        mode="fixture",
    )

    assert isinstance(summary.task_deltas, dict)
    assert "clarification_needed" in summary.task_deltas
    assert "contradiction_handling" in summary.task_deltas
