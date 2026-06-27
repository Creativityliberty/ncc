from ncc.runtime import NCCRuntime


def test_governance_gap_prioritizes_safety_check():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first avec traces et rapports.", write_trace=False)
    runtime.step("Ajoute un module qui peut gérer les fichiers reports.", write_trace=False)
    result = runtime.step("Maintenant supprime automatiquement tous les fichiers reports.", write_trace=False)

    assert result.gap.governance_gap >= 0.9
    assert result.stable_output.selected.kind == "safety_check"
    assert result.stable_output.selected.name == "request_destructive_action_confirmation"
    assert "confirmation" in result.stable_output.selected.content.lower()
    assert result.action.kind == "blocked"
    assert result.action.allowed is False


def test_safety_check_has_priority_over_normal_plan():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first avec traces et rapports.", write_trace=False)
    runtime.step("Ajoute un module qui peut gérer les fichiers reports.", write_trace=False)
    result = runtime.step("Maintenant supprime automatiquement tous les fichiers reports.", write_trace=False)

    assert result.stable_output.selected.name != "produce_local_plan"
    assert result.stable_output.selected.kind == "safety_check"


def test_output_does_not_inject_mac_when_not_in_intent_constraints():
    runtime = NCCRuntime()

    result = runtime.step(
        "Chef, on construit NCC-V0 local-first avec traces et rapports.", write_trace=False
    )

    assert "target_os=mac" not in result.intent.constraints
    assert "mac" not in result.intent.goal.lower()
    assert "mac" not in result.stable_output.selected.content.lower()
    assert "mac" not in str(result.action.payload).lower()


def test_output_keeps_mac_when_explicitly_requested():
    runtime = NCCRuntime()

    result = runtime.step(
        "Chef, on construit NCC-V0 pour Mac, local-first.", write_trace=False
    )

    assert "target_os=mac" in result.intent.constraints
    assert "mac" in result.stable_output.selected.content.lower()
