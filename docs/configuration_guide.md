# 圓形標籤檢測系統 - 配置與運行指南

## 目錄
1. [環境配置](#環境配置)
2. [數據標籤生成](#數據標籤生成)
3. [模型訓練](#模型訓練)
4. [推論運行](#推論運行)
5. [參數調優指南](#參數調優指南)

---

## 環境配置

### 前置需求
- Python 3.10+
- uv (Python 套件管理器)

### 安裝步驟
```bash
cd /Users/jeeshyang/Workspace/Work/YoloLabs

# 安裝依賴
uv sync
```

### 主要依賴
| 套件 | 版本 | 用途 |
|------|------|------|
| ultralytics | latest | YOLOv8 目標檢測 |
| paddlepaddle | latest | OCR 引擎基礎 |
| paddleocr | latest | 文字識別 |
| opencv-python | latest | 圖像處理 |
| pandas | latest | 數據處理 |
| openpyxl | latest | Excel 輸出 |

---

## 數據標籤生成

使用 Hough Circle 自動生成 YOLO 訓練標籤。

### 運行命令
```bash
uv run python label_tool.py \
    --input pic_demo \
    --output dataset \
    --param2 28 \
    --min-dist 60 \
    --min-radius 42 \
    --max-radius 65 \
    --visualize
```

### 參數說明

| 參數 | 建議值 | 說明 |
|------|--------|------|
| `--input` | `pic_demo` | 輸入圖片目錄 |
| `--output` | `dataset` | 輸出數據集目錄 |
| `--param2` | **28** | Hough 檢測閾值（越低越敏感，越高越精確） |
| `--min-dist` | **60** | 圓心最小間距（防止重複檢測） |
| `--min-radius` | **42** | 最小圓形半徑（像素） |
| `--max-radius` | **65** | 最大圓形半徑（像素） |
| `--train-ratio` | 0.8 | 訓練集比例 |
| `--visualize` | - | 生成可視化圖片驗證 |

### 調優建議
- **檢測太多誤報**: 增加 `param2` (如 30-35)
- **漏檢太多標籤**: 降低 `param2` (如 25-26)
- **重複框**: 增加 `min-dist`
- **標籤大小不匹配**: 調整 `min-radius` 和 `max-radius`

---

## 模型訓練

### 運行命令
```bash
uv run python train.py \
    --epochs 80 \
    --batch 8 \
    --device mps
```

### 參數說明

| 參數 | 建議值 | 說明 |
|------|--------|------|
| `--epochs` | **80** | 訓練輪數（需足夠收斂） |
| `--batch` | **8** | 批次大小（根據顯存調整） |
| `--device` | `mps` | 運算設備：`mps`(Mac)/`cuda`(NVIDIA)/`cpu` |
| `--model` | `yolov8n.pt` | 基礎模型 |
| `--data` | `dataset/data.yaml` | 數據集配置 |
| `--img-size` | 640 | 輸入圖片尺寸 |

### 預期結果
- mAP@50: > 90%
- Precision: > 95%
- Recall: > 90%

### 輸出位置
- 模型權重: `runs/detect/models/circle_detector/weights/best.pt`
- 複製到: `models/best.pt`

---

## 推論運行

### 運行命令
```bash
uv run python main.py \
    --input pic_demo \
    --output result_images \
    --model models/best.pt \
    --confidence 0.35 \
    --device mps
```

### 參數說明

| 參數 | 建議值 | 說明 |
|------|--------|------|
| `--input` / `-i` | `pic_demo` | 輸入圖片目錄 |
| `--output` / `-o` | `result_images` | 輸出目錄 |
| `--model` / `-m` | `models/best.pt` | 模型路徑 |
| `--confidence` / `-c` | **0.35** | 檢測置信度閾值 |
| `--device` | `mps` | 運算設備 |
| `--lang` | `en` | OCR 語言（`en`/`ch`） |
| `--y-tolerance` | auto | 行分組容差（自動計算） |
| `--image` | - | 單張圖片模式 |

### 輸出文件
```
result_images/
├── annotated_*.jpeg     # 標註後的圖片
├── *_results.csv        # 單圖結果
├── combined_results.csv # 合併結果
└── combined_results.xlsx # Excel 格式
```

---

## 參數調優指南

### 置信度閾值調整

| 場景 | confidence 值 | 效果 |
|------|---------------|------|
| 高精度需求 | 0.5 | 較少誤報，可能漏檢 |
| 平衡模式 | **0.35** | 推薦配置 |
| 高召回需求 | 0.25 | 較多檢測，可能誤報 |

### 快速運行腳本

```bash
# 使用封裝腳本（推薦）
./scripts/run.sh pic_demo result_images

# 重新訓練模型
./scripts/train.sh 80 8

# 重新生成標籤
./scripts/label.sh pic_demo dataset
```

---

## 完整流程

1. **放置圖片** → `pic_demo/` 目錄
2. **生成標籤** → `uv run python label_tool.py -i pic_demo -o dataset --param2 28 --min-dist 60 --visualize`
3. **驗證標籤** → 查看 `dataset/visualizations/`
4. **訓練模型** → `uv run python train.py --epochs 80 --device mps`
5. **複製模型** → `cp runs/detect/models/circle_detector/weights/best.pt models/best.pt`
6. **運行推論** → `uv run python main.py -i pic_demo -o result_images --confidence 0.35`
7. **查看結果** → `result_images/`

---

## 當前最佳配置

```yaml
# 標籤生成
param2: 28
min_dist: 60
min_radius: 42
max_radius: 65

# 訓練
epochs: 80
batch_size: 8
device: mps

# 推論
confidence: 0.35
device: mps
lang: en
```
