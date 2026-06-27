# Spécification NCC-TraceDataset V0

Chaque exécution NCC doit produire une ligne JSONL.

## Champs obligatoires

```json
{
  "step": 1,
  "observation": {},
  "intent": {},
  "gap": {},
  "candidates": [],
  "stable_output": {},
  "reasoning": {},
  "action": {},
  "feedback": {},
  "state_after_summary": {}
}
```

## Usage futur

Ces traces serviront à entraîner un futur modèle à prédire non seulement du texte, mais aussi :

```text
intent
gap
transformation
action
feedback
memory_update
state_update
```

## Règle importante

Ne jamais mélanger données d’expérience, préférences utilisateur, faits scientifiques et politiques de gouvernance dans un seul champ vague. Chaque type doit rester séparé.
