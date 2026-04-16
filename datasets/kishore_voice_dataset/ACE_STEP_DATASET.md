# ACE-Step Dataset

This repo contains a launch-ready ACE-Step LoRA dataset package built from the curated `audio_keep/` bucket.

ACE-Step training expects exactly three files per sample:

- `sample.mp3`
- `sample_prompt.txt`
- `sample_lyrics.txt`

Per the official `TRAIN_INSTRUCTION.md`, lyrics are optional but recommended. This dataset is therefore valid for prompt-only LoRA training even when lyric placeholders are empty.

## Files

- `ace_step_data/`: packaged MP3 + prompt + lyrics-placeholder triplets
- `ace_step_manifest.tsv`: sample manifest and prompt metadata
- `../audio_keep/`: original curated WAV source files

## Build / Refresh

From repo root:

```bash
python scripts/prepare_acestep_dataset.py
python scripts/validate_acestep_dataset.py
```

## Validation

The validator checks:

- every `.mp3` has matching `_prompt.txt` and `_lyrics.txt`
- prompts are non-empty
- manifest row count matches packaged samples
- manifest sample IDs match packaged sample IDs

Run:

```bash
python scripts/validate_acestep_dataset.py
```

## RunPod / ACE-Step Conversion

After cloning this repo onto a GPU machine and cloning `ace-step/ACE-Step`, run:

```bash
bash scripts/runpod_prepare_for_acestep.sh /path/to/ACE-Step 2000
```

That will:

1. validate the packaged dataset
2. run `convert2hf_dataset.py`
3. create `kishore_lora_dataset/` inside the ACE-Step checkout

## Lyrics Status

Current status:

- prompt metadata: present for all samples
- lyrics metadata: placeholder files present for all samples
- verified lyrics: not included in this repo

This means:

- the dataset is launch-ready for ACE-Step prompt-only LoRA experiments
- the dataset is not a verified lyric-aligned corpus yet

## Recommendation

Use this package for the first training pass.

If the first LoRA shows promising singer-style adaptation, the next upgrade should be manual segmentation and manually sourced lyrics for the strongest subset of clips.
