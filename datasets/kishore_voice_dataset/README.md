# Kishore Voice Dataset

This directory contains a staged Kishore Kumar voice dataset snapshot built from YouTube "vocals only" candidates.

## Layout

- `audio_keep/`: 34 files that passed the first automatic QC pass
- `audio_maybe/`: 5 files that need manual listening review
- `audio_reject/`: 1 file rejected automatically
- `manifest.tsv`: combined metadata and QC summary for all 40 downloaded files

## Current Counts

- `keep`: 34
- `maybe`: 5
- `reject`: 1

## Selection Method

The candidate pool was collected from YouTube search results for Kishore Kumar vocal-only uploads, then filtered by:

- title heuristics to remove karaoke, AI cover, lyric-video, instrumental, and obvious non-Kishore items
- duration range checks
- simple signal QC:
  - clipping fraction
  - low-level / sparse audio fraction
  - sample rate and channel inspection
- duet-risk heuristics

This is only a first-pass curation snapshot. It is not yet a guaranteed clean singer-cloning dataset.

## Known Limitations

- many files are likely source-separated uploads, not official stems
- some `keep` files still carry `channel_risk` in `manifest.tsv`
- some files may still include:
  - residual accompaniment bleed
  - chorus overlap
  - duet contamination
  - aggressive denoising or phase artifacts

## Remaining Work Before Training

For RVC-style or ACE-Step LoRA-style singer work, this dataset still needs:

1. manual listening review of all `keep` files
2. likely trimming into shorter clean solo segments
3. removal of chorus and bleed-heavy regions
4. normalized naming
5. lyrics metadata if training ACE-Step lyric-conditioned LoRA
6. prompt/tag metadata if training ACE-Step

## Recommended Next Step

Treat `audio_keep/` as the review queue for manual segmentation, not as final training-ready audio.
