# overtime_logger.py
"""
只做两件事：
1. 写 log/异常汇总.txt（人可读）
2. 写 log/异常汇总.json（机器可读）
"""
import os
import json
import pandas as pd
from paths import LOG_DIR

# ---------- 1. 写 TXT ----------
def write_log(df: pd.DataFrame, flag_df: pd.DataFrame) -> None:
    """
    把异常信息写成 log/异常汇总.txt
    """
    os.makedirs("log", exist_ok=True)

    def _write_table(fp, title, cond):
        sub = df[cond].copy()
        if sub.empty:
            return
        fp.write(f"\n{title}\n")
        header = f"{'序号':<5}{'行号':<8}{'日期':<12}{'上班时间':<10}{'下班时间':<10}{'异常信息'}"
        fp.write(header + "\n")
        fp.write("-" * (len(header) + 10) + "\n")

        for no, (idx, row) in enumerate(sub.iterrows(), 1):
            msg = []
            if flag_df.at[idx, "late"]:
                msg.append("迟到")
            if flag_df.at[idx, "early"]:
                msg.append("早退")
            if flag_df.at[idx, "absence"]:
                msg.append("缺勤")
            if flag_df.at[idx, "date_null"]:
                msg.append("日期信息异常")
            if flag_df.at[idx, "future_date"]:
                msg.append("未来日期")

            fp.write(
                f"{no:<5}"
                f"{int(row['raw_row']):<8}"
                f"{'' if pd.isna(row['date']) else row['date'].strftime('%Y-%m-%d'):<12}"
                f"{str(row['actual_start'] or ''):<10}"
                f"{str(row['actual_end'] or ''):<10}"
                f"{'+'.join(msg)}\n"
            )

    with open(LOG_DIR / "异常汇总.txt", "w", encoding="utf-8") as f:
        _write_table(f, "文件异常", flag_df["date_null"])
        _write_table(f, "考勤异常", flag_df["absence"])
        _write_table(f, "迟到/早退", flag_df["late_early"])
        _write_table(f, "未来日期", flag_df["future_date"])


# ---------- 2. 写 JSON ----------
def export_log_json(df: pd.DataFrame, flag_df: pd.DataFrame) -> list[dict]:
    """
    把异常信息转成结构化 JSON 列表
    """
    result = []
    for idx, row in df.iterrows():
        issues = []
        if flag_df.at[idx, "late"]:
            issues.append("迟到")
        if flag_df.at[idx, "early"]:
            issues.append("早退")
        if flag_df.at[idx, "absence"]:
            issues.append("缺勤")
        if flag_df.at[idx, "date_null"]:
            issues.append("日期信息异常")
        if flag_df.at[idx, "future_date"]:
            issues.append("未来日期")

        if issues:  # 只记录有异常的行
            result.append({
                "raw_row": int(row["raw_row"]),
                "date": None if pd.isna(row["date"]) else row["date"].strftime("%Y-%m-%d"),
                "actual_start": str(row["actual_start"] or ""),
                "actual_end": str(row["actual_end"] or ""),
                "issues": issues
            })
    return result


# ---------- 3. 一键同时导出 ----------
def write_logs(df: pd.DataFrame, flag_df: pd.DataFrame) -> None:
    """
    同时生成 TXT 与 JSON
    """
    write_log(df, flag_df)          # 人可读
    json_log = export_log_json(df, flag_df)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_DIR / "异常汇总.txt", "w", encoding="utf-8") as f:
        json.dump(json_log, f, ensure_ascii=False, indent=2)