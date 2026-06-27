from ncc.gap import compute_gap
from ncc.schemas import CognitiveState, Intent


def test_gap_is_computable():
    gap = compute_gap(Intent(goal="test", expected_action="plan"), CognitiveState())
    assert gap.norm > 0
