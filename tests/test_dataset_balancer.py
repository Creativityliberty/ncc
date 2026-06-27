from collections import Counter

from ncc.dataset_balancer import balance_report, normalized_entropy


def test_normalized_entropy_empty():
    assert normalized_entropy(Counter()) == 0.0


def test_balance_report_counts_tasks():
    examples = [
        {"scenario": {"scenario_type": "intent_preservation", "difficulty": "easy"}, "action": {"kind": "respond"}},
        {"scenario": {"scenario_type": "governance_block", "difficulty": "medium"}, "action": {"kind": "blocked"}},
    ]

    report = balance_report(examples)

    assert report["total_examples"] == 2
    assert report["task_counts"]["intent_preservation"] == 1
    assert report["task_counts"]["governance_block"] == 1
    assert report["action_counts"]["blocked"] == 1
    assert report["task_coverage"] > 0


def test_balance_report_detects_missing_tasks():
    examples = [
        {"scenario": {"scenario_type": "intent_preservation", "difficulty": "easy"}, "action": {"kind": "respond"}},
    ]

    report = balance_report(examples)

    assert "governance_block" in report["missing_tasks"]
