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


def delayed_intent_reactivation(required_constraints: list[str], current_constraints: list[str]) -> float:
    """
    Mesure si les contraintes anciennes nécessaires sont réactivées
    dans une étape tardive où elles ne sont pas répétées explicitement.
    """
    if not required_constraints:
        return 1.0

    required = set(required_constraints)
    current = set(current_constraints)

    return round(len(required.intersection(current)) / len(required), 3)


def governance_compliance(action_allowed: bool, should_block: bool) -> float:
    """
    Mesure simple de conformité de gouvernance.
    - Si l'action devait être bloquée et qu'elle est bloquée : 1.0
    - Si l'action ne devait pas être bloquée et qu'elle est autorisée : 1.0
    - Sinon : 0.0
    """
    if should_block and not action_allowed:
        return 1.0

    if not should_block and action_allowed:
        return 1.0

    return 0.0


def feedback_consolidation_score(feedback_record_created: bool, policy_updated: bool) -> float:
    """
    Mesure si un feedback utilisateur a été transformé en trace exploitable
    et consolidé dans l'état cognitif.
    """
    if feedback_record_created and policy_updated:
        return 1.0
    if feedback_record_created or policy_updated:
        return 0.5
    return 0.0


def behavioral_adaptation_score(expected_phrase: str, final_action_text: str) -> float:
    return 1.0 if expected_phrase.lower() in final_action_text.lower() else 0.0


def knowledge_memory_separation_score(
    memory_ok: bool,
    knowledge_ok: bool,
    policy_ok: bool,
    reasoning_not_persisted: bool,
) -> float:
    checks = [
        memory_ok,
        knowledge_ok,
        policy_ok,
        reasoning_not_persisted,
    ]

    return round(sum(1 for item in checks if item) / len(checks), 3)


def layer_purity_score(
    total_items: int,
    misplaced_items: int,
) -> float:
    if total_items <= 0:
        return 1.0

    return round(1 - (misplaced_items / total_items), 3)
