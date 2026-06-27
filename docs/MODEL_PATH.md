# Chemin vers NCC-LM

## V0 — Runtime déterministe

Objectif : prouver que le cycle NCC est exécutable, traçable et testable.

## V0.1 — Runtime + métriques

Ajouter IP, GR, KMS, GC, FCS.

## V0.2 — Mémoire expérimentale

Tester plusieurs noyaux : exponentiel, puissance, hybride, futur Mittag-Leffler approximé.

## V0.3 — LLM local comme module

Ajouter Ollama ou LM Studio uniquement pour :

```text
extraction d’intention
génération de transformations
résumé de raisonnement
rédaction finale
```

## V1 — NCC-TraceDataset

Accumuler des traces propres et documentées.

## V2 — Fine-tuning léger

Entraîner un petit modèle à prédire les objets NCC : intention, écart, action, feedback.

## V3 — NCC-Adapter

Ajouter des têtes spécialisées :

```text
intent head
gap head
memory head
action head
policy head
feedback head
```

## V4 — NCC-LM

Modèle de langage centré sur l’intention :

```text
x, S_t → I_t, Δ_t, O_t, A_t, M_{t+1}, S_{t+1}
```
