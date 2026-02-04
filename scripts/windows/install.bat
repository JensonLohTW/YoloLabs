@echo off
REM 安裝依賴腳本 (Windows)
REM 用法: scripts\windows\install.bat

cd /d "%~dp0..\.."

echo === 檢查 uv 是否安裝 ===
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo uv 未安裝，正在安裝...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo 請重新開啟命令提示字元後再執行此腳本
    pause
    exit /b 0
)

echo === 安裝 Python 依賴 ===
uv sync

echo === 驗證安裝 ===
uv run python -c "import ultralytics; import paddleocr; print('依賴安裝成功！')"

echo === 安裝完成 ===
echo 現在可以運行: scripts\windows\run_all.bat infer
pause
