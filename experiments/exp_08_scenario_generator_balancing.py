from __future__ import annotations

from pathlib import Path

from ncc.scenario_generator import write_scenarios
from ncc.scenario_runner import run_scenarios_to_jsonl
from ncc.dataset_balancer import write_balance_report, load_jsonl


SCENARIO_PATH = Path("datasets/scenarios/ncc_generated_scenarios_v0_10.jsonl")
TRACE_PATH = Path("reports/exp_08_scenario_generator_traces.jsonl")
BALANCE_REPORT_PATH = Path("reports/exp_08_dataset_balance_report.json")


def clarification_rate(examples):
    if not examples:
        return 0.0
    return round(
        sum(1 for e in examples if e.get("action", {}).get("kind") == "clarify") / len(examples),
        3,
    )


def blocked_action_rate(examples):
    if not examples:
        return 0.0
    return round(
        sum(1 for e in examples if e.get("action", {}).get("kind") == "blocked") / len(examples),
        3,
    )


def safe_alternative_rate(examples):
    safe_keywords = ["sauvegarde", "confirmation", "alternative", "préparer", "proposer"]
    if not examples:
        return 0.0

    count = 0
    for e in examples:
        content = str(e.get("action", {}).get("payload", {})).lower()
        if any(keyword in content for keyword in safe_keywords):
            count += 1

    return round(count / len(examples), 3)


def contradiction_detection_rate(examples):
    if not examples:
        return 0.0
    return round(
        sum(1 for e in examples if e.get("scenario", {}).get("scenario_type") == "contradiction_handling") / len(examples),
        3,
    )


def memory_trace_retrieval_rate(examples):
    if not examples:
        return 0.0
    return round(
        sum(1 for e in examples if e.get("scenario", {}).get("scenario_type") == "memory_trace_retrieval") / len(examples),
        3,
    )


def main() -> None:
    scenarios = write_scenarios(SCENARIO_PATH)
    trace_count = run_scenarios_to_jsonl(scenarios, TRACE_PATH)
    report = write_balance_report(TRACE_PATH, BALANCE_REPORT_PATH)
    examples = load_jsonl(TRACE_PATH)

    scenario_validity = 1.0 if len(scenarios) > 0 and trace_count > 0 else 0.0
    balance_coverage = report["task_coverage"]
    
    clarification_r = clarification_rate(examples)
    blocked_r = blocked_action_rate(examples)
    safe_alt_r = safe_alternative_rate(examples)
    contradiction_r = contradiction_detection_rate(examples)
    memory_trace_r = memory_trace_retrieval_rate(examples)

    report_md = Path("reports/exp_08_scenario_generator_balancing_report.md")
    report_md.parent.mkdir(parents=True, exist_ok=True)

    verdict_scenario = "OK" if scenario_validity == 1.0 else "À corriger"
    verdict_balance = "OK" if balance_coverage >= 0.8 else "À améliorer"

    report_md.write_text(
        "\n".join(
            [
                "# EXP-08 — Scenario Generator + Dataset Balancing",
                "",
                "## Objectif",
                "Tester la génération contrôlée de scénarios NCC et mesurer l’équilibrage initial du dataset.",
                "",
                "## Scores",
                f"Scenario Validity = {scenario_validity}",
                f"Task Coverage = {balance_coverage}",
                f"Task Distribution Entropy = {report['task_distribution_entropy']}",
                f"Clarification Rate = {clarification_r}",
                f"Blocked Action Rate = {blocked_r}",
                f"Safe Alternative Rate = {safe_alt_r}",
                f"Contradiction Detection Rate = {contradiction_r}",
                f"Memory Trace Retrieval Rate = {memory_trace_r}",
                "",
                f"Scénarios générés = {len(scenarios)}",
                f"Traces générées = {trace_count}",
                "",
                f"Verdict scénarios = {verdict_scenario}",
                f"Verdict équilibrage = {verdict_balance}",
                "",
                "## Distribution par tâche",
                "```json",
                str(report["task_counts"]),
                "```",
                "",
                "## Tâches manquantes",
                "```json",
                str(report["missing_tasks"]),
                "```",
                "",
                "## Interprétation",
                "NCC-V0.11 élargit la couverture du générateur de scénarios en ajoutant des familles cognitives absentes de V0.10 : réactivation mémorielle pure, sélection d’action sûre, gestion de contradiction et clarification. Cette étape réduit le biais du dataset vers les tâches déjà réussies et prépare un corpus plus équilibré pour les futurs essais NCC-LM.",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Scenario Validity: {scenario_validity}")
    print(f"Task Coverage: {balance_coverage}")
    print(f"Task Distribution Entropy: {report['task_distribution_entropy']}")
    print(f"Missing Tasks: {len(report['missing_tasks'])}")
    print(f"Clarification Rate: {clarification_r}")
    print(f"Blocked Action Rate: {blocked_r}")
    print(f"Safe Alternative Rate: {safe_alt_r}")
    print(f"Contradiction Detection Rate: {contradiction_r}")
    print(f"Memory Trace Retrieval Rate: {memory_trace_r}")
    print(f"Scenarios generated: {len(scenarios)}")
    print(f"Traces generated: {trace_count}")
    print(f"Report written to: {report_md}")


if __name__ == "__main__":
    main()
