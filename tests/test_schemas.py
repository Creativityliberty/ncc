from ncc.schemas import Intent, GapVector


def test_intent_schema():
    intent = Intent(goal="test", expected_action="plan")
    assert intent.goal == "test"
    assert intent.expected_action == "plan"


def test_gap_norm():
    gap = GapVector(semantic_gap=1.0, procedure_gap=0.0)
    assert gap.norm == 1.0
