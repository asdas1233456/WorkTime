from pathlib import Path
import sys
import os

def get_root_path():
    """
    动态获取项目根目录，同时兼容：
    1. 开发环境（直接运行Python脚本）
    2. 打包后环境（PyInstaller/Electron打包的exe）
    """
    if getattr(sys, 'frozen', False):
        # 打包后环境：获取可执行文件所在目录
        if sys.platform == "win32":
            # Windows系统：exe所在目录
            return Path(sys.executable).parent
        else:
            # macOS/Linux系统：可执行文件的上级目录
            return Path(os.path.dirname(sys.executable)).parent
    else:
        # 开发环境：使用原来的相对路径计算（backend目录的上级）
        return Path(__file__).resolve().parent.parent

# 根目录（动态计算，兼容两种环境）
ROOT = get_root_path()

# 常用目录（保持你的原有结构习惯）
INPUT_DIR = ROOT                       # 打卡记录放在根目录
DATA_DIR = ROOT / "data"               # 数据目录
LOG_DIR = ROOT / "log"                 # 日志目录
FRONT_DIR = ROOT / "frontend"          # 前端目录
CONFIG_PATH = ROOT / "config.json"     # 配置文件路径
OUTPUT_DIR = DATA_DIR                  # 输出目录指向data（和你原来一致）

# 确保必要目录存在
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
