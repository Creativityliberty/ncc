from ncc.scenario_generator import generate_scenarios


def test_generate_scenarios_not_empty():
    scenarios = generate_scenarios()

    assert len(scenarios) > 0


def test_generated_scenarios_have_required_fields():
    scenarios = generate_scenarios()

    for scenario in scenarios:
        assert scenario.scenario_id
        assert scenario.scenario_type
        assert scenario.difficulty in {"easy", "medium", "hard", "adversarial"}
        assert len(scenario.turns) >= 1
        assert isinstance(scenario.expected_constraints, list)
        assert isinstance(scenario.expected_policy_rules, list)
        assert isinstance(scenario.expected_reactivation_source, dict)


def test_governance_scenarios_expect_blocked_action():
    scenarios = generate_scenarios()
    governance = [s for s in scenarios if s.scenario_type == "governance_block"]

    assert governance

    for scenario in governance:
        assert scenario.expected_action_kind == "blocked"
        assert scenario.expected_governance_status == "blocked"


def test_feedback_scenario_contains_policy_update():
    scenarios = generate_scenarios()
    feedback = [s for s in scenarios if s.scenario_type == "feedback_consolidation"]

    assert feedback

    assert any(
        "destructive_actions_require_backup_and_confirmation"
        in scenario.expected_policy_rules
        for scenario in feedback
    )
