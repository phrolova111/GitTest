#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

EPOCHS="${EPOCHS:-10}"

python src/train.py --epochs "$EPOCHS"
python src/evaluate.py --weights weights/best.pt