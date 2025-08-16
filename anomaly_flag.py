# anomaly_flag.py
import chinese_calendar as cc
import pandas as pd
from datetime import datetime, date, time

# 只比较“时分”用的安全 dummy 日期
DUMMY_DATE = date(1900, 1, 1)

def flag(df: pd.DataFrame, cfg) -> pd.DataFrame:
    """
    为 DataFrame 打异常标记：
      - date_null  : 日期缺失
      - absence    : 上下班任一缺失
      - late       : 迟到（工作日 & 晚于 grace）
      - early      : 早退（工作日 & 早于下班时间）
    返回一个与 df 同 index 的布尔 DataFrame
    """
    # 基准时间（都用 dummy 日期，避免越界）
    work_start = datetime.combine(DUMMY_DATE, cfg.work_start)
    work_end   = datetime.combine(DUMMY_DATE, cfg.work_end)
    grace      = work_start + pd.Timedelta(minutes=5)

    # 解析实际打卡时间
    start = pd.to_datetime(df["actual_start"], format="%H:%M", errors="coerce")
    end   = pd.to_datetime(df["actual_end"],   format="%H:%M", errors="coerce")

    # 1) 空日期短路 → 不调用 chinese_calendar
    is_work = df["date"].dt.date.map(
        lambda d: cc.is_workday(d) if pd.notna(d) else False
    )

    # 2) 构造布尔标记
    flags = pd.DataFrame(index=df.index)
    flags["date_null"] = df["date"].isna()
    flags["absence"]   = start.isna() | end.isna()
    flags["late"]      = (start > grace) & is_work & ~flags["absence"]
    flags["early"]     = (end   < work_end) & is_work & ~flags["absence"]
    return flags