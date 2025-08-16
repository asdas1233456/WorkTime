import json
import os
import datetime as dt
import chinese_calendar as cc
import numpy as np
import pandas as pd

from data_cleaner import clean


# ---------- 内部：加班计算 ----------
def _calc_overtime(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    ws = dt.datetime.strptime(cfg["office"]["work_start"], "%H:%M")
    we = dt.datetime.strptime(cfg["office"]["work_end"], "%H:%M")

    df = df.copy()
    df["_start_dt"] = pd.to_datetime(df["actual_start"], format="%H:%M")
    df["_end_dt"]   = pd.to_datetime(df["actual_end"], format="%H:%M")

    # 跨天修正
    cross = df["_end_dt"] < df["_start_dt"]
    df.loc[cross, "_end_dt"] += pd.Timedelta(days=1)

    df["is_workday"] = df["date"].dt.date.map(cc.is_workday)

    # 工作日
    early_ot = (ws - df["_start_dt"]).clip(lower=pd.Timedelta(0)).dt.total_seconds() / 3600
    late_ot  = (df["_end_dt"] - we).clip(lower=pd.Timedelta(0)).dt.total_seconds() / 3600
    workday_ot = early_ot + late_ot

    # 非工作日
    full_dur = (df["_end_dt"] - df["_start_dt"]).dt.total_seconds() / 3600
    non_workday_ot = np.where(full_dur > 5, full_dur - 1, full_dur)

    df["overtime_hours"] = np.where(df["is_workday"], workday_ot, non_workday_ot).round(2)
    return df.drop(columns=["_start_dt", "_end_dt"])


# ---------- 主函数 ----------
def report_overtime(path: str, cfg_path: str) -> pd.DataFrame:
    # 1) 读取配置
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)

    work_start = dt.datetime.strptime(cfg["office"]["work_start"], "%H:%M")
    work_end   = dt.datetime.strptime(cfg["office"]["work_end"], "%H:%M")
    grace      = work_start + dt.timedelta(minutes=5)

    # 2) 清洗
    df = clean(path)

    # 3) 异常标记 DataFrame
    flag_df = pd.DataFrame(index=df.index)
    flag_df["date_null"] = df["date"].isna()
    flag_df["absence"]   = df[["actual_start", "actual_end"]].isna().any(axis=1)

    flag_df["late"]  = False
    flag_df["early"] = False

    clean_mask = ~(flag_df["date_null"] | flag_df["absence"])
    if clean_mask.any():
        _start = pd.to_datetime(
            df.loc[clean_mask, "actual_start"], format="%H:%M", errors="coerce"
        )
        _end = pd.to_datetime(
            df.loc[clean_mask, "actual_end"], format="%H:%M", errors="coerce"
        )
        is_workday = df.loc[clean_mask, "date"].dt.date.map(cc.is_workday)

        flag_df.loc[clean_mask, "late"]  = (_start > grace) & is_workday
        flag_df.loc[clean_mask, "early"] = (_end   < work_end) & is_workday

    flag_df["late_early"] = flag_df["late"] | flag_df["early"]

    # 4) 生成美观日志
    os.makedirs("log", exist_ok=True)

    with open("log/异常汇总.txt", "w", encoding="utf-8") as f:
        # 工具函数：写一张表
        def _write_table(title: str, cond: pd.Series):
            sub = df[cond].copy()
            if sub.empty:
                return
            f.write(f"\n{title}\n")
            # 表头 & 分隔线
            header = f"{'序号':<5}{'行号':<8}{'日期':<12}{'上班时间':<10}{'下班时间':<10}{'异常信息'}"
            f.write(header + "\n")
            f.write("-" * (len(header) + 10) + "\n")

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

                f.write(f"{no:<5}"
                        f"{int(row['raw_row']):<8}"
                        f"{'' if pd.isna(row['date']) else row['date'].strftime('%Y-%m-%d'):<12}"
                        f"{str(row['actual_start'] or ''):<10}"
                        f"{str(row['actual_end'] or ''):<10}"
                        f"{'+'.join(msg)}\n")

        # 三张表
        _write_table("文件异常", flag_df["date_null"])
        _write_table("考勤异常", flag_df["absence"])
        _write_table("迟到/早退", flag_df["late_early"])

    # 5) 过滤异常行
    bad_mask = flag_df[["date_null", "absence", "late_early"]].any(axis=1)
    df = df[~bad_mask].copy()

    # 6) 计算加班
    df = _calc_overtime(df, cfg)
    return df.drop(columns=['raw_row'])


# ---------- 入口 ----------
if __name__ == "__main__":
    df_result = report_overtime("打卡记录.xlsx", "config.json")
    df_result.to_excel("overtime_report.xlsx", index=False)
    print("已生成报表： overtime_report.xlsx")