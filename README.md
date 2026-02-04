# Circle Label Detection & OCR System

自動化圓形標籤檢測與文字識別系統，使用 YOLOv8 進行目標檢測，PaddleOCR 進行字符識別。

## 功能特點

- 🎯 **精準檢測**：使用 YOLOv8 檢測圓形藍框標籤
- 📝 **智能 OCR**：PaddleOCR 提取多行文字並自動合併
- 📊 **智能排序**：按「從上到下，從左到右」順序輸出
- 🖼️ **可視化**：在原圖標註檢測框、序號和識別文字
- 📁 **數據導出**：支持 CSV/Excel 格式導出

## 環境配置

### 前置條件
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) 包管理器

### 安裝步驟

```bash
# 克隆項目
cd /path/to/YoloLabs

# 使用 uv 安裝依賴
uv sync

# 驗證安裝
uv run python -c "import ultralytics; import paddleocr; print('OK')"
```

## 使用方法

### 1. 數據標註 (首次使用需執行)

使用自動標註工具生成初始標註：

```bash
uv run python label_tool.py --input pic_demo/ --output dataset/
```

### 2. 模型訓練

```bash
uv run python train.py --epochs 100 --batch 16
```

訓練完成後，模型權重保存於 `models/best.pt`。

### 3. 運行識別

```bash
# 處理單張圖片
uv run python main.py --image pic_demo/image.jpeg

# 處理整個文件夾
uv run python main.py --input pic_demo/ --output result_images/
```

### 4. 查看結果

- 標註圖片：`result_images/`
- 數據文件：`output.csv` 或 `output.xlsx`

## 項目結構

```
YoloLabs/
├── pic_demo/              # 輸入圖片
├── dataset/               # YOLO 訓練數據
│   ├── images/
│   ├── labels/
│   └── data.yaml
├── models/                # 訓練好的模型權重
├── result_images/         # 輸出的標註圖片
├── src/                   # 核心模塊
│   ├── detector.py        # YOLO 檢測
│   ├── ocr.py             # PaddleOCR 識別
│   ├── sorter.py          # 排序算法
│   └── utils.py           # 工具函數
├── train.py               # 訓練腳本
├── main.py                # 主程序
├── label_tool.py          # 標註工具
└── README.md
```

## 配置說明

### 排序容差值

在 `src/sorter.py` 中可調整 `y_tolerance` 參數：

```python
# 同一行的 Y 坐標容差（像素）
y_tolerance = 20  # 根據實際圖片調整
```

### OCR 參數

在 `src/ocr.py` 中可配置：

```python
# Mac Apple Silicon 需設置 use_gpu=False
ocr = PaddleOCR(use_gpu=False, lang='ch')
```

## 硬件要求

- **macOS (Apple Silicon)**：使用 MPS 加速 YOLOv8，PaddleOCR 使用 CPU 模式
- **內存**：建議 8GB+

## 授權

MIT License
