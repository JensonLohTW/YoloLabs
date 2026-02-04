#!/bin/bash
# Check script - runs type checking and linting
set -e

cd "$(dirname "$0")/.."

echo "Running type check..."
uv run python -m py_compile src/detector.py src/ocr.py src/sorter.py src/utils.py
uv run python -m py_compile main.py train.py label_tool.py

echo "All checks passed!"
