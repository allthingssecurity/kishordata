# Data Curation

This document defines the curation rules for turning raw Kishore candidate audio into a better training dataset.

The current packaged dataset in this repo is good enough for a first ACE-Step experiment, but not yet strong enough for reliable singer-identity learning. Use this SOP to build a cleaner `v2` dataset.

## Goal

Train for Kishore Kumar identity, not just generic old Bollywood male singing.

That means the dataset should emphasize:

- clearly Kishore-led solo vocals
- clean diction
- minimal accompaniment bleed
- minimal chorus or duet contamination
- broad melodic coverage
- stable vocal timbre across clips

## Source Priority

Best to worst:

1. official clean stems or multitracks
2. high-quality isolated lead vocals from trusted sources
3. strong source separation from high-quality masters
4. random YouTube "vocals only" uploads

The current repo mostly starts from category 4, which is why quality is limited.

## Keep / Reject Rules

Keep a segment only if all of these are true:

- Kishore is clearly the lead singer
- no obvious second singer overlaps the phrase
- no chorus over the phrase
- words are intelligible without strain
- accompaniment bleed is low enough that the lead vocal is dominant
- the segment is not clipped, crushed, distorted, or phasey
- reverb is not so heavy that consonants smear

Reject a segment if any of these are true:

- duet overlap
- chorus or backing ensemble masking the lead
- loud orchestra bleeding through the whole phrase
- strong AI separation artifacts
- metallic / watery / phasey vocals
- strong pitch instability caused by source separation
- line is too short to be useful
- line is mostly humming, crowd, spoken intro, or noise

## Segment Length

Preferred segment length:

- `6s` to `15s`

Acceptable:

- `4s` to `20s`

Avoid:

- full-song vocal tracks as a single sample
- extremely short fragments
- very long sections with changing instrumentation and chorus

Shorter clean solo phrases are much better than longer noisy ones.

## Content Balance

Try to keep variety across:

- slow romantic phrases
- medium-tempo melodic lines
- higher-energy lines
- low register and mid register
- different vowel/consonant patterns

Do not overload the dataset with many nearly identical phrases from the same song.

## Recommended Folder Layout

Use this for a cleaned dataset rebuild:

```bash
datasets/kishore_voice_dataset_v2/
  00_raw_candidates/
  01_review_keep/
  02_review_reject/
  03_segments_wav/
  04_segments_mp3/
  05_ace_step_data/
  manifests/
```

## Review Workflow

For each raw candidate:

1. listen once end-to-end
2. decide: `keep source`, `maybe`, or `reject`
3. if keeping, cut only the strongest solo phrases
4. name each segment deterministically

Example segment naming:

```bash
kishore_<song_slug>_seg001.wav
kishore_<song_slug>_seg002.wav
```

## Prompt Rules

Prompts should be consistent and simple.

Required prompt concepts:

- `kishore kumar`
- `kishore kumar voice`
- `classic bollywood`
- `male solo`
- `warm baritone`

Optional modifiers:

- `melodious`
- `romantic`
- `nostalgic`
- `playback singing`
- `soft strings`
- `gentle orchestra`

Avoid prompt drift. Do not invent a totally different prompt style per sample.

## Lyrics Rules

For ACE-Step, lyrics are optional but recommended.

If adding lyrics:

- use only the sung line in the kept segment
- do not include extra lines not heard in the audio
- preserve the actual language used in the segment
- keep punctuation light and readable

If lyrics are unavailable:

- keep placeholder files for format compatibility
- mark missing lyrics in the manifest

## Manifest Fields

Recommended fields for `v2`:

- `sample_id`
- `song_title`
- `source_file`
- `segment_start_sec`
- `segment_end_sec`
- `duration_sec`
- `language`
- `has_verified_lyrics`
- `prompt`
- `review_status`
- `reject_reason`
- `notes`

## Minimum Quality Standard For Retraining

Do not start a fresh singer-identity run until you have at least:

- `50+` clean solo segments
- low duet/chorus contamination
- consistent prompt format
- preferably at least partial real lyrics

Better to train on:

- `50` clean segments

than:

- `300` noisy full-song vocal files

## What To Do With The Current Dataset

Use the existing packaged set as:

- a baseline experiment
- a pipeline-validation dataset

Do not treat it as final high-quality singer-cloning data.

For a `v2` dataset:

1. start from `audio_keep/`
2. manually segment the best clips
3. discard weak phrases aggressively
4. rebuild ACE-Step packaging from the new segments

## Decision Rule

When unsure whether to keep a segment, reject it.

This workflow benefits more from precision than recall.
