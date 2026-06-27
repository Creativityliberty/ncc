from __future__ import annotations

from pathlib import Path

from ncc.runtime import NCCRuntime
from ncc.schemas import Observation


SCENARIO = [
    # 1. On donne un contexte/objectif initial très clair avec des contraintes
    "Chef, on doit générer le rapport final en format Markdown et toujours l'enregistrer dans reports/final.md.",
    # 2. On change complètement de sujet pour polluer la mémoire à court terme
    "Au fait, tu as pensé à lancer les tests de performance sur le module de gap ?",
    # 3. On continue sur le sujet poubelle
    "Les tests de perf montrent qu'on consomme trop de CPU, il faut optimiser ça.",
    # 4. On revient à l'action finale de manière très ambiguë
    "Bon c'est fait. Génère le livrable maintenant."
]

def memory_reactivation_score(trace) -> float:
    \"\"\"
    Score expérimental : le système s'est-il souvenu qu'un "livrable" 
    dans ce contexte précis signifie "un rapport final en Markdown dans reports/final.md" ?
    \"\"\"
    score = 0.0
    constraints = trace.intent.constraints
    if "produce_markdown_assets" in constraints:
        score += 0.5
    # Si le moteur était très intelligent, il extrairait aussi le path exact
    # Pour l'instant on check au moins s'il a gardé le concept "markdown"
    
    # On ajoute 0.5 si le goal parle du rapport final
    if "rapport" in trace.intent.goal.lower():
        score += 0.5
        
    return score

def main() -> None:
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    rt = NCCRuntime(trace_path="reports/exp_02_traces.jsonl")

    scores = []
    for step_idx, msg in enumerate(SCENARIO):
        trace = rt.step(msg)
        
        # On n'évalue la réactivation que sur le tout dernier tour
        if step_idx == len(SCENARIO) - 1:
            score = memory_reactivation_score(trace)
            scores.append(score)

    # Note: comme on ne score que la dernière étape, avg = la note finale
    avg = scores[0] if scores else 0.0
    verdict = "OK" if avg >= 0.70 else "À améliorer"

    report = f\"\"\"# Rapport expérience 02 — Réactivation de la mémoire

## Objectif

Tester si une intention ou contrainte déclarée loin dans le passé peut être réactivée lorsque l'utilisateur y fait référence de manière implicite.

## Score final de réactivation

{avg:.3f}

## Verdict

{verdict}

## Fichiers produits

- `reports/exp_02_traces.jsonl`
- `reports/exp_02_memory_reactivation_report.md`
\"\"\"
    (reports / "exp_02_memory_reactivation_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
