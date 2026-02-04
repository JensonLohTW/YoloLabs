#!/bin/bash
# 安裝依賴腳本 (Mac/Linux)
# 用法: ./scripts/unix/install.sh

set -e
cd "$(dirname "$0")/../.."

echo "=== 安裝 uv (如未安裝) ==="
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "請重新開啟終端後再執行此腳本"
    exit 0
fi

echo "=== 安裝 Python 依賴 ==="
uv sync

echo "=== 驗證安裝 ==="
uv run python -c "import ultralytics; import paddleocr; print('依賴安裝成功！')"

echo "=== 安裝完成 ==="
echo "現在可以運行: ./scripts/unix/run_all.sh infer"
