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
