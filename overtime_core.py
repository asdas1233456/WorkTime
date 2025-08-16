"""
overtime_core.py
只保留算法，不改原来逻辑。
输入：已 clean 的 DataFrame 和 cfg dict
输出：带 overtime_hours 的 DataFrame 和异常 flag_df（DataFrame）
"""
import datetime as dt
import numpy as np
import pandas as pd
import chinese_calendar as cc

# ---------- 加班计算 ----------
def _calc_overtime(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    ws = dt.datetime.strptime(cfg["office"]["work_start"], "%H:%M")
    we = dt.datetime.strptime(cfg["office"]["work_end"], "%H:%M")

    df = df.copy()
    df["_start_dt"] = pd.to_datetime(df["actual_start"], format="%H:%M")
    df["_end_dt"] = pd.to_datetime(df["actual_end"], format="%H:%M")

    cross = df["_end_dt"] < df["_start_dt"]
    df.loc[cross, "_end_dt"] += pd.Timedelta(days=1)
    df["is_workday"] = df["date"].dt.date.map(cc.is_workday)

    early_ot = (ws - df["_start_dt"]).clip(lower=pd.Timedelta(0)).dt.total_seconds() / 3600
    late_ot = (df["_end_dt"] - we).clip(lower=pd.Timedelta(0)).dt.total_seconds() / 3600
    workday_ot = early_ot + late_ot

    full_dur = (df["_end_dt"] - df["_start_dt"]).dt.total_seconds() / 3600
    non_workday_ot = np.where(full_dur > 5, full_dur - 1, full_dur)

    df["overtime_hours"] = np.where(df["is_workday"], workday_ot, non_workday_ot).round(2)
    return df.drop(columns=["_start_dt", "_end_dt"])

# ---------- 异常标记 ----------
def build_anomaly_flags(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    work_start = dt.datetime.strptime(cfg["office"]["work_start"], "%H:%M")
    work_end = dt.datetime.strptime(cfg["office"]["work_end"], "%H:%M")
    grace = work_start + dt.timedelta(minutes=5)

    flag_df = pd.DataFrame(index=df.index)
    flag_df["date_null"] = df["date"].isna()
    flag_df["absence"] = df[["actual_start", "actual_end"]].isna().any(axis=1)
    flag_df["late"] = False
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

        flag_df.loc[clean_mask, "late"] = (_start > grace) & is_workday
        flag_df.loc[clean_mask, "early"] = (_end < work_end) & is_workday

    flag_df["late_early"] = flag_df["late"] | flag_df["early"]
    return flag_df

# ---------- JSON 导出 ----------
def export_overtime_json(df: pd.DataFrame) -> dict:
    """
    把加班明细 DataFrame → 结构化 dict
    返回值可直接 json.dump
    """
    # 只保留需要字段，避免内部列泄露
    export_cols = ["date", "actual_start", "actual_end",
                   "is_workday", "overtime_hours"]
    out = df[export_cols].copy()
    # 日期转 ISO 字符串
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    # 转 list[dict]
    return out.to_dict("records")