#!/bin/bash
# 統一運行腳本 - 從 config.yaml 讀取配置
# 用法:
#   ./scripts/unix/run_all.sh infer    # 運行推論（最常用）
#   ./scripts/unix/run_all.sh label    # 生成標籤
#   ./scripts/unix/run_all.sh train    # 訓練模型
#   ./scripts/unix/run_all.sh all      # 執行完整流程

set -e
cd "$(dirname "$0")/../.."

ACTION=${1:-infer}

case "$ACTION" in
  label)
    echo "=== 生成訓練標籤 ==="
    uv run python run_with_config.py label
    ;;
  
  train)
    echo "=== 訓練模型 ==="
    uv run python run_with_config.py train
    ;;
  
  infer)
    echo "=== 運行推論 ==="
    uv run python run_with_config.py infer
    ;;
  
  all)
    echo "=== 執行完整流程 ==="
    $0 label
    $0 train
    cp runs/detect/models/circle_detector/weights/best.pt models/best.pt
    $0 infer
    ;;
  
  *)
    echo "用法: $0 {label|train|infer|all}"
    echo "  label - 從圖片生成YOLO標籤"
    echo "  train - 訓練檢測模型"
    echo "  infer - 運行檢測和OCR（最常用，使用已訓練模型）"
    echo "  all   - 執行完整流程"
    exit 1
    ;;
esac

echo "=== 完成 ==="
