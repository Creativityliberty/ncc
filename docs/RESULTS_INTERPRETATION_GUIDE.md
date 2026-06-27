# Guide d’interprétation des résultats NCC-V0

## 1. Lire les traces

Les traces sont dans :

```text
reports/*.jsonl
```

Chaque ligne représente un cycle NCC :

```text
observation → intent → gap → candidates → stable_output → reasoning → action → feedback → state_after
```

## 2. Métrique IP — Intent Preservation

```text
IP >= 0.75      bon
0.55–0.74       moyen
< 0.55          dérive d’intention
```

Si IP est faible, vérifier :

- l’extracteur d’intention ;
- les contraintes perdues ;
- les interruptions utilisateur ;
- la mémoire de contexte.

## 3. Métrique GR — Gap Reduction

```text
GR > 0          l’écart diminue
GR = 0          pas de progrès
GR < 0          l’écart augmente
```

Si GR est faible, le système produit peut-être des réponses fluides mais pas assez actionnables.

## 4. Mémoire

La mémoire V0 est une approximation avec noyau hybride : exponentiel + puissance. Elle sert à tester la logique, pas à prouver la mémoire fractal-fractionnaire complète.

À observer :

```text
memory_size
memory_strength
traces réactivées
```

## 5. Gouvernance

Vérifier que les actions interdites sont bloquées. Exemple : ne pas déclarer que NCC-V0 prouve déjà l’AGI.

## 6. Verdict scientifique

Une expérience réussie donne le droit de dire :

```text
NCC-V0 exécute localement un cycle cognitif borné, traçable et mesurable.
```

Elle ne donne pas encore le droit de dire :

```text
NCC-V0 est une AGI.
NCC-V0 converge globalement.
NCC-V0 dépasse tous les LLMs.
```
