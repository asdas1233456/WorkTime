# backend/paths.py
from pathlib import Path

# WorkTime 根目录
ROOT = Path(__file__).resolve().parent.parent
# 常用目录
INPUT_DIR  = ROOT
DATA_DIR = ROOT / "data"
LOG_DIR    = ROOT/ "log"
FRONT_DIR  = ROOT / "frontend"
CONFIG_PATH = ROOT / "config.json"
OUTPUT_DIR = ROOT / "data"                            # 目标：WorkTime/data
OUTPUT_DIR.mkdir(exist_ok=True)
