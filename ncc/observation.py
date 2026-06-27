from __future__ import annotations

from ncc.memory import MemoryStore
from ncc.schemas import CognitiveState, Observation


def build_observation(
    raw: str, state: CognitiveState, temporal_limit: int | None = None
) -> Observation:
    spatial = [raw.strip()]
    temporal_context = state.context

    if temporal_limit is not None:
        if temporal_limit == 0:
            temporal_context = []
        else:
            temporal_context = temporal_context[-temporal_limit:]

    memory_store = MemoryStore(getattr(state, "memory", []))
    retrieved_memory = memory_store.search(raw, limit=3)

    memorial = [
        {
            "event_type": record.event_type,
            "content": record.content,
            "constraints": record.constraints,
            "tags": record.tags,
            "salience": record.salience,
            "source_step": record.source_step,
        }
        for record in retrieved_memory
    ]

    return Observation(
        raw=raw, spatial=spatial, temporal=temporal_context, memorial=memorial
    )
