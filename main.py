# main.py
import json
from report_overtime import report_overtime
from advisor import make_plan

# ---------- 主流程 ----------
def main():
    # 1) 生成明细
    df = report_overtime("打卡记录.xlsx", "config.json")
    df.to_excel("overtime_report.xlsx", index=False)

    # 2) 读配置
    with open("config.json", encoding="utf-8") as f:
        cfg = json.load(f)

    # 3) 生成计划（返回四值：DataFrame + 文本 + JSON + 错误）
    summary_df, advice, json_result= make_plan(df, cfg)

    # 4) 落盘
    summary_df.to_excel("加班计划.xlsx", index=False)
    with open("加班计划.txt", "w", encoding="utf-8") as f:
        f.write(advice)
    with open("加班计划.json", "w", encoding="utf-8") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=2)


    print("已生成：overtime_report.xlsx / 加班计划.xlsx / 加班计划.txt / 加班计划.json")

if __name__ == "__main__":
    main()