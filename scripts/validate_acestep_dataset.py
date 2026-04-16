#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ACE-Step triplet dataset packaging.")
    parser.add_argument(
        "--data-dir",
        default="datasets/kishore_voice_dataset/ace_step_data",
        help="Directory containing ACE-Step mp3/prompt/lyrics triplets.",
    )
    parser.add_argument(
        "--manifest",
        default="datasets/kishore_voice_dataset/ace_step_manifest.tsv",
        help="Optional TSV manifest to cross-check.",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    manifest_path = Path(args.manifest)
    errors: list[str] = []

    mp3s = sorted(data_dir.glob("*.mp3"))
    prompts = sorted(data_dir.glob("*_prompt.txt"))
    lyrics = sorted(data_dir.glob("*_lyrics.txt"))

    sample_ids = [p.stem for p in mp3s]
    for sample_id in sample_ids:
        prompt = data_dir / f"{sample_id}_prompt.txt"
        lyric = data_dir / f"{sample_id}_lyrics.txt"
        if not prompt.exists():
            errors.append(f"missing prompt for {sample_id}")
        elif not prompt.read_text(errors="ignore").strip():
            errors.append(f"empty prompt for {sample_id}")
        if not lyric.exists():
            errors.append(f"missing lyrics placeholder for {sample_id}")

    manifest_rows = []
    if manifest_path.exists():
        with manifest_path.open(newline="") as handle:
            manifest_rows = list(csv.DictReader(handle, delimiter="\t"))
        if len(manifest_rows) != len(mp3s):
            errors.append(
                f"manifest row count mismatch: manifest={len(manifest_rows)} data_dir={len(mp3s)}"
            )
        manifest_ids = {row["sample_id"] for row in manifest_rows}
        data_ids = set(sample_ids)
        missing_manifest = sorted(data_ids - manifest_ids)
        extra_manifest = sorted(manifest_ids - data_ids)
        if missing_manifest:
            errors.append(f"manifest missing sample ids: {', '.join(missing_manifest[:10])}")
        if extra_manifest:
            errors.append(f"manifest has extra sample ids: {', '.join(extra_manifest[:10])}")

    filled_lyrics = 0
    for lyric in lyrics:
        if lyric.read_text(errors="ignore").strip():
            filled_lyrics += 1

    print(f"data_dir={data_dir}")
    print(f"mp3={len(mp3s)} prompt={len(prompts)} lyrics={len(lyrics)}")
    print(f"lyrics_filled={filled_lyrics} lyrics_empty={len(lyrics) - filled_lyrics}")
    if manifest_rows:
        print(f"manifest_rows={len(manifest_rows)}")

    if errors:
        print("validation=failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("validation=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
