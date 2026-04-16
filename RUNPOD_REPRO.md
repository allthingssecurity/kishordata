# RunPod Repro

This repo now contains the minimum pieces needed to reproduce the Kishore ACE-Step experiment without depending on an ad hoc pod shell history.

## What Is Here

- `datasets/kishore_voice_dataset/`
  - curated source pool
  - packaged ACE-Step dataset
- `scripts/runpod_prepare_for_acestep.sh`
  - validates packaged dataset and runs `convert2hf_dataset.py`
- `scripts/patch_acestep_for_kishore.py`
  - patches upstream `ACE-Step/trainer.py`
  - writes a single-GPU launcher `run_train_single.py`
  - replaces giant Lightning checkpoints with lightweight LoRA-only saves every 100 steps
  - prunes older local LoRA folders and keeps the last 2
- `scripts/runpod_train_kishore.sh`
  - applies the patch and starts training
- `scripts/infer_acestep_sample.py`
  - generates a sample from any saved LoRA checkpoint

## Why The Patch Exists

Upstream ACE-Step training was not good enough for this workflow as-is:

- full Lightning `.ckpt` files consumed disk too quickly on the pod
- a single-GPU wrapper was needed for a stable LoRA run
- we wanted direct lightweight LoRA adapter folders every 100 steps

The patch script applies those changes to a fresh ACE-Step checkout.

## Expected Pod Layout

Suggested paths on RunPod:

```bash
/runpod-volume/work/ACE-Step
/runpod-volume/work/kishordata
/runpod-volume/ace_models
/runpod-volume/ace_logs
```

## 1. Clone Repos

```bash
cd /runpod-volume/work
git clone https://github.com/ace-step/ACE-Step.git
git clone https://github.com/allthingssecurity/kishordata.git
```

## 2. Install ACE-Step Dependencies

Use ACE-Step’s own setup instructions. This repo does not vendor ACE-Step itself.

## 3. Build The HF Dataset

```bash
cd /runpod-volume/work/kishordata
bash scripts/runpod_prepare_for_acestep.sh /runpod-volume/work/ACE-Step 300
```

That produces:

```bash
/runpod-volume/work/ACE-Step/kishore_lora_dataset
```

## 4. Start Training

Fresh run:

```bash
cd /runpod-volume/work/kishordata
bash scripts/runpod_train_kishore.sh \
  /runpod-volume/work/ACE-Step \
  /runpod-volume/work/ACE-Step/kishore_lora_dataset
```

Resume from an existing LoRA checkpoint:

```bash
cd /runpod-volume/work/kishordata
bash scripts/runpod_train_kishore.sh \
  /runpod-volume/work/ACE-Step \
  /runpod-volume/work/ACE-Step/kishore_lora_dataset \
  /runpod-volume/ace_logs/lightning_logs/<run_dir>/checkpoints/epoch=0-step=500_lora
```

Useful env vars:

```bash
export CHECKPOINT_DIR=/runpod-volume/ace_models
export LOG_DIR=/runpod-volume/ace_logs
export ADAPTER_NAME=kishore_lora_a100_resume
export MAX_STEPS=500
export SAVE_EVERY_STEPS=100
export KEEP_LAST=2
```

## 5. Watch Training

```bash
tail -f /runpod-volume/ace_logs/train_resume.out
```

Saved checkpoints appear under:

```bash
/runpod-volume/ace_logs/lightning_logs/<run_dir>/checkpoints/
```

Each folder is a lightweight LoRA adapter directory:

```bash
epoch=0-step=100_lora
epoch=0-step=200_lora
...
```

The patch prunes old ones and keeps the latest 2.

## 6. Run Inference

Example English comparison sample:

```bash
cd /runpod-volume/work/ACE-Step
PYTHONPATH=/runpod-volume/work/ACE-Step python3 /runpod-volume/work/kishordata/scripts/infer_acestep_sample.py \
  --checkpoint-dir /runpod-volume/ace_models \
  --lora-path /runpod-volume/ace_logs/lightning_logs/<run_dir>/checkpoints/epoch=0-step=500_lora \
  --output-path /runpod-volume/ace_logs/samples/step1000_kishore_english.wav \
  --prompt "kishore kumar, kishore kumar voice, kishore kumar style, classic bollywood, melodious male solo, soothing, warm baritone, romantic, nostalgic, gentle orchestra, soft strings, playback singing, english lyrics" \
  --lyrics $'Moonlight lingers while my lonely heart is humming,\nSoftly all your distant memories keep returning,\nThrough the night a tender fragrance falls around me,\nIn the silent dark a faded song is found in me,' \
  --use-erg-tag \
  --use-erg-lyric \
  --use-erg-diffusion
```

## 7. Push To Hugging Face

This repo does not store your token. Use the HF CLI or `huggingface_hub` after authenticating on the pod.

At minimum, push:

- latest `checkpoints/epoch=..._lora`
- sample wavs
- sample `*_input_params.json`

## Notes

- Effective progress can be larger than the checkpoint folder name if you resume from an older LoRA and start a fresh trainer run.
- In our run, a resumed `epoch=0-step=500_lora` on top of an older local `step=500_lora` represented roughly effective `1000`.
- Current results suggest this setup learns broad vintage male Bollywood style more easily than strong Kishore identity. Better segmentation and stronger supervision are likely needed.
