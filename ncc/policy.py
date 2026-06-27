from __future__ import annotations

from .schemas import Action, CognitiveState, PolicyRule, StableOutput


def seed_policies(state: CognitiveState) -> CognitiveState:
    if state.policies:
        return state
    state.policies.append(PolicyRule(name="allow_response", action_kind="respond", allowed=True))
    state.policies.append(PolicyRule(name="allow_tests", action_kind="run_test", allowed=True))
    state.policies.append(PolicyRule(name="guard_agi_claim", action_kind="claim_agi", allowed=False, reason="NCC-V0 ne prouve pas l’AGI."))
    return state


def check_action(state: CognitiveState, action: Action) -> Action:
    for rule in state.policies:
        if rule.action_kind == action.kind and not rule.allowed:
            action.allowed = False
            action.reason = rule.reason or f"Action bloquée par politique: {rule.name}"
            return action
    action.allowed = True
    return action
