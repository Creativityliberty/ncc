from __future__ import annotations

from pathlib import Path

from ncc.scenario_generator import write_scenarios
from ncc.scenario_runner import run_scenarios_to_jsonl
from ncc.dataset_balancer import write_balance_report


SCENARIO_PATH = Path("datasets/scenarios/ncc_generated_scenarios_v0_10.jsonl")
TRACE_PATH = Path("reports/exp_08_scenario_generator_traces.jsonl")
BALANCE_REPORT_PATH = Path("reports/exp_08_dataset_balance_report.json")


def main() -> None:
    scenarios = write_scenarios(SCENARIO_PATH)
    trace_count = run_scenarios_to_jsonl(scenarios, TRACE_PATH)
    report = write_balance_report(TRACE_PATH, BALANCE_REPORT_PATH)

    scenario_validity = 1.0 if len(scenarios) > 0 and trace_count > 0 else 0.0
    balance_coverage = report["task_coverage"]

    report_md = Path("reports/exp_08_scenario_generator_balancing_report.md")
    report_md.parent.mkdir(parents=True, exist_ok=True)

    verdict_scenario = "OK" if scenario_validity == 1.0 else "À corriger"
    verdict_balance = "OK" if balance_coverage >= 0.5 else "À améliorer"

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
                f"Balance Coverage = {balance_coverage}",
                f"Task Distribution Entropy = {report['task_distribution_entropy']}",
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
                "V0.10 valide le passage d’un dataset expérimental fixe vers une génération contrôlée de scénarios cognitifs. "
                "Le but n’est pas encore de produire un très grand dataset, mais de préparer une croissance saine, équilibrée et vérifiable pour NCC-LM.",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Scenario Validity: {scenario_validity}")
    print(f"Balance Coverage: {balance_coverage}")
    print(f"Task Distribution Entropy: {report['task_distribution_entropy']}")
    print(f"Scenarios generated: {len(scenarios)}")
    print(f"Traces generated: {trace_count}")
    print(f"Report written to: {report_md}")


if __name__ == "__main__":
    main()
