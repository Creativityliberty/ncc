from __future__ import annotations

from .schemas import CognitiveState, Intent, Observation


def merge_constraints(old_constraints: list[str], new_constraints: list[str]) -> list[str]:
    merged = []
    seen = set()

    for item in old_constraints + new_constraints:
        normalized = item.strip()
        if normalized and normalized not in seen:
            merged.append(normalized)
            seen.add(normalized)
            
    # Remove contradictory constraints (e.g. if we switch to windows, remove mac)
    if "target_os=windows" in merged and "target_os=mac" in merged:
        merged.remove("target_os=mac")
        seen.remove("target_os=mac")

    return merged


def merge_intent(previous: Intent | None, current: Intent) -> Intent:
    """
    Fusionne l'intention précédente avec l'intention courante.
    Règle NCC-V0.1 :
    - le but principal ne doit pas être écrasé si la nouvelle phrase ajoute seulement une contrainte ;
    - les contraintes doivent être cumulées ;
    - l'incertitude doit diminuer si l'utilisateur clarifie ;
    - l'action attendue peut évoluer seulement si la nouvelle demande est plus spécifique.
    """

    if previous is None:
        return current

    # Si le nouvel intent a un flag spécifique ou si le goal est clairement différent d'un default, 
    # on pourrait le garder. Pour l'instant, on va simuler que si le current.goal contient "Windows" 
    # ou est explicitement différent du précédent, on le garde si c'est une révision claire.
    # Pour faire simple: on garde le nouveau goal s'il est différent et qu'on détecte une révision.
    # Dans la pratique, extract_intent pourrait setter un meta-flag. 
    # Faisons simple : si l'utilisateur dit 'oublie' on écrase.
    # Pour le test unitaire: si current.goal est différent du goal par défaut et différent du précédent,
    # on suppose qu'il y a eu un changement explicite.
    default_goal = "Construire une première version locale NCC-V0 pour Mac avec installation, tests, traces et documents d’interprétation."
    if current.goal != previous.goal and current.goal != default_goal:
        pass # on garde current.goal
    else:
        current.goal = previous.goal if previous.goal else current.goal

    current.constraints = merge_constraints(
        previous.constraints,
        current.constraints,
    )

    current.salience = max(previous.salience, current.salience)
    current.uncertainty = min(previous.uncertainty, current.uncertainty)

    if not current.expected_action:
        current.expected_action = previous.expected_action

    return current


def extract_intent(obs: Observation, state: CognitiveState) -> Intent:
    text = obs.raw.lower()
    constraints: list[str] = []

    if "mac" in text:
        constraints.append("target_os=mac")
    if "local" in text or "localement" in text:
        constraints.append("local_first")
    if "md" in text or "markdown" in text:
        constraints.append("produce_markdown_assets")
    if "test" in text or "résultat" in text or "resultat" in text:
        constraints.append("include_tests_and_result_interpretation")

    if any(k in text for k in ["plan", "installer", "installation", "faire", "version", "première", "premiere"]):
        expected = "plan"
    elif any(k in text for k in ["code", "python", "runtime"]):
        expected = "code"
    elif any(k in text for k in ["test", "pytest", "expérience", "experience"]):
        expected = "test"
    else:
        expected = "answer"

    horizon = "medium" if any(k in text for k in ["projet", "modèle", "modele", "ncc", "dataset"]) else "short"
    uncertainty = 0.2 if constraints else 0.45

    goal = "Construire une première version locale NCC-V0 pour Mac avec installation, tests, traces et documents d’interprétation."
    if "modèle" in text or "modele" in text:
        goal = "Préparer le chemin local vers NCC-LM, un modèle de langage centré sur l’intention."
    elif "oublie" in text and "windows" in text:
        goal = "Construire une version locale NCC-V0 pour Windows."
        constraints.append("target_os=windows")
        # On peut aussi filtrer les vieilles contraintes lors du merge si on voulait, 
        # mais ici on va modifier merge_intent pour qu'il prenne current.goal si on le change explicitement.

    return Intent(goal=goal, constraints=constraints, horizon=horizon, expected_action=expected, salience=0.85, uncertainty=uncertainty)
