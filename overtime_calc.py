import chinese_calendar as cc
import pandas as pd, numpy as np, datetime as dt

def calc(df: pd.DataFrame, cfg) -> pd.DataFrame:
    ws = dt.datetime.combine(dt.date.min, cfg.work_start)
    we = dt.datetime.combine(dt.date.min, cfg.work_end)

    start = pd.to_datetime(df["actual_start"], format="%H:%M")
    end   = pd.to_datetime(df["actual_end"],   format="%H:%M")
    end  += (end < start) * pd.Timedelta(days=1)

    is_work = df["date"].dt.date.map(cc.is_workday)

    early = ((ws - start).clip(lower=pd.Timedelta(0))).dt.total_seconds()/3600
    late  = ((end - we).clip(lower=pd.Timedelta(0))).dt.total_seconds()/3600
    work_ot = early + late

    full = (end - start).dt.total_seconds()/3600
    non_work_ot = np.where(full > 5, full - 1, full)

    return df.assign(overtime_hours=np.where(is_work, work_ot, non_work_ot).round(2))