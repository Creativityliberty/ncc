from __future__ import annotations

from .schemas import CognitiveState, GapVector, Intent


def compute_gap(intent: Intent, state: CognitiveState) -> GapVector:
    has_memory = len(state.memory) > 0
    has_policies = len(state.policies) > 0

    return GapVector(
        semantic_gap=0.25 if intent.goal else 0.7,
        procedure_gap=0.75 if intent.expected_action in {"plan", "code", "test"} else 0.35,
        knowledge_gap=0.45 if not state.knowledge else 0.25,
        action_gap=0.60 if intent.expected_action in {"plan", "code", "test"} else 0.25,
        governance_gap=0.10 if has_policies else 0.30,
    )
