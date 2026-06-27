from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ncc.runtime import NCCRuntime
from ncc.scenario_generator import Scenario


def _to_dict(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, list):
        return [_to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


def run_scenario(scenario: Scenario) -> list[dict[str, Any]]:
    runtime = NCCRuntime()
    traces: list[dict[str, Any]] = []

    for index, turn in enumerate(scenario.turns, start=1):
        result = runtime.step(turn)

        trace = _to_dict(result)
        trace["scenario"] = {
            "scenario_id": scenario.scenario_id,
            "scenario_type": scenario.scenario_type,
            "difficulty": scenario.difficulty,
            "step": index,
            "total_steps": len(scenario.turns),
            "expected_action_kind": scenario.expected_action_kind,
            "expected_governance_status": scenario.expected_governance_status,
            "expected_constraints": scenario.expected_constraints,
            "expected_policy_rules": scenario.expected_policy_rules,
            "expected_knowledge_records": scenario.expected_knowledge_records,
            "expected_reactivation_source": scenario.expected_reactivation_source,
            "quality_tags": scenario.quality_tags,
        }

        traces.append(trace)

    return traces


def run_scenarios_to_jsonl(scenarios: list[Scenario], output_path: str | Path) -> int:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0

    with output_path.open("w", encoding="utf-8") as f:
        for scenario in scenarios:
            traces = run_scenario(scenario)
            for trace in traces:
                f.write(json.dumps(trace, ensure_ascii=False) + "\n")
                count += 1

    return count
