from ncc.runtime import NCCRuntime


def test_intent_does_not_inject_mac_when_not_requested():
    runtime = NCCRuntime()

    result = runtime.step(
        "Chef, on construit NCC-V0 local-first avec traces et rapports.",
        write_trace=False
    )

    assert "target_os=mac" not in result.intent.constraints
    assert "Mac" not in result.intent.goal
    assert "mac" not in result.intent.goal.lower()


def test_intent_keeps_mac_when_explicitly_requested():
    runtime = NCCRuntime()

    result = runtime.step(
        "Chef, on construit NCC-V0 pour Mac, local-first.",
        write_trace=False
    )

    assert "target_os=mac" in result.intent.constraints
