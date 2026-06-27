# EXP-02b — Memory Source Attribution Report

## Objectif

Vérifier si les contraintes anciennes réactivées viennent réellement du champ `memory_trace`
ou si elles sont seulement portées par `active_intent` / `temporal_context`.

## Contraintes anciennes attendues

```text
['target_os=mac', 'local_first']
```

## Scores

```text
DIR = 1.0
DIR verdict = OK

Memory Trace Coverage = 0.0
Memory verdict = Mémoire pure à améliorer
```

## Sources détectées au dernier tour

```json
{'target_os=mac': 'temporal_context', 'local_first': 'temporal_context'}
```

## Distribution des sources

```json
{'temporal_context': 2}
```

## Interprétation

* DIR mesure si les contraintes anciennes sont encore présentes.
* Memory Trace Coverage mesure si elles viennent réellement du canal `memory_trace`.
* Si DIR = 1.0 mais Memory Trace Coverage = 0.0, alors NCC préserve l’intention, mais n’a pas encore prouvé une réactivation mémorielle pure.

## Trace

```text
reports/exp_02b_memory_source_attribution_traces.jsonl
```

