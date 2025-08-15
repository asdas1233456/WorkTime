# data_cleaner.py
import pandas as pd, chardet
from typing import Union

def _detect_encoding(path: str) -> str:
    with open(path, "rb") as f:
        return chardet.detect(f.read(100_000))["encoding"] or "utf-8"

def _load_raw(path: str) -> pd.DataFrame:
    path_l = path.lower()
    if path_l.endswith(".xlsx"):
        return pd.read_excel(path, dtype=str)
    elif path_l.endswith(".csv"):
        enc = _detect_encoding(path)
        return pd.read_csv(path, dtype=str, encoding=enc)
    else:
        raise ValueError("仅支持 .xlsx 或 .csv 文件")

def _normalize_date(raw_date) -> Union[pd.Timestamp, None]:
    ts = pd.to_datetime(raw_date, errors="coerce")
    return ts.normalize() if pd.notna(ts) else None

def _normalize_time(raw_time) -> Union[str, None]:
    return None if pd.isna(raw_time) else pd.to_datetime(raw_time, errors="coerce").strftime("%H:%M")

def clean(path: str) -> pd.DataFrame:
    """返回所有行：date, actual_start, actual_end"""
    df_raw = _load_raw(path)

    # 记录原始行号（包含表头行，因此从 2 开始）
    df_raw.insert(0, "_raw_row", range(2, len(df_raw) + 2))

    # 统一处理列名
    df_raw.columns = [str(c).lower() for c in df_raw.columns]

    date_col  = next(c for c in df_raw.columns if "日期" in c or "date" in c)
    start_col = next(c for c in df_raw.columns if "上班" in c or "start" in c)
    end_col   = next(c for c in df_raw.columns if "下班" in c or "end" in c)

    # 组装结果
    df = pd.DataFrame()
    df["raw_row"]        = df_raw["_raw_row"]
    df["date"]           = pd.to_datetime(df_raw[date_col].apply(_normalize_date))
    df["actual_start"]   = df_raw[start_col].apply(_normalize_time)
    df["actual_end"]     = df_raw[end_col].apply(_normalize_time)

    # 去重、排序
    df = (
        df.assign(
            end_ord=lambda x: pd.to_datetime(x["actual_end"], format="%H:%M", errors="coerce"),
            start_ord=lambda x: pd.to_datetime(x["actual_start"], format="%H:%M", errors="coerce")
        )
        .sort_values(["date", "end_ord", "start_ord"], na_position="last")
        .drop_duplicates(subset=["date"], keep="last")
        .drop(columns=["end_ord", "start_ord"])
        .reset_index(drop=True)
    )
    return df