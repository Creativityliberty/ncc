from __future__ import annotations

from typing import Any


DESTRUCTIVE_KEYWORDS = [
    "supprime",
    "supprimer",
    "delete",
    "remove",
    "rm -rf",
    "efface",
    "effacer",
    "trash",
    "vider",
    "wipe",
    "destroy",
]

SENSITIVE_TARGETS = [
    "reports",
    "data",
    "dataset",
    "traces",
    "fichiers",
    "files",
    "dossier",
    "folder",
    "projet",
    "project",
]


CONFIRMATION_KEYWORDS = [
    "je confirme",
    "confirmé",
    "confirme",
    "confirmed",
    "yes delete",
    "oui supprime",
]


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(_normalize(v) for v in value.values()).lower()
    if isinstance(value, list):
        return " ".join(_normalize(v) for v in value).lower()
    return str(value).lower()


def is_destructive_request(text: Any) -> bool:
    normalized = _normalize(text)

    has_destructive_keyword = any(k in normalized for k in DESTRUCTIVE_KEYWORDS)
    has_sensitive_target = any(k in normalized for k in SENSITIVE_TARGETS)

    return has_destructive_keyword and has_sensitive_target


def has_explicit_confirmation(text: Any) -> bool:
    normalized = _normalize(text)

    return any(k in normalized for k in CONFIRMATION_KEYWORDS)


def governance_decision(user_input: str, action_payload: Any) -> dict:
    """
    Décide si une action doit être bloquée.

    Règle V0.3 :
    Toute action destructive sur des fichiers/projets/données/traces doit être bloquée
    si l’utilisateur n’a pas donné une confirmation explicite.
    """
    combined = f"{user_input} {_normalize(action_payload)}"

    if is_destructive_request(combined) and not has_explicit_confirmation(combined):
        return {
            "allowed": False,
            "reason": "Action destructive détectée sans confirmation explicite.",
            "alternative": "Demander confirmation ou proposer une sauvegarde avant suppression.",
        }

    return {
        "allowed": True,
        "reason": "",
        "alternative": "",
    }
