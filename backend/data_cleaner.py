# data_cleaner.py
import os
from pathlib import Path

import pandas as pd
import chardet
from typing import Union
import logging
from backend.paths import DATA_DIR, INPUT_DIR


# ---------- 工具 ----------
def _detect_encoding(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return chardet.detect(f.read(100_000))["encoding"] or "utf-8"
    except Exception as e:
        logging.error(f"编码检测失败：{path} | {e}")
        raise

def _load_raw(path):
    path_l = str(path).lower()
    if path_l.endswith(".xlsx"):
        return pd.read_excel(path, dtype=str, engine="openpyxl")
    elif path_l.endswith(".xls"):
        return pd.read_excel(path, dtype=str, engine="xlrd")
    elif path_l.endswith(".csv"):
        enc = _detect_encoding(path)
        return pd.read_csv(path, dtype=str, encoding=enc)
    else:
        raise ValueError("仅支持 .xls / .xlsx / .csv 文件")

def _normalize_date(raw_date) -> Union[pd.Timestamp, None]:
    try:
        ts = pd.to_datetime(raw_date, errors="coerce")
        return ts.normalize() if pd.notna(ts) else None
    except Exception as e:
        logging.error(f"日期解析失败：{raw_date} | {e}")
        return None

def _normalize_time(raw_time) -> Union[str, None]:
    try:
        return None if pd.isna(raw_time) else pd.to_datetime(raw_time, errors="coerce").strftime("%H:%M")
    except Exception as e:
        logging.error(f"时间解析失败：{raw_time} | {e}")
        return None

def _find_column(df: pd.DataFrame, keywords: list[str]) -> str:
    """按关键词查找列名（忽略大小写），找不到抛异常"""
    for kw in keywords:
        for col in df.columns:
            if kw.lower() in str(col).lower():
                return col
    raise KeyError(f"未找到包含 {keywords} 的列")

# ---------- 主入口 ----------
def clean(path: str) -> pd.DataFrame:
    """
    返回清洗后的 DataFrame：
        raw_row, date, actual_start, actual_end
    任何异常都会写入 log/数据清洗异常.txt
    """
    try:
        df_raw = _load_raw(path)

        # 原始行号（含表头，从 2 开始）
        df_raw.insert(0, "raw_row", range(2, len(df_raw) + 2))

        # 统一小写列名
        df_raw.columns = [str(c).lower() for c in df_raw.columns]

        date_col  = _find_column(df_raw, ["日期", "date"])
        start_col = _find_column(df_raw, ["上班", "start"])
        end_col   = _find_column(df_raw, ["下班", "end"])

        df = pd.DataFrame()
        df["raw_row"]      = df_raw["raw_row"]
        df["date"]         = pd.to_datetime(df_raw[date_col].apply(_normalize_date))
        df["actual_start"] = df_raw[start_col].apply(_normalize_time)
        df["actual_end"]   = df_raw[end_col].apply(_normalize_time)

        # 去重、排序：同一天只保留最后一次打卡
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

    except Exception as e:
        logging.error(f"清洗失败：{path} | {e}")
        raise