#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 /path/to/ACE-Step [repeat_count]" >&2
  exit 1
fi

ACE_STEP_DIR="$1"
REPEAT_COUNT="${2:-2000}"
DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/datasets/kishore_voice_dataset/ace_step_data"
MANIFEST_PATH="$(cd "$(dirname "$0")/.." && pwd)/datasets/kishore_voice_dataset/ace_step_manifest.tsv"

python3 "$(cd "$(dirname "$0")" && pwd)/validate_acestep_dataset.py" \
  --data-dir "$DATA_DIR" \
  --manifest "$MANIFEST_PATH"

cd "$ACE_STEP_DIR"
python convert2hf_dataset.py \
  --data_dir "$DATA_DIR" \
  --repeat_count "$REPEAT_COUNT" \
  --output_name "kishore_lora_dataset"

cat <<'EOF'
Dataset conversion complete.

Suggested next step:
python trainer.py \
  --dataset_path ./kishore_lora_dataset \
  --exp_name kishore_lora \
  --lora_config_path config/zh_rap_lora_config.json
EOF
