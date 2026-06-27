# EXP-05 — Knowledge / Memory / Policy Separation Report

## Objectif

Tester si NCC distingue correctement mémoire, connaissance, politique et raisonnement temporaire.

## Scénario

```text
['Chef, on construit NCC-V0 local-first avec traces et rapports.', 'Fait vérifié : CoALA organise les agents de langage autour de la mémoire, de l’espace d’action et de la décision.', 'À partir de maintenant, pour toute action destructive, propose toujours une sauvegarde avant de demander confirmation.', 'Pourquoi la séparation mémoire / connaissance est importante ?', 'Rappelle l’état cognitif séparé du projet.']
```

## Scores

```text
KMS = 1.0
Layer Purity = 1.0
Verdict KMS = OK
Verdict Layer Purity = OK
```

## Vérifications

```text
memory_ok = True
knowledge_ok = True
policy_ok = True
reasoning_not_persisted = True
```

## Interprétation

KMS = 1.0 signifie que :

* la demande projet reste une trace mémoire ;
* le fait vérifié est stocké comme connaissance ;
* le feedback de sécurité devient une règle/politique ;
* la question de raisonnement ne pollue pas la connaissance.

Layer Purity >= 0.9 signifie que les éléments cognitifs ne sont pas mélangés entre les couches.

## Trace

```text
reports/exp_05_knowledge_memory_separation_traces.jsonl
```

