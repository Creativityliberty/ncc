# NCC Cognitive Dataset — Datasheet

## Dataset

Name: NCC Cognitive Dataset  
Version: ncc-dataset-v0.8

## Motivation

Ce dataset sert à préparer l’entraînement futur de NCC-LM.
Il ne contient pas seulement des couples prompt/réponse.
Il encode des cycles cognitifs complets :
observation, intention, écart, transformation, raisonnement, action, état futur et couches persistantes.

## Composition

Total examples: 42  
Exported examples: 27  
Skipped examples: 15

## Quality

Schema validity: 1.0  
Target completeness: 1.0  
Layer separation integrity: 1.0

## Intended Use

- entraînement expérimental NCC-LM ;
- génération de données cognitives ;
- évaluation de préservation d’intention ;
- évaluation de mémoire et gouvernance ;
- construction de benchmarks internes.

## Limitations

- Dataset encore petit.
- Données issues d’expériences contrôlées.
- Pas encore représentatif du monde réel.
- Ne prouve pas l’existence d’un nouveau modèle de langage.
- Sert uniquement de base de recherche.

## Governance Notes

Avant tout entraînement réel :
- retirer les données privées ;
- vérifier les permissions ;
- anonymiser les entrées sensibles ;
- conserver les métadonnées de provenance ;
- garder la séparation mémoire / connaissance / politique.
