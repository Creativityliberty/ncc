from __future__ import annotations

from .schemas import GapVector, Intent


def constraint_retention(initial_constraints: list[str], current_constraints: list[str]) -> float:
    if not initial_constraints:
        return 1.0

    initial = set(initial_constraints)
    current = set(current_constraints)

    return len(initial.intersection(current)) / len(initial)


def intent_preservation(initial: Intent, current: Intent) -> float:
    goal_score = 1.0 if initial.goal == current.goal else 0.5

    constraint_score = constraint_retention(
        initial.constraints,
        current.constraints,
    )

    return round((0.7 * goal_score) + (0.3 * constraint_score), 3)


def gap_reduction(initial: GapVector, current: GapVector) -> float:
    if initial.norm == 0:
        return 0.0
    return round(1 - (current.norm / initial.norm), 3)
