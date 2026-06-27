from __future__ import annotations

from .schemas import CognitiveState, KnowledgeClaim


def seed_knowledge(state: CognitiveState) -> CognitiveState:
    if state.knowledge:
        return state
    state.knowledge.append(KnowledgeClaim(
        claim="NCC distingue mémoire, connaissance, politique/sagesse et inférence temporaire.",
        evidence=["Missing Knowledge Layer"],
    ))
    state.knowledge.append(KnowledgeClaim(
        claim="La mémoire NCC-V0 est une approximation tronquée, pas encore une preuve de mémoire fractal-fractionnaire complète.",
        evidence=["NCC methodological guardrail"],
    ))
    return state


from ncc.schemas import EvidenceRecord, KnowledgeRecord


VERIFIED_FACT_MARKERS = [
    "fait vérifié :",
    "fait verifie :",
    "connaissance vérifiée :",
    "connaissance verifiee :",
    "source vérifiée :",
    "source verifiee :",
]


def is_verified_knowledge_input(user_input: str) -> bool:
    text = user_input.lower().strip()
    return any(marker in text for marker in VERIFIED_FACT_MARKERS)


def extract_knowledge(
    user_input: str,
    source_step: int | None = None,
) -> KnowledgeRecord | None:
    """
    Extrait une connaissance uniquement si l'utilisateur marque explicitement
    l'entrée comme fait/connaissance/source vérifiée.

    Règle V0.7 :
    - une demande projet n'est pas une connaissance ;
    - un feedback politique n'est pas une connaissance ;
    - une question de raisonnement n'est pas une connaissance ;
    - une connaissance doit être explicitement signalée ou sourcée.
    """
    if not is_verified_knowledge_input(user_input):
        return None

    claim = user_input

    for marker in VERIFIED_FACT_MARKERS:
        if marker in user_input.lower():
            claim = user_input.split(":", 1)[-1].strip()
            break

    evidence = EvidenceRecord(
        source="user_verified_input",
        content=user_input,
        source_step=source_step,
        confidence=0.85,
    )

    return KnowledgeRecord(
        claim=claim,
        evidence=[evidence],
        status="active",
        confidence=0.85,
        tags=["verified_user_claim"],
        source_step=source_step,
    )


def consolidate_knowledge(state, knowledge_record: KnowledgeRecord):
    existing_claims = {item.claim for item in state.knowledge_records}

    if knowledge_record.claim not in existing_claims:
        state.knowledge_records.append(knowledge_record)

    return state
