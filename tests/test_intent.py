from ncc.intent import extract_intent
from ncc.schemas import CognitiveState, Observation


def test_mac_intent_constraints():
    obs = Observation(raw="Fais une version locale pour Mac avec fichiers md et tests")
    intent = extract_intent(obs, CognitiveState())
    assert "target_os=mac" in intent.constraints
    assert "produce_markdown_assets" in intent.constraints


def test_intent_merge_preserves_initial_constraints():
    from ncc.intent import merge_intent
    from ncc.schemas import Intent
    
    intent1 = Intent(goal="Goal", constraints=["target_os=mac", "local_first"])
    intent2 = Intent(goal="Goal", constraints=["include_tests_and_result_interpretation"])
    
    merged = merge_intent(intent1, intent2)
    assert "target_os=mac" in merged.constraints
    assert "local_first" in merged.constraints
    assert "include_tests_and_result_interpretation" in merged.constraints


def test_intent_can_change_when_user_explicitly_changes_goal():
    from ncc.intent import merge_intent
    from ncc.schemas import Intent
    
    intent1 = Intent(goal="Goal Mac", constraints=["target_os=mac"])
    intent2 = Intent(goal="Goal Windows", constraints=["target_os=windows"])
    
    # Simulate a flag or a smart merge where if the goal is explicitly changed, we take it.
    merged = merge_intent(intent1, intent2)
    assert merged.goal == "Goal Windows"
    assert "target_os=windows" in merged.constraints
    assert "target_os=mac" not in merged.constraints
