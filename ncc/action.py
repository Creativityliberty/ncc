from __future__ import annotations

from .policy import check_action
from .schemas import Action, CognitiveState, StableOutput


def select_action(stable: StableOutput, state: CognitiveState) -> Action:
    kind = "respond"
    if stable.selected.kind == "test":
        kind = "run_test"
    elif stable.selected.kind == "clarify":
        kind = "ask_clarification"
    elif stable.selected.kind == "refuse":
        kind = "refuse"

    action = Action(kind=kind, payload={"content": stable.selected.content})
    return check_action(state, action)


def destructive_block_message(state: CognitiveState) -> str:
    learned_rules = getattr(state, "learned_policy_rules", [])

    if "destructive_actions_require_backup_and_confirmation" in learned_rules:
        return (
            "Action bloquée par gouvernance. Raison : action destructive détectée. "
            "Conformément au feedback utilisateur, il faut proposer une sauvegarde préalable "
            "puis demander une confirmation explicite avant toute suppression."
        )

    return (
        "Action bloquée par gouvernance. Raison : action destructive détectée sans confirmation explicite. "
        "Alternative : demander confirmation ou proposer une sauvegarde avant suppression."
    )
