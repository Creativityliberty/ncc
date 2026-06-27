from __future__ import annotations

from typing import Iterable

from ncc.schemas import MemoryRecord


MEMORY_KEYWORDS: dict[str, list[str]] = {
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
    "installation": ["installation", "install", "setup", "mac", "local"],
}


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(normalize_text(v) for v in value).lower()
    if isinstance(value, dict):
        return " ".join(normalize_text(v) for v in value.values()).lower()
    return str(value).lower()


def extract_query_terms(text: str) -> set[str]:
    normalized = normalize_text(text)
    terms: set[str] = set()

    for constraint, keywords in MEMORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            terms.add(constraint)

    for raw in normalized.replace(".", " ").replace(",", " ").split():
        if len(raw) >= 4:
            terms.add(raw)

    return terms


def memory_record_score(record: MemoryRecord, query: str) -> float:
    query_terms = extract_query_terms(query)
    record_text = normalize_text(
        {
            "content": record.content,
            "constraints": record.constraints,
            "tags": record.tags,
            "event_type": record.event_type,
        }
    )

    if not query_terms:
        return 0.0

    hits = 0

    for term in query_terms:
        keywords = MEMORY_KEYWORDS.get(term, [term])
        if any(keyword in record_text for keyword in keywords):
            hits += 1

    constraint_bonus = 0.25 * len(record.constraints)
    salience_bonus = record.salience

    return round(hits + constraint_bonus + salience_bonus, 3)


class MemoryStore:
    def __init__(self, records: list[MemoryRecord] | None = None):
        self.records = records or []

    def add(self, record: MemoryRecord) -> None:
        self.records.append(record)

    def search(self, query: str, limit: int = 3, min_score: float = 0.75) -> list[MemoryRecord]:
        scored = [
            (memory_record_score(record, query), record)
            for record in self.records
        ]

        scored = [
            (score, record)
            for score, record in scored
            if score >= min_score
        ]

        scored.sort(key=lambda item: item[0], reverse=True)

        return [record for _, record in scored[:limit]]


def build_memory_record(
    *,
    event_type: str,
    content: str,
    constraints: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    salience: float = 0.5,
    source_step: int | None = None,
) -> MemoryRecord:
    return MemoryRecord(
        event_type=event_type,
        content=content,
        constraints=list(constraints or []),
        tags=list(tags or []),
        salience=salience,
        source_step=source_step,
    )
