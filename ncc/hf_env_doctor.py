from __future__ import annotations

import importlib
import json
import platform
import sys
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


DEFAULT_SFT_DATASET_PATH = Path("datasets/sft/ncc_sft_hf_text.jsonl")
DEFAULT_BASE_MODEL = "sshleifer/tiny-gpt2"


@dataclass
class DependencyCheck:
    name: str
    installed: bool
    version: str | None = None
    error: str | None = None


@dataclass
class PythonCheck:
    executable: str
    version: str
    major: int
    minor: int
    micro: int
    recommended: bool
    reason: str


@dataclass
class TorchCheck:
    dependency: DependencyCheck
    cuda_available: bool
    mps_available: bool
    selected_device: str
    device_reason: str


@dataclass
class DatasetCheck:
    path: str
    exists: bool
    line_count: int
    error: str | None = None


@dataclass
class HFEnvironmentReport:
    status: str
    python: PythonCheck
    torch: TorchCheck
    transformers: DependencyCheck
    accelerate: DependencyCheck
    safetensors: DependencyCheck
    dataset: DatasetCheck
    base_model: str
    recommended_commands: list[str]
    notes: list[str]


def check_dependency(package_name: str, import_name: str | None = None) -> DependencyCheck:
    import_name = import_name or package_name

    try:
        package_version = version(package_name)
    except PackageNotFoundError:
        return DependencyCheck(
            name=package_name,
            installed=False,
            error="package_not_installed",
        )
    except Exception as exc:
        return DependencyCheck(
            name=package_name,
            installed=False,
            error=f"package_version_error: {exc}",
        )

    try:
        importlib.import_module(import_name)
    except Exception as exc:
        return DependencyCheck(
            name=package_name,
            installed=False,
            version=package_version,
            error=f"import_error: {exc}",
        )

    return DependencyCheck(
        name=package_name,
        installed=True,
        version=package_version,
        error=None,
    )


def inspect_python() -> PythonCheck:
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    recommended = major == 3 and minor in {11, 12}

    if recommended:
        reason = "Python version compatible with the NCC HF smoke-test target."
    elif major == 3 and minor >= 13:
        reason = "Python version is too new for reliable local torch availability in this project."
    elif major == 3 and minor < 11:
        reason = "Python version is older than the recommended NCC HF target."
    else:
        reason = "Unsupported Python version for this NCC HF runner."

    return PythonCheck(
        executable=sys.executable,
        version=platform.python_version(),
        major=major,
        minor=minor,
        micro=micro,
        recommended=recommended,
        reason=reason,
    )


def inspect_torch() -> TorchCheck:
    dependency = check_dependency("torch")

    if not dependency.installed:
        return TorchCheck(
            dependency=dependency,
            cuda_available=False,
            mps_available=False,
            selected_device="none",
            device_reason="torch_not_available",
        )

    try:
        import torch

        cuda_available = bool(torch.cuda.is_available())

        mps_available = False
        if hasattr(torch.backends, "mps"):
            mps_available = bool(torch.backends.mps.is_available())

        if cuda_available:
            selected_device = "cuda"
            device_reason = "CUDA is available."
        elif mps_available:
            selected_device = "mps"
            device_reason = "Apple Silicon MPS is available."
        else:
            selected_device = "cpu"
            device_reason = "Torch is installed but no GPU/MPS accelerator was detected."

        return TorchCheck(
            dependency=dependency,
            cuda_available=cuda_available,
            mps_available=mps_available,
            selected_device=selected_device,
            device_reason=device_reason,
        )

    except Exception as exc:
        return TorchCheck(
            dependency=DependencyCheck(
                name="torch",
                installed=False,
                version=dependency.version,
                error=f"torch_runtime_error: {exc}",
            ),
            cuda_available=False,
            mps_available=False,
            selected_device="none",
            device_reason="torch_runtime_error",
        )


def inspect_dataset(path: str | Path = DEFAULT_SFT_DATASET_PATH) -> DatasetCheck:
    dataset_path = Path(path)

    if not dataset_path.exists():
        return DatasetCheck(
            path=str(dataset_path),
            exists=False,
            line_count=0,
            error="dataset_missing",
        )

    try:
        line_count = 0
        with dataset_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    line_count += 1

        return DatasetCheck(
            path=str(dataset_path),
            exists=True,
            line_count=line_count,
            error=None,
        )

    except Exception as exc:
        return DatasetCheck(
            path=str(dataset_path),
            exists=False,
            line_count=0,
            error=f"dataset_read_error: {exc}",
        )


def build_recommended_commands() -> list[str]:
    return [
        "python3.11 -m venv .venv-hf",
        "source .venv-hf/bin/activate",
        "python -m pip install -U pip setuptools wheel",
        "python -m pip install -U -r requirements-hf.txt",
        "python experiments/exp_14_real_hf_environment_doctor.py",
        "python experiments/exp_11_local_tiny_causal_lm_smoke_test.py",
    ]


def determine_status(
    python_check: PythonCheck,
    torch_check: TorchCheck,
    transformers_check: DependencyCheck,
    accelerate_check: DependencyCheck,
    safetensors_check: DependencyCheck,
    dataset_check: DatasetCheck,
) -> tuple[str, list[str]]:
    notes: list[str] = []

    if not dataset_check.exists:
        notes.append("Dataset SFT HF missing. Run V0.13 / make exp10 first.")
        return "BLOCKED_DATASET_MISSING", notes

    if not python_check.recommended:
        notes.append("Create a dedicated Python 3.11 or 3.12 environment for HF training.")
        notes.append(python_check.reason)
        return "BLOCKED_PYTHON_VERSION", notes

    missing = []
    for dep in [torch_check.dependency, transformers_check, accelerate_check, safetensors_check]:
        if not dep.installed:
            missing.append(dep.name)

    if missing:
        notes.append(f"Missing HF dependencies: {', '.join(missing)}")
        notes.append("Install requirements-hf.txt inside .venv-hf.")
        return "SKIPPED_HF_DEPENDENCIES_MISSING", notes

    if dataset_check.line_count <= 0:
        notes.append("Dataset exists but contains no usable examples.")
        return "BLOCKED_EMPTY_DATASET", notes

    notes.append("HF environment is ready for the NCC local causal LM smoke test.")
    notes.append(f"Selected device: {torch_check.selected_device}")
    return "READY", notes


def build_hf_environment_report(
    dataset_path: str | Path = DEFAULT_SFT_DATASET_PATH,
    base_model: str = DEFAULT_BASE_MODEL,
) -> HFEnvironmentReport:
    python_check = inspect_python()
    torch_check = inspect_torch()
    transformers_check = check_dependency("transformers")
    accelerate_check = check_dependency("accelerate")
    safetensors_check = check_dependency("safetensors")
    dataset_check = inspect_dataset(dataset_path)

    status, notes = determine_status(
        python_check=python_check,
        torch_check=torch_check,
        transformers_check=transformers_check,
        accelerate_check=accelerate_check,
        safetensors_check=safetensors_check,
        dataset_check=dataset_check,
    )

    return HFEnvironmentReport(
        status=status,
        python=python_check,
        torch=torch_check,
        transformers=transformers_check,
        accelerate=accelerate_check,
        safetensors=safetensors_check,
        dataset=dataset_check,
        base_model=base_model,
        recommended_commands=build_recommended_commands(),
        notes=notes,
    )


def write_hf_environment_report(
    report: HFEnvironmentReport,
    json_path: str | Path,
    markdown_path: str | Path,
) -> None:
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    report_dict = asdict(report)

    json_path.write_text(
        json.dumps(report_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    commands = "\n".join(report.recommended_commands)
    notes = "\n".join(f"- {note}" for note in report.notes)

    content = f"""# EXP-14 — Real HF Environment Doctor

## Objectif

Diagnostiquer l’environnement local requis pour exécuter le smoke test de fine-tuning causal HF du NCC.

## Statut

```text
{report.status}
```

## Python

```json
{json.dumps(asdict(report.python), ensure_ascii=False, indent=2)}
```

## Torch

```json
{json.dumps(asdict(report.torch), ensure_ascii=False, indent=2)}
```

## Dépendances HF

```json
{json.dumps({
    "transformers": asdict(report.transformers),
    "accelerate": asdict(report.accelerate),
    "safetensors": asdict(report.safetensors),
}, ensure_ascii=False, indent=2)}
```

## Dataset

```json
{json.dumps(asdict(report.dataset), ensure_ascii=False, indent=2)}
```

## Modèle de base

```text
{report.base_model}
```

## Notes

{notes}

## Commandes recommandées

```bash
{commands}
```

## Interprétation

Ce diagnostic ne prétend pas entraîner un modèle. Il vérifie si l’environnement local peut lancer le fine-tuning HF court introduit en V0.14. Si le statut est READY, le runner Python 3.11 peut exécuter EXP-11. Si le statut est BLOCKED ou SKIPPED, le rapport indique précisément la cause.
"""

    markdown_path.write_text(content, encoding="utf-8")
