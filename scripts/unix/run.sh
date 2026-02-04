#!/bin/bash
# Run script - executes the main detection pipeline
set -e

cd "$(dirname "$0")/.."

INPUT=${1:-pic_demo}
OUTPUT=${2:-result_images}

echo "Running circle label detection..."
echo "Input: $INPUT"
echo "Output: $OUTPUT"

uv run python main.py --input "$INPUT" --output "$OUTPUT"

echo "Processing complete! Results saved to $OUTPUT"
