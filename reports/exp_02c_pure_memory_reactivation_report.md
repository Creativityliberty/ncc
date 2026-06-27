# EXP-02c — Pure Memory Reactivation Report

## Objectif

Tester si NCC peut réactiver des contraintes anciennes depuis `memory_trace`
lorsque le contexte temporel est volontairement limité.

## Contraintes anciennes attendues

```text
['target_os=mac', 'local_first']
```

## Scores

```text
DIR = 1.0
DIR verdict = OK

Memory Trace Coverage = 1.0
Memory verdict = OK
```

## Sources détectées au dernier tour

```json
{'target_os=mac': 'memory_trace', 'local_first': 'memory_trace'}
```

## Distribution des sources

```json
{'memory_trace': 2}
```

## Observation finale

```json
{'raw': 'Maintenant prépare l’installation.', 'spatial': ['Maintenant prépare l’installation.'], 'temporal': [], 'memorial': [{'event_type': 'stable_output', 'content': 'Produire un plan local Mac avec installation, structure du dépôt, tests, expériences et lecture des résultats.', 'constraints': ['target_os=mac', 'local_first', 'include_tests_and_result_interpretation'], 'tags': ['transformation', 'produce_local_plan', 'plan'], 'salience': 0.95, 'source_step': 2}, {'event_type': 'stable_output', 'content': 'Produire un plan local Mac avec installation, structure du dépôt, tests, expériences et lecture des résultats.', 'constraints': ['target_os=mac', 'local_first', 'include_tests_and_result_interpretation'], 'tags': ['transformation', 'produce_local_plan', 'plan'], 'salience': 0.95, 'source_step': 3}, {'event_type': 'stable_output', 'content': 'Produire un plan local Mac avec installation, structure du dépôt, tests, expériences et lecture des résultats.', 'constraints': ['target_os=mac', 'local_first', 'include_tests_and_result_interpretation'], 'tags': ['transformation', 'produce_local_plan', 'plan'], 'salience': 0.95, 'source_step': 4}], 'weight_spatial': 0.5, 'weight_temporal': 0.25, 'weight_memorial': 0.25, 'timestamp': '2026-06-27T19:47:26.641815+00:00'}
```

## Intention finale

```json
{'goal': 'Construire une première version locale NCC-V0 avec installation, tests, traces et documents d’interprétation.', 'constraints': ['target_os=mac', 'local_first', 'include_tests_and_result_interpretation'], 'horizon': 'short', 'expected_action': 'plan', 'salience': 0.85, 'uncertainty': 0.2}
```

## Interprétation

Si DIR = 1.0 et Memory Trace Coverage >= 0.75, NCC ne se contente plus de conserver l’intention
par contexte temporel : il réactive effectivement des traces structurées depuis la mémoire.

Si DIR = 1.0 mais Memory Trace Coverage = 0.0, alors la mémoire pure reste insuffisante.

## Trace

```text
reports/exp_02c_pure_memory_reactivation_traces.jsonl
```

