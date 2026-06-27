from __future__ import annotations

from .schemas import GapVector, Intent, TransformationCandidate
from ncc.clarification import clarification_needed


def is_safe_action_request(user_input: str) -> bool:
    text = user_input.lower()
    return (
        "sans les supprimer directement" in text
        or "sans supprimer directement" in text
        or "prépare une action pour supprimer" in text
        or "prepare an action to delete" in text
    )


def build_safe_action_candidate():
    return TransformationCandidate(
        name="prepare_safe_deletion_plan",
        kind="safe_action_plan",
        content=(
            "Préparer une action sûre : lister les rapports anciens, proposer une sauvegarde préalable, "
            "demander confirmation explicite, puis seulement exécuter la suppression si elle est confirmée."
        ),
        value=0.96,
        coherence=0.95,
        actionability=0.9,
        risk=0.02,
        cost=0.2,
    )


def build_clarification_candidate(reason: str):
    return TransformationCandidate(
        name="request_clarification",
        kind="clarification",
        content=reason,
        value=0.97,
        coherence=0.96,
        actionability=0.9,
        risk=0.01,
        cost=0.1,
    )


def build_safety_candidate(state=None) -> TransformationCandidate:
    learned_rules = getattr(state, "learned_policy_rules", []) if state else []

    if "destructive_actions_require_backup_and_confirmation" in learned_rules:
        content = (
            "Action destructive détectée. Conformément au feedback utilisateur, "
            "proposer d’abord une sauvegarde préalable, puis demander une confirmation explicite "
            "avant toute exécution."
        )
    else:
        content = (
            "Action destructive détectée. Demander une confirmation explicite "
            "avant exécution et proposer une sauvegarde préalable."
        )

    return TransformationCandidate(
        name="request_destructive_action_confirmation",
        kind="safety_check",
        content=content,
        value=0.98,
        coherence=0.98,
        actionability=0.85,
        risk=0.01,
        cost=0.2,
    )


def platform_label_from_constraints(constraints: list[str]) -> str:
    if "target_os=mac" in constraints:
        return " Mac"
    if "target_os=windows" in constraints:
        return " Windows"
    return ""


def build_local_plan_content(constraints: list[str]) -> str:
    platform_label = platform_label_from_constraints(constraints)

    return (
        f"Produire un plan local{platform_label} avec installation, "
        "structure du dépôt, tests, expériences et lecture des résultats."
    )


def generate_transformations(intent: Intent, gap: GapVector, max_candidates: int = 8, state=None, user_input: str = "") -> list[TransformationCandidate]:
    candidates: list[TransformationCandidate] = []

    needs_clarification, clarification_reason = clarification_needed(
        user_input=user_input,
        constraints=intent.constraints,
    )

    if needs_clarification:
        candidates.insert(
            0,
            build_clarification_candidate(clarification_reason),
        )

    if is_safe_action_request(user_input):
        candidates.insert(0, build_safe_action_candidate())

    if intent.uncertainty > 0.6:
        candidates.append(TransformationCandidate(
            name="clarify_intent",
            kind="clarify",
            content="Demander une clarification car l’intention est trop incertaine.",
            value=0.5, coherence=0.8, actionability=0.7, risk=0.1, cost=0.2,
        ))

    if gap.governance_gap >= 0.9:
        candidates.insert(0, build_safety_candidate(state=state))

    candidates.append(TransformationCandidate(
        name="produce_local_plan",
        kind="plan",
        content=build_local_plan_content(intent.constraints),
        value=0.95, coherence=0.9, actionability=0.95, risk=0.05, cost=0.25,
    ))

    candidates.append(TransformationCandidate(
        name="produce_runtime_skeleton",
        kind="code",
        content="Générer le squelette Python NCC-V0 : schemas, runtime, memory, policy, metrics, tests.",
        value=0.9, coherence=0.85, actionability=0.85, risk=0.15, cost=0.35,
    ))

    candidates.append(TransformationCandidate(
        name="produce_experiment_protocol",
        kind="test",
        content="Créer les premiers scénarios expérimentaux : préservation d’intention, mémoire, gouvernance, feedback.",
        value=0.85, coherence=0.85, actionability=0.9, risk=0.1, cost=0.3,
    ))

    candidates.append(TransformationCandidate(
        name="produce_scientific_warning",
        kind="answer",
        content="Rappeler que NCC-V0 est un banc d’essai borné et non une preuve d’AGI ou de convergence globale.",
        value=0.75, coherence=0.95, actionability=0.55, risk=0.02, cost=0.1,
    ))

    return candidates[:max_candidates]
