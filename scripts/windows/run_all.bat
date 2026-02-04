@echo off
REM 統一運行腳本 - 從 config.yaml 讀取配置
REM 用法:
REM   scripts\windows\run_all.bat infer    - 運行推論（最常用）
REM   scripts\windows\run_all.bat label    - 生成標籤
REM   scripts\windows\run_all.bat train    - 訓練模型
REM   scripts\windows\run_all.bat all      - 執行完整流程

cd /d "%~dp0..\.."

set ACTION=%1
if "%ACTION%"=="" set ACTION=infer

if "%ACTION%"=="label" goto label
if "%ACTION%"=="train" goto train
if "%ACTION%"=="infer" goto infer
if "%ACTION%"=="all" goto all
goto usage

:label
echo === 生成訓練標籤 ===
uv run python run_with_config.py label
goto end

:train
echo === 訓練模型 ===
uv run python run_with_config.py train
goto end

:infer
echo === 運行推論 ===
uv run python run_with_config.py infer
goto end

:all
echo === 執行完整流程 ===
call %0 label
call %0 train
copy runs\detect\models\circle_detector\weights\best.pt models\best.pt
call %0 infer
goto end

:usage
echo 用法: %0 {label^|train^|infer^|all}
echo   label - 從圖片生成YOLO標籤
echo   train - 訓練檢測模型  
echo   infer - 運行檢測和OCR（最常用，使用已訓練模型）
echo   all   - 執行完整流程
exit /b 1

:end
echo === 完成 ===
