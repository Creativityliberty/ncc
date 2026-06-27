from __future__ import annotations

import numpy as np

from .schemas import CognitiveState, MemoryTrace, StableOutput


def exponential_kernel(age: int, alpha: float = 0.2) -> float:
    return float(np.exp(-alpha * max(age, 0)))


def power_kernel(age: int, alpha: float = 0.8) -> float:
    return float(1.0 / ((1 + max(age, 0)) ** alpha))


def hybrid_kernel(age: int, alpha: float = 0.2, beta: float = 0.8, mu: float = 0.5) -> float:
    return float(mu * exponential_kernel(age, alpha) + (1 - mu) * power_kernel(age, beta))


class MemoryEngine:
    def __init__(self, window: int = 100) -> None:
        self.window = window

    def update(self, state: CognitiveState, stable: StableOutput) -> CognitiveState:
        trace = MemoryTrace(
            content=stable.selected.content,
            kind="result",
            importance=min(1.0, max(0.1, stable.score / 3.0)),
            created_at_step=state.step,
            metadata={"candidate": stable.selected.name, "score": stable.score},
        )
        state.memory.append(trace)
        if len(state.memory) > self.window:
            state.memory = state.memory[-self.window:]
        return state

    def weighted_memory_strength(self, state: CognitiveState) -> float:
        total = 0.0
        for tr in state.memory:
            age = max(0, state.step - tr.created_at_step)
            total += hybrid_kernel(age) * tr.importance
        return float(total)
