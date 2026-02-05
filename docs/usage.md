# Circle Label Detector - 操作指南

本指南提供在 macOS 和 Windows 上安裝與執行 Circle Label Detector 流程的詳細說明。

## 1. 前置需求 (Prerequisites)

在開始之前，請確保您已安裝以下項目：

*   **Python**: 版本 3.10 或更高。
    *   *檢查版本:* `python --version` 或 `python3 --version`
*   **uv**: 極速的 Python 套件安裝與解析器。

### 安裝 `uv`

**macOS:**
```bash
# 使用 Homebrew
brew install uv
```
*或者，透過 curl 安裝:* `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Windows:**
```powershell
# 使用 pip (如果已安裝 Python)
pip install uv
```
*或者，使用 PowerShell:* `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

---

## 2. 安裝步驟 (Installation)

本專案使用 `pyproject.toml` 進行依賴管理。`uv` 將自動處理虛擬環境的建立以及跨平台的依賴安裝。

### 步驟 1: 克隆存儲庫或下載原始碼
在終端機 (Terminal) 中切換到專案資料夾。
```bash
cd path/to/YoloLabs
```

### 步驟 2: 安裝依賴
執行 sync 指令以安裝 `pyproject.toml` 中定義的所有必要套件。

**macOS & Windows:**
```bash
uv sync
```
*注意：這會建立一個名為 `.venv` 的資料夾，其中包含隔離的 Python 環境。*

---

## 3. 執行流程 (Running the Pipeline)

您可以直接使用 `uv run` 執行流程。這確保指令是在專案的虛擬環境中運行。

### 指令格式
```bash
uv run python main.py [選項]
```

### 3.1. 處理目錄 (批量模式)
處理資料夾中的所有圖像並將結果保存到輸出資料夾。

```bash
uv run python main.py --input <輸入目錄> --output <輸出目錄>
```

**範例:**
```bash
uv run python main.py --input pic_demo --output result_images
```

### 3.2. 處理單張圖像
對特定檔案進行檢測。

```bash
uv run python main.py --image <圖像路徑>
```

**範例:**
```bash
uv run python main.py --image pic_demo/test_image.jpg
```

---

## 4. 配置與參數 (Configuration & Parameters)

| 標記 (Flag) | 簡寫 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | `None` | 包含要處理圖像的輸入目錄。 |
| `--output` | `-o` | `result_images` | 保存結果（圖像、CSV、Excel）的目錄。 |
| `--model` | `-m` | `models/best.pt` | 訓練好的 YOLOv8 模型路徑。 |
| `--confidence`| `-c` | `0.5` | 檢測置信度閾值 (0.0 - 1.0)。較高的值可減少誤報。 |
| `--padding` | | `0` | 在 OCR 之前，檢測到的圓形周圍的額外填充（像素）。如果文字被切斷，增加此值會有幫助。 |
| `--y-tolerance`| | `None` | (進階) 用於排序文字行的垂直像素容差。`None` = 自動計算。 |
| `--device` | | `None` | 強制指定推論裝置 (`cpu`, `mps`, `cuda`)。若留空則自動檢測。 |
| `--lang` | | `en` | OCR 語言代碼 (例如 `en` 為英文, `ch` 為中文)。 |

---

## 5. 故障排除與相容性 (Troubleshooting)

### 平台相容性
本專案設計為可自動檢測您的作業系統與硬體。
- **macOS (Apple Silicon)**: 若可用，可利用 `mps` (Metal Performance Shaders) 進行加速。
- **Windows**: 若有 NVIDIA GPU 且已配置，可利用 `cuda`；否則預設為 `cpu`。

### 常見問題

**1. 找不到 `uv` 指令**
*   請確保在安裝過程中已將 `uv` 加入您的系統 PATH。請重新啟動終端機。

**2. 找不到模型 (Model not found)**
*   請確保模型檔案存在於 `models/best.pt`。如果從不同目錄運行，請使用 `--model path/to/model.pt` 提供完整路徑。

**3. OCR 準確度問題**
*   嘗試增加 `--padding` (例如 `--padding 10`) 以在文字周圍包含更多背景。
*   檢查圖像是否旋轉；目前的流程假設文字是正立的。

**4. 依賴安裝失敗**
*   如果 `uv sync` 在 **PaddlePaddle** 或 **PyTorch** 上失敗，請嘗試更新 `uv`：
    ```bash
    uv self update
    ```
