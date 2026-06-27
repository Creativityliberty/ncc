from pathlib import Path
from statistics import mean

from ncc.metrics import delayed_intent_reactivation
from ncc.reactivation import (
    detect_reactivation_sources,
    memory_trace_coverage,
    source_distribution,
)
from ncc.runtime import NCCRuntime
from ncc.trace import JSONLTraceWriter


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

TRACE_PATH = REPORTS_DIR / "exp_02c_pure_memory_reactivation_traces.jsonl"
REPORT_PATH = REPORTS_DIR / "exp_02c_pure_memory_reactivation_report.md"


SCENARIO = [
    "Chef, on veut créer une première version locale NCC pour Mac, local-first.",
    "Ajoute les tests unitaires.",
    "Mets les traces JSONL pour produire un dataset plus tard.",
    "Prépare aussi un rapport de résultats.",
    "Maintenant prépare l’installation.",
]

REQUIRED_OLD_CONSTRAINTS = [
    "target_os=mac",
    "local_first",
]


def main() -> None:
    runtime = NCCRuntime()
    writer = JSONLTraceWriter(TRACE_PATH)

    dir_scores = []
    memory_trace_scores = []
    final_sources = {}
    final_observation = None
    final_intent = None

    for step, user_input in enumerate(SCENARIO, start=1):
        if step == 5:
            runtime.temporal_limit = 0

        result = runtime.step(user_input)

        if step == 5:
            result.observation.temporal = []

        active_intent = getattr(runtime.state, "active_intent", None)
        knowledge = getattr(runtime.state, "knowledge", None)

        reactivation_source = detect_reactivation_sources(
            required_constraints=REQUIRED_OLD_CONSTRAINTS,
            current_constraints=result.intent.constraints,
            observation=result.observation,
            active_intent=active_intent,
            knowledge=knowledge,
        )

        writer.write(
            {
                "experiment": "EXP-02c Pure Memory Reactivation",
                "step": step,
                "input": user_input,
                "observation": result.observation.model_dump(),
                "intent": result.intent.model_dump(),
                "gap": result.gap.model_dump(),
                "stable_output": result.stable_output.model_dump(),
                "reasoning": result.reasoning.model_dump(),
                "action": result.action.model_dump(),
                "reactivation_source": reactivation_source,
                "state_after_summary": result.state_after_summary,
            }
        )

        if step == 5:
            dir_score = delayed_intent_reactivation(
                REQUIRED_OLD_CONSTRAINTS,
                result.intent.constraints,
            )
            memory_score = memory_trace_coverage(reactivation_source)

            dir_scores.append(dir_score)
            memory_trace_scores.append(memory_score)
            final_sources = reactivation_source
            final_observation = result.observation.model_dump()
            final_intent = result.intent.model_dump()

    avg_dir = round(mean(dir_scores), 3) if dir_scores else 0.0
    avg_memory_trace = round(mean(memory_trace_scores), 3) if memory_trace_scores else 0.0

    dir_verdict = "OK" if avg_dir >= 0.75 else "À améliorer"
    memory_verdict = "OK" if avg_memory_trace >= 0.75 else "Mémoire pure à améliorer"

    report = f"""# EXP-02c — Pure Memory Reactivation Report

## Objectif

Tester si NCC peut réactiver des contraintes anciennes depuis `memory_trace`
lorsque le contexte temporel est volontairement limité.

## Contraintes anciennes attendues

```text
{REQUIRED_OLD_CONSTRAINTS}
```

## Scores

```text
DIR = {avg_dir}
DIR verdict = {dir_verdict}

Memory Trace Coverage = {avg_memory_trace}
Memory verdict = {memory_verdict}
```

## Sources détectées au dernier tour

```json
{final_sources}
```

## Distribution des sources

```json
{source_distribution(final_sources)}
```

## Observation finale

```json
{final_observation}
```

## Intention finale

```json
{final_intent}
```

## Interprétation

Si DIR = 1.0 et Memory Trace Coverage >= 0.75, NCC ne se contente plus de conserver l’intention
par contexte temporel : il réactive effectivement des traces structurées depuis la mémoire.

Si DIR = 1.0 mais Memory Trace Coverage = 0.0, alors la mémoire pure reste insuffisante.

## Trace

```text
{TRACE_PATH}
```

"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"DIR: {avg_dir}")
    print(f"DIR verdict: {dir_verdict}")
    print(f"Memory Trace Coverage: {avg_memory_trace}")
    print(f"Memory verdict: {memory_verdict}")
    print(f"Sources: {final_sources}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
