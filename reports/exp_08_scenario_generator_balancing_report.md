# EXP-08 — Scenario Generator + Dataset Balancing

## Objectif
Tester la génération contrôlée de scénarios NCC et mesurer l’équilibrage initial du dataset.

## Scores
Scenario Validity = 1.0
Task Coverage = 0.818
Task Distribution Entropy = 0.974
Clarification Rate = 0.0
Blocked Action Rate = 0.077
Safe Alternative Rate = 0.077
Contradiction Detection Rate = 0.077
Memory Trace Retrieval Rate = 0.103

Scénarios générés = 12
Traces générées = 39

Verdict scénarios = OK
Verdict équilibrage = OK

## Distribution par tâche
```json
{'intent_preservation': 8, 'memory_reactivation': 4, 'memory_trace_retrieval': 4, 'governance_block': 6, 'feedback_consolidation': 4, 'knowledge_memory_separation': 4, 'safe_action_selection': 3, 'contradiction_handling': 3, 'clarification_needed': 3}
```

## Tâches manquantes
```json
['tool_action_planning', 'dataset_quality']
```

## Interprétation
NCC-V0.11 élargit la couverture du générateur de scénarios en ajoutant des familles cognitives absentes de V0.10 : réactivation mémorielle pure, sélection d’action sûre, gestion de contradiction et clarification. Cette étape réduit le biais du dataset vers les tâches déjà réussies et prépare un corpus plus équilibré pour les futurs essais NCC-LM.