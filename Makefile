.PHONY: setup test demo exp clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip && pip install -e ".[dev]"

test:
	. .venv/bin/activate && pytest

demo:
	. .venv/bin/activate && python -m ncc.cli demo

exp:
	. .venv/bin/activate && python experiments/exp_01_intent_preservation.py

exp2:
	. .venv/bin/activate && python experiments/exp_02_memory_reactivation.py

exp2b:
	. .venv/bin/activate && python experiments/exp_02b_memory_source_attribution.py

exp2c:
	. .venv/bin/activate && python experiments/exp_02c_pure_memory_reactivation.py

exp3:
	. .venv/bin/activate && python experiments/exp_03_governance_block.py

exp4:
	. .venv/bin/activate && python experiments/exp_04_feedback_consolidation.py
exp6:
	. .venv/bin/activate && python experiments/exp_06_cognitive_dataset_export.py

dataset: exp6

experiments: exp exp2 exp2b exp2c exp3 exp4 exp5 exp6 exp7 exp8 exp8b exp9 exp10 exp11 exp12 exp13 exp14 exp15

quality: exp7

exp7:
	. .venv/bin/activate && python experiments/exp_07_dataset_quality_gates.py

exp8:
	. .venv/bin/activate && python experiments/exp_08_scenario_generator_balancing.py

exp8b:
	. .venv/bin/activate && python experiments/exp_08b_runtime_alignment_hotfix.py

exp9:
	. .venv/bin/activate && python experiments/exp_09_tiny_ncc_lm_training_dry_run.py

train-dry-run: exp9

exp10:
	. .venv/bin/activate && python experiments/exp_10_tiny_sft_format_hf_adapter.py

sft: exp10

exp11:
	. .venv/bin/activate && python experiments/exp_11_local_tiny_causal_lm_smoke_test.py

exp12:
	. .venv/bin/activate && python experiments/exp_12_generation_evaluation_harness.py

exp13:
	. .venv/bin/activate && python experiments/exp_13_base_vs_finetuned_model_comparison.py

exp14:
	. .venv/bin/activate && python experiments/exp_14_real_hf_environment_doctor.py

exp15:
	. .venv/bin/activate && python experiments/exp_15_real_generations_eval_rerun.py

hf-doctor:
	. .venv/bin/activate && python experiments/exp_14_real_hf_environment_doctor.py

hf-runner:
	. .venv/bin/activate && python experiments/exp_14_py311_training_runner.py

clean:
	rm -rf .pytest_cache __pycache__ ncc/__pycache__ tests/__pycache__ reports/*.jsonl
