# EXP-02 — Memory Reactivation Report

## Objectif

Tester si NCC-V0.2 peut réactiver des contraintes anciennes sans que l’utilisateur les répète explicitement.

## Contraintes anciennes attendues

```text
['target_os=mac', 'local_first']
```

## Score DIR

```text
DIR = 1.0
Verdict = OK
```

## Interprétation

Si DIR est supérieur ou égal à 0.75, le système réactive correctement les contraintes anciennes.

Si DIR est inférieur à 0.75, cela signifie que la mémoire ou l’intention active ne conserve pas suffisamment les contraintes nécessaires à l’action tardive.

## Trace

```text
reports/exp_02_memory_reactivation_traces.jsonl
```

