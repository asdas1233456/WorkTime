# main.py
import json
from report_overtime import report_overtime
from advisor import make_plan
from paths import CONFIG_PATH, OUTPUT_DIR, INPUT_DIR
# ---------- 主流程 ----------
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def main():
    # 1) 生成明细
    df = report_overtime(INPUT_DIR / "打卡记录.xlsx",CONFIG_PATH)

    # 2) 读配置
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)

    # 3) 生成计划（返回四值：DataFrame + 文本 + JSON + 错误）
    summary_df, advice, json_result= make_plan(df, cfg)

    # 4) 落盘
    with open(OUTPUT_DIR /"加班计划.txt", "w", encoding="utf-8") as f:
        f.write(advice)
    with open(OUTPUT_DIR /"加班计划.json", "w", encoding="utf-8") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=2)

    print("已生成：overtime_report.xlsx / 加班计划.xlsx / 加班计划.txt / 加班计划.json")

if __name__ == "__main__":
    main()