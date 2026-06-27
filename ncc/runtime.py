from __future__ import annotations

from .action import select_action
from .feedback import no_feedback
from .gap import compute_gap
from .intent import extract_intent
from .knowledge import seed_knowledge
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
        self.trace_path = trace_path

    def step(self, raw: str, write_trace: bool = True) -> NCCTrace:
        self.state.step += 1
        temporal_limit = getattr(self, "temporal_limit", None)
        obs = build_observation(raw, self.state, temporal_limit=temporal_limit)
        current_intent = extract_intent(obs, self.state)
        
        # V0.1 — Cumulative Intent Preservation Patch
        if self.state.active_intent is not None:
            from .intent import merge_intent
            intent = merge_intent(self.state.active_intent, current_intent)
        else:
            intent = current_intent
            
        self.state.active_intent = intent
        gap = compute_gap(intent, self.state, user_input=raw)
        candidates = generate_transformations(intent, gap)
        stable = select_stable_output(candidates)
        reasoning = reason(intent, gap, stable, self.state)
        action = select_action(stable, self.state)
        
        from ncc.governance import governance_decision
        decision = governance_decision(
            user_input=raw,
            action_payload=action.payload,
        )

        if not decision["allowed"]:
            action.allowed = False
            action.kind = "blocked"
            action.reason = decision["reason"]
            action.payload = {
                "content": (
                    "Action bloquée par gouvernance. "
                    f"Raison : {decision['reason']} "
                    f"Alternative : {decision['alternative']}"
                )
            }

        feedback = no_feedback()

        from ncc.memory import build_memory_record
        step_index = len(self.state.context) + 1

        intent_record = build_memory_record(
            event_type="intent",
            content=intent.goal,
            constraints=intent.constraints,
            tags=[
                "intent",
                intent.expected_action,
                intent.horizon,
            ],
            salience=intent.salience,
            source_step=step_index,
        )
        self.state.memory.append(intent_record)

        transform_record = build_memory_record(
            event_type="stable_output",
            content=stable.selected.content,
            constraints=intent.constraints,
            tags=[
                "transformation",
                stable.selected.name,
                stable.selected.kind,
            ],
            salience=stable.selected.value,
            source_step=step_index,
        )
        self.state.memory.append(transform_record)

        action_record = build_memory_record(
            event_type="action",
            content=str(action.payload),
            constraints=intent.constraints,
            tags=[
                "action",
                action.kind,
                "allowed" if action.allowed else "blocked",
            ],
            salience=0.8 if action.allowed else 0.95,
            source_step=step_index,
        )
        self.state.memory.append(action_record)

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
                "memory_strength": 0.0,
            },
        )
        if write_trace:
            append_trace(self.trace_path, trace)
        return trace
