# ACE-Step Packaging

This repo includes a helper script to package the curated `audio_keep/` bucket into an ACE-Step-compatible `data/` directory.

## Script

Run:

```bash
python scripts/prepare_acestep_dataset.py
```

Default outputs:

- `datasets/kishore_voice_dataset/ace_step_data/`
- `datasets/kishore_voice_dataset/ace_step_manifest.tsv`

## Output Format

For each `keep` sample, the script creates:

- `sample.mp3`
- `sample_prompt.txt`
- `sample_lyrics.txt`

This matches the ACE-Step training doc requirement.

## Important Limitation

`*_lyrics.txt` files are intentionally created empty because verified lyrics are not available in this repo yet.

That means this package is suitable for:

- structural dataset preparation
- RunPod handoff
- later ACE-Step conversion once lyrics are filled

It is **not** a final lyric-conditioned ACE-Step training dataset until the lyrics files are populated and reviewed.
