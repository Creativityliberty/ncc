from __future__ import annotations

from .action import select_action
from .feedback import no_feedback
from .gap import compute_gap
from .intent import extract_intent
from .knowledge import seed_knowledge
from .memory import MemoryEngine
from .observation import build_observation
from .policy import seed_policies
from .reasoner import reason
from .schemas import CognitiveState, NCCTrace
from .stabilize import select_stable_output
from .trace import append_trace
from .transform import generate_transformations


class NCCRuntime:
    def __init__(self, trace_path: str = "reports/traces.jsonl") -> None:
        self.state = CognitiveState()
        self.state = seed_knowledge(seed_policies(self.state))
        self.memory_engine = MemoryEngine(window=100)
        self.trace_path = trace_path

    def step(self, raw: str, write_trace: bool = True) -> NCCTrace:
        self.state.step += 1
        obs = build_observation(raw, self.state)
        current_intent = extract_intent(obs, self.state)
        
        # V0.1 — Cumulative Intent Preservation Patch
        if self.state.active_intent is not None:
            # Note: need to import merge_intent at the top
            from .intent import merge_intent
            intent = merge_intent(self.state.active_intent, current_intent)
        else:
            intent = current_intent
            
        self.state.active_intent = intent
        gap = compute_gap(intent, self.state)
        candidates = generate_transformations(intent, gap)
        stable = select_stable_output(candidates)
        self.state = self.memory_engine.update(self.state, stable)
        reasoning = reason(intent, gap, stable, self.state)
        action = select_action(stable, self.state)
        feedback = no_feedback()

        self.state.context.append(raw)
        self.state.last_intent = intent
        self.state.last_gap = gap

        trace = NCCTrace(
            step=self.state.step,
            observation=obs,
            intent=intent,
            gap=gap,
            candidates=candidates,
            stable_output=stable,
            reasoning=reasoning,
            action=action,
            feedback=feedback,
            state_after_summary={
                "context_size": len(self.state.context),
                "memory_size": len(self.state.memory),
                "knowledge_size": len(self.state.knowledge),
                "policy_size": len(self.state.policies),
                "memory_strength": self.memory_engine.weighted_memory_strength(self.state),
            },
        )
        if write_trace:
            append_trace(self.trace_path, trace)
        return trace
