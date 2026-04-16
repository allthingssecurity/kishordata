#!/usr/bin/env python3
import argparse
import csv
import re
import subprocess
from pathlib import Path


BASE_TAGS = [
    "old bollywood",
    "hindi film song",
    "male vocal",
    "solo vocal",
    "playback singing",
    "vintage",
    "kishore kumar style",
]

KEYWORD_TAGS = [
    (re.compile(r"sad|toda|bheegi|safar|chhote|o sathi re", re.I), ["melancholic", "emotional"]),
    (re.compile(r"romantic|pal pal|dil|pyaar|o hansini|tere chehre", re.I), ["romantic", "expressive"]),
    (re.compile(r"mastani|rang|ghungroo|deewana|jaadu", re.I), ["energetic", "lively"]),
    (re.compile(r"naina|rimjhim|saawan|shaam|khwab", re.I), ["melodic", "nostalgic"]),
]

STOPWORDS = re.compile(
    r"\b("
    r"without|music|vocals?|only|no|acapella|kishore|kumar|hit|songs?|"
    r"evergreen|hindi|old|song|style|vocal|audio|classic|playback|sings?|"
    r"jhankar|rajesh|khanna|dharmendra|rakhee|padosan|manzil|gulzar|"
    r"dev|anand|waheeda|rishi|kapoor|amitabh|bachchan|rd|burman"
    r")\b",
    re.I,
)


def slug_to_title(filename: str) -> str:
    stem = Path(filename).stem
    if "__" in stem:
        stem = stem.split("__", 1)[1]
    stem = stem.replace("_", " ")
    stem = re.sub(r"[^A-Za-z0-9 ]+", " ", stem)
    stem = STOPWORDS.sub(" ", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem.title() if stem else "Unknown Track"


def build_tags(title: str) -> list[str]:
    tags = list(BASE_TAGS)
    for pattern, extra in KEYWORD_TAGS:
        if pattern.search(title):
            tags.extend(extra)
    deduped = []
    seen = set()
    for tag in tags:
        if tag not in seen:
            deduped.append(tag)
            seen.add(tag)
    return deduped


def ffmpeg_convert(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-ar",
        "44100",
        "-ac",
        "2",
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "2",
        str(dst),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare ACE-Step dataset from curated Kishore audio.")
    parser.add_argument(
        "--source-dir",
        default="datasets/kishore_voice_dataset/audio_keep",
        help="Directory containing curated WAV files.",
    )
    parser.add_argument(
        "--output-dir",
        default="datasets/kishore_voice_dataset/ace_step_data",
        help="ACE-Step data directory to create.",
    )
    parser.add_argument(
        "--manifest",
        default="datasets/kishore_voice_dataset/ace_step_manifest.tsv",
        help="Output TSV manifest.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    wavs = sorted(source_dir.glob("*.wav"))
    for idx, wav in enumerate(wavs, start=1):
        sample_id = f"kishore_keep_{idx:03d}"
        title = slug_to_title(wav.name)
        tags = build_tags(title)

        mp3_path = output_dir / f"{sample_id}.mp3"
        prompt_path = output_dir / f"{sample_id}_prompt.txt"
        lyrics_path = output_dir / f"{sample_id}_lyrics.txt"

        ffmpeg_convert(wav, mp3_path)
        prompt_path.write_text(", ".join(tags) + "\n")
        # Lyrics are intentionally left blank until manually verified.
        lyrics_path.write_text("")

        rows.append(
            {
                "sample_id": sample_id,
                "source_file": wav.name,
                "song_title_guess": title,
                "prompt_tags": ", ".join(tags),
                "lyrics_status": "missing",
                "mp3_path": str(mp3_path.relative_to(manifest_path.parent.parent if manifest_path.parent.parent.exists() else Path("."))),
            }
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["sample_id", "source_file", "song_title_guess", "prompt_tags", "lyrics_status", "mp3_path"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"prepared {len(rows)} samples")
    print(output_dir)
    print(manifest_path)


if __name__ == "__main__":
    main()
