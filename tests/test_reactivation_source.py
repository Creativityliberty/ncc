from types import SimpleNamespace

from ncc.reactivation import (
    detect_reactivation_sources,
    memory_trace_coverage,
    source_distribution,
)


def test_reactivation_source_manual_input():
    observation = SimpleNamespace(
        raw="On prépare l'installation Mac local-first.",
        temporal=[],
        memorial=[],
    )

    sources = detect_reactivation_sources(
        required_constraints=["target_os=mac", "local_first"],
        current_constraints=["target_os=mac", "local_first"],
        observation=observation,
    )

    assert sources["target_os=mac"] == "manual_input"
    assert sources["local_first"] == "manual_input"


def test_reactivation_source_memory_trace():
    observation = SimpleNamespace(
        raw="Maintenant prépare l'installation.",
        temporal=[],
        memorial=["Ancienne mission: NCC pour Mac en local-first."],
    )

    sources = detect_reactivation_sources(
        required_constraints=["target_os=mac", "local_first"],
        current_constraints=["target_os=mac", "local_first"],
        observation=observation,
    )

    assert sources["target_os=mac"] == "memory_trace"
    assert sources["local_first"] == "memory_trace"


def test_reactivation_source_temporal_context():
    observation = SimpleNamespace(
        raw="Maintenant prépare l'installation.",
        temporal=["Chef, on veut créer une version NCC pour Mac, local-first."],
        memorial=[],
    )

    sources = detect_reactivation_sources(
        required_constraints=["target_os=mac", "local_first"],
        current_constraints=["target_os=mac", "local_first"],
        observation=observation,
    )

    assert sources["target_os=mac"] == "temporal_context"
    assert sources["local_first"] == "temporal_context"


def test_memory_trace_coverage():
    sources = {
        "target_os=mac": "memory_trace",
        "local_first": "active_intent",
    }

    assert memory_trace_coverage(sources) == 0.5


def test_source_distribution():
    sources = {
        "target_os=mac": "memory_trace",
        "local_first": "active_intent",
        "jsonl_traces": "active_intent",
    }

    assert source_distribution(sources) == {
        "memory_trace": 1,
        "active_intent": 2,
    }
