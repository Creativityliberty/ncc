from ncc.knowledge import extract_knowledge
from ncc.metrics import knowledge_memory_separation_score, layer_purity_score
from ncc.runtime import NCCRuntime


def test_verified_fact_creates_knowledge_record():
    record = extract_knowledge(
        "Fait vérifié : CoALA organise les agents de langage autour de la mémoire, de l’espace d’action et de la décision.",
        source_step=1,
    )

    assert record is not None
    assert "CoALA" in record.claim
    assert record.status == "active"
    assert record.evidence[0].source == "user_verified_input"


def test_project_request_does_not_create_knowledge_record():
    record = extract_knowledge(
        "Chef, on construit NCC-V0 local-first avec traces et rapports.",
        source_step=1,
    )

    assert record is None


def test_policy_feedback_does_not_create_knowledge_record():
    record = extract_knowledge(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation.",
        source_step=1,
    )

    assert record is None


def test_reasoning_question_does_not_create_knowledge_record():
    record = extract_knowledge(
        "Pourquoi la séparation mémoire / connaissance est importante ?",
        source_step=1,
    )

    assert record is None


def test_knowledge_memory_separation_score_ok():
    score = knowledge_memory_separation_score(
        memory_ok=True,
        knowledge_ok=True,
        policy_ok=True,
        reasoning_not_persisted=True,
    )

    assert score == 1.0


def test_layer_purity_score_ok():
    assert layer_purity_score(total_items=10, misplaced_items=0) == 1.0
    assert layer_purity_score(total_items=10, misplaced_items=1) == 0.9


def test_runtime_separates_knowledge_and_policy():
    runtime = NCCRuntime()

    runtime.step("Chef, on construit NCC-V0 local-first avec traces et rapports.")

    runtime.step(
        "Fait vérifié : CoALA organise les agents de langage autour de la mémoire, de l’espace d’action et de la décision."
    )

    runtime.step(
        "À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation."
    )

    knowledge_text = str([
        record.model_dump()
        for record in runtime.state.knowledge_records
    ])

    assert "CoALA" in knowledge_text
    assert (
        "destructive_actions_require_backup_and_confirmation"
        in runtime.state.learned_policy_rules
    )

    assert "destructive_actions_require_backup_and_confirmation" not in knowledge_text
