#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 /path/to/ACE-Step /path/to/kishore_lora_dataset [resume_lora_dir]" >&2
  exit 1
fi

ACE_STEP_DIR="$1"
DATASET_PATH="$2"
RESUME_LORA="${3:-}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-/runpod-volume/ace_models}"
LOG_DIR="${LOG_DIR:-/runpod-volume/ace_logs}"
ADAPTER_NAME="${ADAPTER_NAME:-kishore_lora_a100_resume}"
MAX_STEPS="${MAX_STEPS:-500}"
SAVE_EVERY_STEPS="${SAVE_EVERY_STEPS:-100}"
KEEP_LAST="${KEEP_LAST:-2}"

mkdir -p "$LOG_DIR"

python3 "$(cd "$(dirname "$0")" && pwd)/patch_acestep_for_kishore.py" \
  --ace-step-dir "$ACE_STEP_DIR" \
  --dataset-path "$DATASET_PATH" \
  --checkpoint-dir "$CHECKPOINT_DIR" \
  --resume-lora "$RESUME_LORA" \
  --adapter-name "$ADAPTER_NAME" \
  --max-steps "$MAX_STEPS" \
  --save-every-steps "$SAVE_EVERY_STEPS" \
  --keep-last "$KEEP_LAST" \
  --log-dir "$LOG_DIR"

cd "$ACE_STEP_DIR"
nohup python3 -u run_train_single.py > "$LOG_DIR/train_resume.out" 2>&1 &
echo $! > "$LOG_DIR/train_resume.pid"
echo "Started training PID $(cat "$LOG_DIR/train_resume.pid")"
echo "Log: $LOG_DIR/train_resume.out"
