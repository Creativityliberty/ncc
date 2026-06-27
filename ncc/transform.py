from __future__ import annotations

from .schemas import GapVector, Intent, TransformationCandidate


def generate_transformations(intent: Intent, gap: GapVector, max_candidates: int = 8) -> list[TransformationCandidate]:
    candidates: list[TransformationCandidate] = []

    if intent.uncertainty > 0.6:
        candidates.append(TransformationCandidate(
            name="clarify_intent",
            kind="clarify",
            content="Demander une clarification car l’intention est trop incertaine.",
            value=0.5, coherence=0.8, actionability=0.7, risk=0.1, cost=0.2,
        ))

    if gap.governance_gap >= 0.9:
        candidates.append(
            TransformationCandidate(
                name="request_destructive_action_confirmation",
                kind="safety_check",
                content=(
                    "Demander une confirmation explicite avant toute action destructive "
                    "et proposer une sauvegarde préalable."
                ),
                value=0.95,
                coherence=0.95,
                actionability=0.8,
                risk=0.05,
                cost=0.2,
            )
        )

    candidates.append(TransformationCandidate(
        name="produce_local_plan",
        kind="plan",
        content="Produire un plan local Mac avec installation, structure du dépôt, tests, expériences et lecture des résultats.",
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
