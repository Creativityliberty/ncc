from ncc.runtime import NCCRuntime


def test_runtime_step():
    rt = NCCRuntime(trace_path="reports/test_traces.jsonl")
    trace = rt.step("Plan local pour Mac avec tests", write_trace=False)
    assert trace.intent.expected_action in {"plan", "test", "answer", "code"}
    assert trace.stable_output.score > 0
    assert trace.action.allowed is True
