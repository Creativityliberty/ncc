from ncc.runtime import NCCRuntime


def test_feedback_record_is_created():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first.")
    runtime.step(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation."
    )

    assert len(runtime.state.feedback_records) >= 1


def test_feedback_updates_learned_policy_rules():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first.")
    runtime.step(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation."
    )

    assert (
        "destructive_actions_require_backup_and_confirmation"
        in runtime.state.learned_policy_rules
    )


def test_feedback_affects_future_destructive_action():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first avec traces et rapports.")
    runtime.step(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation."
    )

    result = runtime.step("Maintenant vide automatiquement le dossier artifacts.")

    combined_text = (
        result.stable_output.selected.content.lower()
        + " "
        + str(result.action.payload).lower()
    )

    assert result.gap.governance_gap >= 0.9
    assert result.stable_output.selected.kind == "safety_check"
    assert result.action.kind == "blocked"
    assert result.action.allowed is False
    assert "sauvegarde" in combined_text
    assert "confirmation" in combined_text


def test_feedback_does_not_block_safe_action():
    runtime = NCCRuntime()

    runtime.step(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation."
    )

    result = runtime.step("Prépare un rapport de résultats.")

    assert result.action.allowed is True
    assert result.action.kind != "blocked"
