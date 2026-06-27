from pathlib import Path

from ncc.runtime import NCCRuntime
from ncc.metrics import knowledge_memory_separation_score, layer_purity_score
from ncc.trace import JSONLTraceWriter


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

TRACE_PATH = REPORTS_DIR / "exp_05_knowledge_memory_separation_traces.jsonl"
REPORT_PATH = REPORTS_DIR / "exp_05_knowledge_memory_separation_report.md"


SCENARIO = [
    "Chef, on construit NCC-V0 local-first avec traces et rapports.",
    "Fait vérifié : CoALA organise les agents de langage autour de la mémoire, de l’espace d’action et de la décision.",
    "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation.",
    "Pourquoi la séparation mémoire / connaissance est importante ?",
    "Rappelle l’état cognitif séparé du projet.",
]


EXPECTED_KNOWLEDGE = "CoALA organise les agents de langage"
EXPECTED_POLICY = "destructive_actions_require_backup_and_confirmation"
MEMORY_MARKER = "local_first"


def main():
    runtime = NCCRuntime()
    writer = JSONLTraceWriter(TRACE_PATH)

    final_result = None

    for step, user_input in enumerate(SCENARIO, start=1):
        result = runtime.step(user_input)
        final_result = result

        payload = {
            "experiment": "EXP-05 Knowledge Memory Separation",
            "step": step,
            "input": user_input,
            "observation": result.observation.model_dump(),
            "intent": result.intent.model_dump(),
            "gap": result.gap.model_dump(),
            "stable_output": result.stable_output.model_dump(),
            "reasoning": result.reasoning.model_dump(),
            "action": result.action.model_dump(),
            "state_after_summary": result.state_after_summary,
            "knowledge_records": [
                record.model_dump()
                for record in getattr(runtime.state, "knowledge_records", [])
            ],
            "feedback_records": [
                record.model_dump()
                for record in getattr(runtime.state, "feedback_records", [])
            ],
            "learned_policy_rules": getattr(runtime.state, "learned_policy_rules", []),
        }

        writer.write(payload)

    memory_text = str([
        record.model_dump()
        for record in getattr(runtime.state, "memory", [])
    ]).lower()
    knowledge_text = str([
        record.model_dump()
        for record in getattr(runtime.state, "knowledge_records", [])
    ])
    policy_rules = getattr(runtime.state, "learned_policy_rules", [])

    memory_ok = MEMORY_MARKER.lower() in memory_text

    knowledge_ok = EXPECTED_KNOWLEDGE.lower() in knowledge_text.lower()

    policy_ok = EXPECTED_POLICY in policy_rules

    reasoning_not_persisted = not any(
        "pourquoi la séparation mémoire" in record.claim.lower()
        for record in getattr(runtime.state, "knowledge_records", [])
    )

    kms = knowledge_memory_separation_score(
        memory_ok=memory_ok,
        knowledge_ok=knowledge_ok,
        policy_ok=policy_ok,
        reasoning_not_persisted=reasoning_not_persisted,
    )

    total_items = (
        len(getattr(runtime.state, "knowledge_records", []))
        + len(getattr(runtime.state, "feedback_records", []))
        + len(getattr(runtime.state, "memory", []))
    )

    misplaced_items = 0

    if EXPECTED_POLICY.lower() in knowledge_text.lower():
        misplaced_items += 1

    if EXPECTED_KNOWLEDGE.lower() in " ".join(policy_rules).lower():
        misplaced_items += 1

    purity = layer_purity_score(
        total_items=total_items,
        misplaced_items=misplaced_items,
    )

    verdict_kms = "OK" if kms >= 1.0 else "À améliorer"
    verdict_purity = "OK" if purity >= 0.9 else "À améliorer"

    report = f"""# EXP-05 — Knowledge / Memory / Policy Separation Report

## Objectif

Tester si NCC distingue correctement mémoire, connaissance, politique et raisonnement temporaire.

## Scénario

```text
{SCENARIO}
```

## Scores

```text
KMS = {kms}
Layer Purity = {purity}
Verdict KMS = {verdict_kms}
Verdict Layer Purity = {verdict_purity}
```

## Vérifications

```text
memory_ok = {memory_ok}
knowledge_ok = {knowledge_ok}
policy_ok = {policy_ok}
reasoning_not_persisted = {reasoning_not_persisted}
```

## Interprétation

KMS = 1.0 signifie que :

* la demande projet reste une trace mémoire ;
* le fait vérifié est stocké comme connaissance ;
* le feedback de sécurité devient une règle/politique ;
* la question de raisonnement ne pollue pas la connaissance.

Layer Purity >= 0.9 signifie que les éléments cognitifs ne sont pas mélangés entre les couches.

## Trace

```text
{TRACE_PATH}
```

"""

    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"KMS: {kms}")
    print(f"Layer Purity: {purity}")
    print(f"Verdict KMS: {verdict_kms}")
    print(f"Verdict Layer Purity: {verdict_purity}")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
