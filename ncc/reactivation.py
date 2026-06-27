from __future__ import annotations

from typing import Any


CONSTRAINT_KEYWORDS: dict[str, list[str]] = {
    "target_os=mac": ["mac", "macos", "os x"],
    "target_os=windows": ["windows", "wsl", "powershell"],
    "local_first": ["local-first", "local first", "local"],
    "include_tests_and_result_interpretation": [
        "tests",
        "test",
        "pytest",
        "rapport",
        "résultats",
        "resultats",
        "interprétation",
        "interpretation",
    ],
    "jsonl_traces": ["jsonl", "trace", "traces", "dataset"],
    "ncc_lm_preparation": ["ncc-lm", "dataset", "fine-tuning", "modèle", "modele"],
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(_normalize_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(_normalize_text(v) for v in value.values())
    return str(value).lower()


def _constraint_is_mentioned(constraint: str, text: Any) -> bool:
    haystack = _normalize_text(text)
    keywords = CONSTRAINT_KEYWORDS.get(constraint, [constraint])

    return any(keyword.lower() in haystack for keyword in keywords)


def detect_reactivation_sources(
    required_constraints: list[str],
    current_constraints: list[str],
    observation: Any,
    active_intent: Any | None = None,
    knowledge: Any | None = None,
) -> dict[str, str]:
    """
    Retourne l'origine la plus probable de chaque contrainte ancienne réactivée.

    Priorité :
    1. manual_input      : la contrainte est répétée dans l'entrée courante.
    2. memory_trace      : elle vient du champ observation.memorial.
    3. temporal_context  : elle vient de l'historique/trajectory.
    4. active_intent     : elle est portée par l'intention active cumulée.
    5. knowledge         : elle est portée par une couche de connaissance.
    6. unknown           : elle est présente mais source non identifiée.
    """
    sources: dict[str, str] = {}

    current_set = set(current_constraints)

    raw = getattr(observation, "raw", "")
    memorial = getattr(observation, "memorial", [])
    temporal = getattr(observation, "temporal", [])

    active_constraints = []
    if active_intent is not None:
        active_constraints = getattr(active_intent, "constraints", []) or []

    for constraint in required_constraints:
        if constraint not in current_set:
            sources[constraint] = "missing"
            continue

        if _constraint_is_mentioned(constraint, raw):
            sources[constraint] = "manual_input"
        elif _constraint_is_mentioned(constraint, memorial):
            sources[constraint] = "memory_trace"
        elif _constraint_is_mentioned(constraint, temporal):
            sources[constraint] = "temporal_context"
        elif constraint in active_constraints:
            sources[constraint] = "active_intent"
        elif _constraint_is_mentioned(constraint, knowledge):
            sources[constraint] = "knowledge"
        else:
            sources[constraint] = "unknown"

    return sources


def memory_trace_coverage(reactivation_source: dict[str, str]) -> float:
    """
    Mesure la part des contraintes réactivées qui viennent réellement de memory_trace.
    """
    if not reactivation_source:
        return 1.0

    total = len(reactivation_source)
    from_memory = sum(1 for src in reactivation_source.values() if src == "memory_trace")

    return round(from_memory / total, 3)


def source_distribution(reactivation_source: dict[str, str]) -> dict[str, int]:
    distribution: dict[str, int] = {}

    for src in reactivation_source.values():
        distribution[src] = distribution.get(src, 0) + 1

    return distribution
