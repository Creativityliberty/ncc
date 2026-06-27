# EXP-11 — Local Tiny Causal LM Fine-Tuning Smoke Test

## Objectif

Valider le premier smoke test local de fine-tuning causal sur le dataset SFT NCC.

Cette expérience ne prétend pas entraîner un vrai NCC-LM final. Elle vérifie que le format SFT généré en V0.13 peut être chargé par un petit modèle causal local, tokenisé, entraîné pendant quelques pas, sauvegardé, puis utilisé pour produire des générations de test.

## Statut

```text
Status = skipped
Verdict = SKIPPED
```

## Métriques

```json
{
  "status": "skipped",
  "reason": "No module named 'torch'",
  "verdict": "SKIPPED_HF_DEPENDENCIES_MISSING"
}
```

## Interprétation scientifique

V0.14 valide le passage du dataset SFT NCC vers un pipeline local minimal de fine-tuning causal. Le résultat ne doit pas être interprété comme une preuve de performance linguistique ou cognitive du modèle. La contribution de cette étape est d’ingénierie : elle démontre que le corpus NCC peut être utilisé par un modèle causal local, sauvegardé comme checkpoint et rejoué pour produire des sorties testables.

La prochaine étape sera d’améliorer le contrôle de génération, d’ajouter une évaluation structurée des sorties NCC, puis de comparer le modèle fine-tuné à un modèle non fine-tuné sur les mêmes prompts.
