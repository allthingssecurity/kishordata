# Kishore ACE-Step Repro

This repo is structured so an agent can pick it up and run the workflow without reconstructing chat history.

## Start Here

Read:

- [RUNPOD_REPRO.md](./RUNPOD_REPRO.md)
- [DATA_CURATION.md](./DATA_CURATION.md)

Use:

- `scripts/runpod_kishore_workflow.sh`

## What The Repo Contains

- `datasets/kishore_voice_dataset/`
  - curated source pool
  - packaged ACE-Step dataset
- `scripts/prepare_acestep_dataset.py`
  - package local audio into ACE-Step triplets
- `scripts/validate_acestep_dataset.py`
  - validate the packaged dataset
- `scripts/runpod_prepare_for_acestep.sh`
  - convert the packaged set into an ACE-Step HF dataset
- `scripts/patch_acestep_for_kishore.py`
  - patch upstream ACE-Step for single-GPU LoRA-only checkpointing
- `scripts/runpod_train_kishore.sh`
  - start training
- `scripts/infer_acestep_sample.py`
  - generate a sample from any saved LoRA
- `scripts/runpod_kishore_workflow.sh`
  - one command entrypoint for `prepare`, `train`, `infer`, `status`
- `DATA_CURATION.md`
  - rules for building a cleaner `v2` singer dataset

## Agent-Friendly Rule

If you are an agent and need to run this:

1. clone this repo and upstream `ACE-Step`
2. run `scripts/runpod_kishore_workflow.sh prepare`
3. run `scripts/runpod_kishore_workflow.sh train`
4. watch `scripts/runpod_kishore_workflow.sh status`
5. run `scripts/runpod_kishore_workflow.sh infer ...`

Do not guess the old shell history. Use the scripts in this repo.
