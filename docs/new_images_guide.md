# 新圖片推論指南

使用已訓練好的模型對新圖片進行圓形標籤檢測和 OCR 識別。

---

## 前置條件

1. 已安裝依賴（執行安裝腳本）
2. 已有訓練好的模型 `models/best.pt`

---

## 快速開始

### 步驟 1: 放置新圖片

將新圖片放入目錄，例如 `new_images/`

### 步驟 2: 修改配置

編輯 `config.yaml`：

```yaml
paths:
  input_dir: new_images      # 改成你的圖片目錄
  output_dir: result_images  # 輸出位置
```

### 步驟 3: 運行推論

**Mac/Linux:**
```bash
./scripts/unix/run_all.sh infer
```

**Windows:**
```cmd
scripts\windows\run_all.bat infer
```

**跨平台 Python:**
```bash
uv run python run_with_config.py infer
```

---

## 輸出結果

執行後，`result_images/` 目錄會生成：

| 文件 | 說明 |
|------|------|
| `annotated_*.jpeg` | 標註後的圖片（含框和編號） |
| `*_results.csv` | 單圖識別結果 |
| `combined_results.csv` | 所有結果合併 |
| `combined_results.xlsx` | Excel 格式 |

---

## 調整參數

如需調整檢測敏感度，修改 `config.yaml`：

```yaml
inference:
  confidence: 0.35  # 降低可檢測更多，升高減少誤報
```

---

## 常見問題

**Q: 檢測數量比預期少？**
- 降低 `confidence` 值（如 0.25）

**Q: 有太多誤報？**
- 升高 `confidence` 值（如 0.45）

**Q: OCR 識別不準確？**
- 確認圖片清晰度足夠
- 嘗試更換 `ocr_lang`（`en` 或 `ch`）
