"""
配置文件驅動的運行腳本
用法: uv run python run_with_config.py {label|train|infer}
"""

import subprocess
import sys
from pathlib import Path

import yaml


def load_config() -> dict:
    """載入配置文件"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("錯誤：找不到 config.yaml")
        sys.exit(1)
    
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_label(cfg: dict):
    """生成訓練標籤"""
    lab = cfg["labeling"]
    paths = cfg["paths"]
    
    cmd = [
        sys.executable, "label_tool.py",
        "-i", paths["input_dir"],
        "-o", paths["dataset_dir"],
        "--param2", str(lab["param2"]),
        "--min-dist", str(lab["min_dist"]),
        "--min-radius", str(lab["min_radius"]),
        "--max-radius", str(lab["max_radius"]),
        "--train-ratio", str(lab["train_ratio"]),
        "--visualize"
    ]
    subprocess.run(cmd, check=True)


def run_train(cfg: dict):
    """訓練模型"""
    tr = cfg["training"]
    
    cmd = [
        sys.executable, "train.py",
        "--epochs", str(tr["epochs"]),
        "--batch", str(tr["batch_size"]),
        "--device", tr["device"]
    ]
    subprocess.run(cmd, check=True)


def run_infer(cfg: dict):
    """運行推論"""
    inf = cfg["inference"]
    paths = cfg["paths"]
    
    cmd = [
        sys.executable, "main.py",
        "-i", paths["input_dir"],
        "-o", paths["output_dir"],
        "-m", inf["model_path"],
        "-c", str(inf["confidence"]),
        "--device", inf["device"],
        "--lang", inf["ocr_lang"]
    ]
    
    if inf.get("y_tolerance"):
        cmd.extend(["--y-tolerance", str(inf["y_tolerance"])])
    
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 2:
        print("用法: uv run python run_with_config.py {label|train|infer}")
        print("  label - 生成訓練標籤")
        print("  train - 訓練模型")
        print("  infer - 運行推論（使用已訓練模型）")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    cfg = load_config()
    
    if action == "label":
        run_label(cfg)
    elif action == "train":
        run_train(cfg)
    elif action == "infer":
        run_infer(cfg)
    else:
        print(f"未知操作: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
