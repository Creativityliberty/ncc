from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from ncc.hf_env_doctor import (
    HFEnvironmentReport,
    build_hf_environment_report,
    write_hf_environment_report,
)


@dataclass
class HFTrainingRunnerResult:
    doctor_status: str
    launched: bool
    command: list[str]
    returncode: int | None
    stdout_tail: str | None
    stderr_tail: str | None
    verdict: str


def _tail(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def run_training_if_ready(
    training_script: str | Path = "experiments/exp_11_local_tiny_causal_lm_smoke_test.py",
    doctor_json_path: str | Path = "reports/exp_14_hf_environment_doctor.json",
    doctor_md_path: str | Path = "reports/exp_14_hf_environment_doctor_report.md",
) -> HFTrainingRunnerResult:
    report: HFEnvironmentReport = build_hf_environment_report()

    write_hf_environment_report(
        report=report,
        json_path=doctor_json_path,
        markdown_path=doctor_md_path,
    )

    command = [sys.executable, str(training_script)]

    if report.status != "READY":
        return HFTrainingRunnerResult(
            doctor_status=report.status,
            launched=False,
            command=command,
            returncode=None,
            stdout_tail=None,
            stderr_tail=None,
            verdict="SKIPPED_NOT_READY",
        )

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode == 0:
        verdict = "OK"
    else:
        verdict = "FAILED"

    return HFTrainingRunnerResult(
        doctor_status=report.status,
        launched=True,
        command=command,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
        verdict=verdict,
    )


def write_training_runner_report(
    result: HFTrainingRunnerResult,
    json_path: str | Path = "reports/exp_14_hf_training_runner.json",
    markdown_path: str | Path = "reports/exp_14_hf_training_runner_report.md",
) -> None:
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    result_dict = asdict(result)

    json_path.write_text(
        json.dumps(result_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    content = f"""# EXP-14 — Python 3.11 HF Training Runner

## Objectif

Lancer le smoke test de fine-tuning causal local uniquement si le diagnostic HF est READY.

## Résultat

```json
{json.dumps(result_dict, ensure_ascii=False, indent=2)}
```

## Verdict

```text
{result.verdict}
```

## Interprétation

Le runner ne force pas l’entraînement si l’environnement est incomplet. Il protège le pipeline en séparant le diagnostic de l’exécution. Lorsque le diagnostic indique READY, il lance EXP-11 dans l’environnement Python actif, idéalement `.venv-hf` basé sur Python 3.11 ou 3.12.
"""

    markdown_path.write_text(content, encoding="utf-8")
