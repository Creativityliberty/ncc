from __future__ import annotations

from .schemas import StableOutput, TransformationCandidate


def select_stable_output(candidates: list[TransformationCandidate]) -> StableOutput:
    if not candidates:
        raise ValueError("No transformation candidates available.")
    selected = max(candidates, key=lambda c: c.score)
    return StableOutput(
        selected=selected,
        score=selected.score,
        rationale=f"Sélection par score fini: {selected.name} avec score={selected.score:.3f}.",
    )
