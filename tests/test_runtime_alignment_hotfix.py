import pytest

from ncc.runtime import NCCRuntime
from ncc.scenario_generator import generate_scenarios

def test_clarification_alignment():
    scenarios = generate_scenarios()
    clarification_scenarios = [s for s in scenarios if s.scenario_type == "clarification_needed"]
    assert len(clarification_scenarios) > 0

    runtime = NCCRuntime(trace_path="/tmp/null.jsonl")
    for event in clarification_scenarios[0].turns:
        trace = runtime.step(event, write_trace=False)
        
    assert trace.action.kind in ["ask_clarification", "clarify"]
    assert "Clarification" in trace.action.reason or "clarification" in trace.action.reason.lower()

def test_contradiction_alignment():
    scenarios = generate_scenarios()
    contradiction_scenarios = [s for s in scenarios if s.scenario_type == "contradiction_handling"]
    assert len(contradiction_scenarios) > 0

    runtime = NCCRuntime(trace_path="/tmp/null.jsonl")
    for event in contradiction_scenarios[0].turns:
        trace = runtime.step(event, write_trace=False)
        
    has_contradiction = any(
        r.get("status") == "contradicted" 
        for r in trace.knowledge_records
    )
    assert has_contradiction

def test_safe_action_alignment():
    scenarios = generate_scenarios()
    safe_scenarios = [s for s in scenarios if s.scenario_type == "safe_action_selection"]
    assert len(safe_scenarios) > 0

    runtime = NCCRuntime(trace_path="/tmp/null.jsonl")
    for event in safe_scenarios[0].turns:
        trace = runtime.step(event, write_trace=False)
        
    assert trace.stable_output.selected.kind == "safe_action_plan"

def test_wsl2_retention():
    scenarios = generate_scenarios()
    wsl_scenarios = [s for s in scenarios if s.scenario_type == "intent_preservation" and "wsl" in s.scenario_id.lower()]
    assert len(wsl_scenarios) > 0

    runtime = NCCRuntime(trace_path="/tmp/null.jsonl")
    for event in wsl_scenarios[0].turns:
        trace = runtime.step(event, write_trace=False)
        
    assert "wsl2" in trace.intent.constraints
