#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from acestep.pipeline_ace_step import ACEStepPipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--lora-path", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--lyrics", required=True)
    parser.add_argument("--audio-duration", type=float, default=22.0)
    parser.add_argument("--infer-step", type=int, default=30)
    parser.add_argument("--guidance-scale", type=float, default=12.5)
    parser.add_argument("--scheduler-type", default="euler")
    parser.add_argument("--cfg-type", default="apg")
    parser.add_argument("--omega-scale", type=float, default=10.0)
    parser.add_argument("--manual-seeds", default="24682")
    parser.add_argument("--guidance-interval", type=float, default=0.5)
    parser.add_argument("--guidance-interval-decay", type=float, default=0.0)
    parser.add_argument("--min-guidance-scale", type=float, default=3.0)
    parser.add_argument("--use-erg-tag", action="store_true")
    parser.add_argument("--use-erg-lyric", action="store_true")
    parser.add_argument("--use-erg-diffusion", action="store_true")
    parser.add_argument("--dtype", default="bfloat16")
    args = parser.parse_args()

    params = {
        "lora_name_or_path": args.lora_path,
        "lora_weight": 1.0,
        "prompt": args.prompt,
        "lyrics": args.lyrics,
        "audio_duration": args.audio_duration,
        "infer_step": args.infer_step,
        "guidance_scale": args.guidance_scale,
        "scheduler_type": args.scheduler_type,
        "cfg_type": args.cfg_type,
        "omega_scale": args.omega_scale,
        "manual_seeds": args.manual_seeds,
        "guidance_interval": args.guidance_interval,
        "guidance_interval_decay": args.guidance_interval_decay,
        "min_guidance_scale": args.min_guidance_scale,
        "use_erg_tag": args.use_erg_tag,
        "use_erg_lyric": args.use_erg_lyric,
        "use_erg_diffusion": args.use_erg_diffusion,
        "oss_steps": "",
        "guidance_scale_text": 0.0,
        "guidance_scale_lyric": 0.0,
        "save_path": args.output_path,
    }

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pipe = ACEStepPipeline(
        checkpoint_dir=args.checkpoint_dir,
        dtype=args.dtype,
        torch_compile=False,
        cpu_offload=False,
        overlapped_decode=False,
    )
    result = pipe(**params)
    with open(output_path.with_name(output_path.stem + "_input_params.json"), "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2)
    print(result)


if __name__ == "__main__":
    main()
