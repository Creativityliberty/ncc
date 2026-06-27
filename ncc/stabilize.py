from __future__ import annotations

from .schemas import GapVector, StableOutput, TransformationCandidate


def select_stable_output(
    candidates: list[TransformationCandidate], gap: GapVector | None = None
) -> StableOutput:
    if not candidates:
        raise ValueError("No transformation candidates available.")

    if gap is not None and gap.governance_gap >= 0.9:
        safety_candidates = [
            candidate for candidate in candidates if candidate.kind == "safety_check"
        ]

        if safety_candidates:
            selected = max(
                safety_candidates,
                key=lambda c: c.value + c.coherence + c.actionability - c.risk - c.cost,
            )

            return StableOutput(
                selected=selected,
                score=round(
                    selected.value
                    + selected.coherence
                    + selected.actionability
                    - selected.risk
                    - selected.cost,
                    3,
                ),
                rationale=(
                    "Sélection prioritaire par gouvernance : "
                    "risque élevé détecté, transformation safety_check retenue."
                ),
            )

    selected = max(candidates, key=lambda c: c.score)
    return StableOutput(
        selected=selected,
        score=selected.score,
        rationale=f"Sélection par score fini: {selected.name} avec score={selected.score:.3f}.",
    )
