from __future__ import annotations


AMBIGUOUS_DELETE_PATTERNS = [
    "supprime ce qui ne sert plus",
    "nettoie le projet",
    "fais le nettoyage",
    "supprime les trucs inutiles",
    "delete unused",
    "clean project",
]

INSTALLATION_PATTERNS = [
    "prépare l’installation",
    "prepare installation",
    "installation ncc",
    "installer ncc",
]

PLATFORM_MARKERS = [
    "mac",
    "macos",
    "windows",
    "wsl",
    "wsl2",
    "linux",
    "ubuntu",
]


def normalize_text(text: str) -> str:
    return text.lower().strip()


def is_ambiguous_cleanup_request(user_input: str) -> bool:
    text = normalize_text(user_input)
    return any(pattern in text for pattern in AMBIGUOUS_DELETE_PATTERNS)


def is_installation_without_platform(user_input: str, constraints: list[str]) -> bool:
    text = normalize_text(user_input)

    asks_installation = any(pattern in text for pattern in INSTALLATION_PATTERNS)
    if not asks_installation:
        return False

    has_platform_in_text = any(marker in text for marker in PLATFORM_MARKERS)
    has_platform_constraint = any(
        constraint.startswith("target_os=") or constraint == "wsl2"
        for constraint in constraints
    )

    return not has_platform_in_text and not has_platform_constraint


def clarification_needed(user_input: str, constraints: list[str]) -> tuple[bool, str]:
    if is_ambiguous_cleanup_request(user_input):
        return (
            True,
            "Demande ambiguë de nettoyage/suppression : préciser les fichiers, dossiers ou critères avant toute action.",
        )

    if is_installation_without_platform(user_input, constraints):
        return (
            True,
            "Plateforme cible manquante : préciser Mac, Windows/WSL2 ou Linux avant de préparer l’installation.",
        )

    return False, ""
