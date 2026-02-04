#!/bin/bash
# Train script - trains the YOLO model
set -e

cd "$(dirname "$0")/.."

# Default parameters
EPOCHS=${1:-100}
BATCH=${2:-16}
DEVICE=${3:-}

echo "Training YOLO model..."
echo "Epochs: $EPOCHS"
echo "Batch size: $BATCH"

if [ -n "$DEVICE" ]; then
    uv run python train.py --epochs "$EPOCHS" --batch "$BATCH" --device "$DEVICE"
else
    uv run python train.py --epochs "$EPOCHS" --batch "$BATCH"
fi

echo "Training complete!"
