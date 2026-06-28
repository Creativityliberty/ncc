from __future__ import annotations

from pathlib import Path

from ncc.hf_env_doctor import (
    DatasetCheck,
    DependencyCheck,
    PythonCheck,
    TorchCheck,
    build_recommended_commands,
    determine_status,
    inspect_dataset,
)


def test_recommended_commands_include_py311_venv():
    commands = build_recommended_commands()
    joined = "\n".join(commands)

    assert "python3.11 -m venv .venv-hf" in joined
    assert "requirements-hf.txt" in joined
    assert "exp_14_real_hf_environment_doctor.py" in joined


def test_dataset_check_counts_jsonl_lines(tmp_path: Path):
    dataset = tmp_path / "sample.jsonl"
    dataset.write_text('{"a":1}\n\n{"b":2}\n', encoding="utf-8")

    check = inspect_dataset(dataset)

    assert check.exists is True
    assert check.line_count == 2
    assert check.error is None


def test_dataset_check_missing_file(tmp_path: Path):
    check = inspect_dataset(tmp_path / "missing.jsonl")

    assert check.exists is False
    assert check.line_count == 0
    assert check.error == "dataset_missing"


def test_status_blocks_bad_python_even_if_dataset_exists():
    python_check = PythonCheck(
        executable="python",
        version="3.14.0",
        major=3,
        minor=14,
        micro=0,
        recommended=False,
        reason="too new",
    )

    torch_check = TorchCheck(
        dependency=DependencyCheck(name="torch", installed=False),
        cuda_available=False,
        mps_available=False,
        selected_device="none",
        device_reason="torch_missing",
    )

    status, notes = determine_status(
        python_check=python_check,
        torch_check=torch_check,
        transformers_check=DependencyCheck(name="transformers", installed=False),
        accelerate_check=DependencyCheck(name="accelerate", installed=False),
        safetensors_check=DependencyCheck(name="safetensors", installed=False),
        dataset_check=DatasetCheck(path="dataset.jsonl", exists=True, line_count=10),
    )

    assert status == "BLOCKED_PYTHON_VERSION"
    assert notes


def test_status_skips_missing_hf_dependencies_on_good_python():
    python_check = PythonCheck(
        executable="python",
        version="3.11.9",
        major=3,
        minor=11,
        micro=9,
        recommended=True,
        reason="ok",
    )

    torch_check = TorchCheck(
        dependency=DependencyCheck(name="torch", installed=False),
        cuda_available=False,
        mps_available=False,
        selected_device="none",
        device_reason="torch_missing",
    )

    status, notes = determine_status(
        python_check=python_check,
        torch_check=torch_check,
        transformers_check=DependencyCheck(name="transformers", installed=False),
        accelerate_check=DependencyCheck(name="accelerate", installed=True, version="x"),
        safetensors_check=DependencyCheck(name="safetensors", installed=True, version="x"),
        dataset_check=DatasetCheck(path="dataset.jsonl", exists=True, line_count=10),
    )

    assert status == "SKIPPED_HF_DEPENDENCIES_MISSING"
    assert any("Missing HF dependencies" in note for note in notes)


def test_status_ready_when_everything_is_present():
    python_check = PythonCheck(
        executable="python",
        version="3.11.9",
        major=3,
        minor=11,
        micro=9,
        recommended=True,
        reason="ok",
    )

    torch_check = TorchCheck(
        dependency=DependencyCheck(name="torch", installed=True, version="x"),
        cuda_available=False,
        mps_available=True,
        selected_device="mps",
        device_reason="ok",
    )

    status, notes = determine_status(
        python_check=python_check,
        torch_check=torch_check,
        transformers_check=DependencyCheck(name="transformers", installed=True, version="x"),
        accelerate_check=DependencyCheck(name="accelerate", installed=True, version="x"),
        safetensors_check=DependencyCheck(name="safetensors", installed=True, version="x"),
        dataset_check=DatasetCheck(path="dataset.jsonl", exists=True, line_count=10),
    )

    assert status == "READY"
    assert notes
