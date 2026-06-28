from __future__ import annotations

from ncc.hf_training_runner import HFTrainingRunnerResult


def test_training_runner_result_shape():
    result = HFTrainingRunnerResult(
        doctor_status="BLOCKED_PYTHON_VERSION",
        launched=False,
        command=["python", "script.py"],
        returncode=None,
        stdout_tail=None,
        stderr_tail=None,
        verdict="SKIPPED_NOT_READY",
    )

    assert result.launched is False
    assert result.verdict == "SKIPPED_NOT_READY"
    assert result.command == ["python", "script.py"]
