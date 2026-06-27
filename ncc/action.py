from __future__ import annotations

from .policy import check_action
from .schemas import Action, CognitiveState, StableOutput


def select_action(stable: StableOutput, state: CognitiveState) -> Action:
    selected = stable.selected
    kind_value = selected.kind if hasattr(selected, "kind") else selected.get("kind")
    content_value = selected.content if hasattr(selected, "content") else selected.get("content")

    if kind_value == "clarification":
        return Action(
            kind="clarify",
            payload={
                "content": content_value,
            },
            allowed=True,
            reason="Clarification requise avant exécution.",
        )

    kind = "respond"
    if kind_value == "test":
        kind = "run_test"
    elif kind_value == "refuse":
        kind = "refuse"

    action = Action(kind=kind, payload={"content": content_value})
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
