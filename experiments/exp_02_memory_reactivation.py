from pathlib import Path
from statistics import mean

from ncc.runtime import NCCRuntime
from ncc.metrics import delayed_intent_reactivation
from ncc.trace import JSONLTraceWriter


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

TRACE_PATH = REPORTS_DIR / "exp_02_memory_reactivation_traces.jsonl"
REPORT_PATH = REPORTS_DIR / "exp_02_memory_reactivation_report.md"


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


def main():
    runtime = NCCRuntime()
    writer = JSONLTraceWriter(TRACE_PATH)

    scores = []

    for step, user_input in enumerate(SCENARIO, start=1):
        result = runtime.step(user_input)

        writer.write({
            "experiment": "EXP-02 Memory Reactivation",
            "step": step,
            "input": user_input,
            "observation": result.observation.model_dump(),
            "intent": result.intent.model_dump(),
            "gap": result.gap.model_dump(),
            "stable_output": result.stable_output.model_dump(),
            "reasoning": result.reasoning.model_dump(),
            "action": result.action.model_dump(),
            "state_after_summary": result.state_after_summary,
        })

        if step == 5:
            score = delayed_intent_reactivation(
                REQUIRED_OLD_CONSTRAINTS,
                result.intent.constraints,
            )
            scores.append(score)

    avg_score = round(mean(scores), 3) if scores else 0.0
    verdict = "OK" if avg_score >= 0.75 else "À améliorer"

    report = f"""# EXP-02 — Memory Reactivation Report

## Objectif

Tester si NCC-V0.2 peut réactiver des contraintes anciennes sans que l’utilisateur les répète explicitement.

## Contraintes anciennes attendues

```text
{REQUIRED_OLD_CONSTRAINTS}
```

## Score DIR

```text
DIR = {avg_score}
Verdict = {verdict}
```

## Interprétation

Si DIR est supérieur ou égal à 0.75, le système réactive correctement les contraintes anciennes.

Si DIR est inférieur à 0.75, cela signifie que la mémoire ou l’intention active ne conserve pas suffisamment les contraintes nécessaires à l’action tardive.

## Trace

```text
{TRACE_PATH}
```

"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"DIR: {avg_score}")
    print(f"Verdict: {verdict}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
