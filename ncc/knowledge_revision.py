from __future__ import annotations


CONTRADICTION_MARKERS = [
    ("organise les agents de langage autour de la mémoire", "ne parle pas du tout de mémoire"),
    ("espace d’action", "ne parle pas du tout d’espace d’action"),
    ("mémoire", "ne parle pas du tout de mémoire"),
]


def normalize(text: str) -> str:
    return text.lower().strip()


def claims_conflict(existing_claim: str, new_claim: str) -> bool:
    old = normalize(existing_claim)
    new = normalize(new_claim)

    for positive, negative in CONTRADICTION_MARKERS:
        if positive in old and negative in new:
            return True
        if positive in new and negative in old:
            return True

    return False


def find_conflicting_claims(state, new_claim: str):
    conflicts = []

    for record in getattr(state, "knowledge_records", []):
        if claims_conflict(record.claim, new_claim):
            conflicts.append(record)

    return conflicts
