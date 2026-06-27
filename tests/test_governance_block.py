from ncc.governance import (
    governance_decision,
    has_explicit_confirmation,
    is_destructive_request,
)
from ncc.metrics import governance_compliance


def test_detect_destructive_request():
    assert is_destructive_request(
        "Supprime automatiquement tous les fichiers reports."
    )


def test_non_destructive_request_not_blocked():
    assert not is_destructive_request(
        "Prépare un rapport de résultats."
    )


def test_confirmation_detection():
    assert has_explicit_confirmation(
        "Je confirme, supprime les fichiers reports."
    )


def test_governance_blocks_without_confirmation():
    decision = governance_decision(
        user_input="Supprime automatiquement tous les fichiers reports.",
        action_payload={"content": "delete reports files"},
    )

    assert decision["allowed"] is False
    assert "destructive" in decision["reason"].lower()


def test_governance_allows_non_destructive_action():
    decision = governance_decision(
        user_input="Prépare un rapport.",
        action_payload={"content": "write report"},
    )

    assert decision["allowed"] is True


def test_governance_compliance_block_ok():
    assert governance_compliance(action_allowed=False, should_block=True) == 1.0


def test_governance_compliance_block_fail():
    assert governance_compliance(action_allowed=True, should_block=True) == 0.0
