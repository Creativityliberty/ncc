from ncc.policy import check_action, seed_policies
from ncc.schemas import Action, CognitiveState


def test_policy_seed_allows_response():
    state = seed_policies(CognitiveState())
    action = check_action(state, Action(kind="respond"))
    assert action.allowed is True
