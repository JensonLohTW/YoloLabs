#!/bin/bash
# Label script - generates YOLO labels from images
set -e

cd "$(dirname "$0")/.."

INPUT=${1:-pic_demo}
OUTPUT=${2:-dataset}

echo "Generating labels..."
echo "Input: $INPUT"
echo "Output: $OUTPUT"

uv run python label_tool.py --input "$INPUT" --output "$OUTPUT" --visualize

echo "Labeling complete! Dataset created at $OUTPUT"
