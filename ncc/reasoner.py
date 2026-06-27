from __future__ import annotations

from .schemas import CognitiveState, GapVector, Intent, ReasoningState, StableOutput


def reason(intent: Intent, gap: GapVector, stable: StableOutput, state: CognitiveState) -> ReasoningState:
    warnings = []
    if gap.norm > 1.2:
        warnings.append("Écart élevé : il faut garder des étapes bornées et traçables.")
    if "target_os=mac" in intent.constraints:
        warnings.append("Cible Mac détectée : privilégier Terminal, Homebrew, venv, pytest.")
    if gap.governance_gap >= 0.9:
        warnings.append("Risque de gouvernance élevé : action destructive détectée, confirmation explicite requise.")

    return ReasoningState(
        summary=f"Intention: {intent.goal} | Transformation retenue: {stable.selected.name}",
        assumptions=["Runtime déterministe avant LLM", "Chaque cycle doit produire une trace JSONL"],
        warnings=warnings,
    )
