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
