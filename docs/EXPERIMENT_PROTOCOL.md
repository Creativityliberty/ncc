# Protocole expérimental NCC-V0

## Question centrale

Le runtime NCC-V0 améliore-t-il la transformation d’une intention en sortie cohérente, mémorielle, gouvernée et actionnable à travers le temps ?

## Expériences V0

### EXP-01 — Préservation de l’intention

Tester si l’intention initiale reste stable malgré des tours supplémentaires.

Métrique :

```text
IP = Intent Preservation
```

Critère minimal :

```text
IP >= 0.75
```

### EXP-02 — Réactivation mémoire

Tester si une préférence ancienne influence une décision future.

### EXP-03 — Gouvernance

Tester si une règle bloque une affirmation ou action interdite.

### EXP-04 — Feedback correctif

Tester si une correction utilisateur modifie les décisions futures.

## Baselines futures

```text
B0 — réponse sans mémoire
B1 — mémoire simple en liste
B2 — mémoire vectorielle
B3 — agent classique avec tools
B4 — NCC-V0
```
