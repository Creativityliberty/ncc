from __future__ import annotations

from .schemas import CognitiveState, Observation


def build_observation(raw: str, state: CognitiveState) -> Observation:
    spatial = [raw.strip()]
    temporal = state.context[-5:]

    memorial = []
    for trace in state.memory[-10:]:
        if any(word.lower() in trace.content.lower() for word in raw.split()[:8]):
            memorial.append(trace.content)

    return Observation(raw=raw, spatial=spatial, temporal=temporal, memorial=memorial)
