# EXP-14 — Python 3.11 HF Training Runner

## Objectif

Lancer le smoke test de fine-tuning causal local uniquement si le diagnostic HF est READY.

## Résultat

```json
{
  "doctor_status": "READY",
  "launched": true,
  "command": [
    "/Users/NUMTEMA/Downloads/ncc-v0-mac-starter.zip_1/ncc-v0-mac-starter/.venv-hf/bin/python",
    "experiments/exp_11_local_tiny_causal_lm_smoke_test.py"
  ],
  "returncode": 0,
  "stdout_tail": "{'loss': 10.8265, 'grad_norm': 0.18503110110759735, 'learning_rate': 4e-05, 'epoch': 0.05}\n{'loss': 10.8291, 'grad_norm': 0.22130298614501953, 'learning_rate': 3e-05, 'epoch': 0.1}\n{'loss': 10.8277, 'grad_norm': 0.40579545497894287, 'learning_rate': 2e-05, 'epoch': 0.14}\n{'loss': 10.8281, 'grad_norm': 0.6049244999885559, 'learning_rate': 1e-05, 'epoch': 0.19}\n{'loss': 10.8262, 'grad_norm': 0.37523603439331055, 'learning_rate': 0.0, 'epoch': 0.24}\n{'train_runtime': 14.1844, 'train_samples_per_second': 0.352, 'train_steps_per_second': 0.352, 'train_loss': 10.827506637573242, 'epoch': 0.24}\n=== EXP 11: Local Tiny Causal LM Fine-Tuning Smoke Test ===\nStatus: ok\nBase model: sshleifer/tiny-gpt2\nTrain examples: 21\nVal examples:   3\nTest examples:  3\nMax steps:      5\nTraining loss:  10.827506637573242\nUnsafe findings:1\nReport written to: reports/exp_11_local_tiny_causal_lm_smoke_test_report.md\n",
  "stderr_tail": "max_steps is given, it will override any value given in num_train_epochs\n\n  0%|          | 0/5 [00:00<?, ?it/s]\n 20%|██        | 1/5 [00:13<00:52, 13.17s/it]\n                                             \n\n 20%|██        | 1/5 [00:13<00:52, 13.17s/it]\n 40%|████      | 2/5 [00:13<00:16,  5.56s/it]\n                                             \n\n 40%|████      | 2/5 [00:13<00:16,  5.56s/it]\n 60%|██████    | 3/5 [00:13<00:06,  3.11s/it]\n                                             \n\n 60%|██████    | 3/5 [00:13<00:06,  3.11s/it]\n 80%|████████  | 4/5 [00:13<00:01,  1.99s/it]\n                                             \n\n 80%|████████  | 4/5 [00:13<00:01,  1.99s/it]\n100%|██████████| 5/5 [00:14<00:00,  1.38s/it]\n                                             \n\n100%|██████████| 5/5 [00:14<00:00,  1.38s/it]\n                                             \n\n100%|██████████| 5/5 [00:14<00:00,  1.38s/it]\n100%|██████████| 5/5 [00:14<00:00,  2.84s/it]\n",
  "verdict": "OK"
}
```

## Verdict

```text
OK
```

## Interprétation

Le runner ne force pas l’entraînement si l’environnement est incomplet. Il protège le pipeline en séparant le diagnostic de l’exécution. Lorsque le diagnostic indique READY, il lance EXP-11 dans l’environnement Python actif, idéalement `.venv-hf` basé sur Python 3.11 ou 3.12.
