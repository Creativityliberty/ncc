from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Observation(BaseModel):
    raw: str
    spatial: list[str] = Field(default_factory=list)
    temporal: list[str] = Field(default_factory=list)
    memorial: list[str] = Field(default_factory=list)
    weight_spatial: float = 0.5
    weight_temporal: float = 0.25
    weight_memorial: float = 0.25
    timestamp: str = Field(default_factory=now_iso)


class Intent(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    horizon: Literal["short", "medium", "long"] = "short"
    expected_action: Literal["answer", "plan", "code", "artifact", "clarify", "refuse", "test"] = "answer"
    salience: float = 0.5
    uncertainty: float = 0.5


class GapVector(BaseModel):
    semantic_gap: float = 0.0
    procedure_gap: float = 0.0
    knowledge_gap: float = 0.0
    action_gap: float = 0.0
    governance_gap: float = 0.0

    @property
    def norm(self) -> float:
        vals = [self.semantic_gap, self.procedure_gap, self.knowledge_gap, self.action_gap, self.governance_gap]
        return sum(v * v for v in vals) ** 0.5


class TransformationCandidate(BaseModel):
    name: str
    kind: Literal["answer", "clarify", "plan", "code", "test", "refuse", "memory", "policy"]
    content: str
    value: float = 0.0
    coherence: float = 0.0
    actionability: float = 0.0
    risk: float = 0.0
    cost: float = 0.0

    @property
    def score(self) -> float:
        return self.value + self.coherence + self.actionability - self.risk - self.cost


class StableOutput(BaseModel):
    selected: TransformationCandidate
    score: float
    rationale: str


class MemoryTrace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    kind: Literal["event", "preference", "constraint", "result", "feedback", "knowledge_hint"] = "event"
    importance: float = 0.5
    created_at_step: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeClaim(BaseModel):
    claim: str
    status: Literal["active", "superseded", "uncertain"] = "active"
    evidence: list[str] = Field(default_factory=list)
    revision_policy: str = "evidence_gated"


class PolicyRule(BaseModel):
    name: str
    action_kind: str
    allowed: bool = True
    requires_confirmation: bool = False
    reason: str = ""


class ReasoningState(BaseModel):
    summary: str
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Action(BaseModel):
    kind: Literal["respond", "ask_clarification", "write_file", "run_test", "refuse", "no_op"] = "respond"
    payload: dict[str, Any] = Field(default_factory=dict)
    allowed: bool = True
    reason: str = ""


class Feedback(BaseModel):
    type: Literal["approval", "correction", "rejection", "preference", "new_constraint", "none"] = "none"
    content: str = ""
    impact: dict[str, float] = Field(default_factory=dict)


class CognitiveState(BaseModel):
    step: int = 0
    context: list[str] = Field(default_factory=list)
    memory: list[MemoryTrace] = Field(default_factory=list)
    knowledge: list[KnowledgeClaim] = Field(default_factory=list)
    policies: list[PolicyRule] = Field(default_factory=list)
    active_intent: Intent | None = None
    last_intent: Intent | None = None
    last_gap: GapVector | None = None


class NCCTrace(BaseModel):
    step: int
    observation: Observation
    intent: Intent
    gap: GapVector
    candidates: list[TransformationCandidate]
    stable_output: StableOutput
    reasoning: ReasoningState
    action: Action
    feedback: Feedback
    state_after_summary: dict[str, Any]
    timestamp: str = Field(default_factory=now_iso)
