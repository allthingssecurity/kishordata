#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ACE_STEP_DIR="${ACE_STEP_DIR:-/runpod-volume/work/ACE-Step}"
DATASET_DIR="${DATASET_DIR:-$ACE_STEP_DIR/kishore_lora_dataset}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-/runpod-volume/ace_models}"
LOG_DIR="${LOG_DIR:-/runpod-volume/ace_logs}"
ADAPTER_NAME="${ADAPTER_NAME:-kishore_lora_a100_resume}"
MAX_STEPS="${MAX_STEPS:-500}"
SAVE_EVERY_STEPS="${SAVE_EVERY_STEPS:-100}"
KEEP_LAST="${KEEP_LAST:-2}"
REPEAT_COUNT="${REPEAT_COUNT:-300}"

usage() {
  cat <<EOF
usage:
  $0 prepare
  $0 train [resume_lora_dir]
  $0 infer <lora_dir> <output_wav>
  $0 status

env:
  ACE_STEP_DIR=$ACE_STEP_DIR
  DATASET_DIR=$DATASET_DIR
  CHECKPOINT_DIR=$CHECKPOINT_DIR
  LOG_DIR=$LOG_DIR
  ADAPTER_NAME=$ADAPTER_NAME
  MAX_STEPS=$MAX_STEPS
  SAVE_EVERY_STEPS=$SAVE_EVERY_STEPS
  KEEP_LAST=$KEEP_LAST
  REPEAT_COUNT=$REPEAT_COUNT
EOF
}

cmd_prepare() {
  bash "$ROOT_DIR/scripts/runpod_prepare_for_acestep.sh" "$ACE_STEP_DIR" "$REPEAT_COUNT"
}

cmd_train() {
  local resume_lora="${1:-}"
  CHECKPOINT_DIR="$CHECKPOINT_DIR" \
  LOG_DIR="$LOG_DIR" \
  ADAPTER_NAME="$ADAPTER_NAME" \
  MAX_STEPS="$MAX_STEPS" \
  SAVE_EVERY_STEPS="$SAVE_EVERY_STEPS" \
  KEEP_LAST="$KEEP_LAST" \
  bash "$ROOT_DIR/scripts/runpod_train_kishore.sh" "$ACE_STEP_DIR" "$DATASET_DIR" "$resume_lora"
}

cmd_infer() {
  local lora_dir="${1:-}"
  local output_wav="${2:-}"
  if [[ -z "$lora_dir" || -z "$output_wav" ]]; then
    echo "infer needs: <lora_dir> <output_wav>" >&2
    exit 1
  fi
  (
    cd "$ACE_STEP_DIR"
    PYTHONPATH="$ACE_STEP_DIR" python3 "$ROOT_DIR/scripts/infer_acestep_sample.py" \
      --checkpoint-dir "$CHECKPOINT_DIR" \
      --lora-path "$lora_dir" \
      --output-path "$output_wav" \
      --prompt "kishore kumar, kishore kumar voice, kishore kumar style, classic bollywood, melodious male solo, soothing, warm baritone, romantic, nostalgic, gentle orchestra, soft strings, playback singing, english lyrics" \
      --lyrics $'Moonlight lingers while my lonely heart is humming,\nSoftly all your distant memories keep returning,\nThrough the night a tender fragrance falls around me,\nIn the silent dark a faded song is found in me,' \
      --use-erg-tag \
      --use-erg-lyric \
      --use-erg-diffusion
  )
}

cmd_status() {
  echo "== volume =="
  df -h /runpod-volume | tail -n 1 || true
  echo "== train pid =="
  if [[ -f "$LOG_DIR/train_resume.pid" ]]; then
    ps -fp "$(cat "$LOG_DIR/train_resume.pid")" || true
  else
    echo "no pid file"
  fi
  echo "== latest log tail =="
  tail -n 20 "$LOG_DIR/train_resume.out" || true
  echo "== checkpoints =="
  find "$LOG_DIR/lightning_logs" -maxdepth 4 -type d -name "*_lora" | sort || true
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    prepare)
      shift
      cmd_prepare "$@"
      ;;
    train)
      shift
      cmd_train "$@"
      ;;
    infer)
      shift
      cmd_infer "$@"
      ;;
    status)
      shift
      cmd_status "$@"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
