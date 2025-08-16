# report_overtime.py
import json
import pandas as pd
from data_cleaner import clean
from overtime_core import build_anomaly_flags, _calc_overtime
from overtime_logger import write_log

def report_overtime(path: str, cfg_path: str) -> pd.DataFrame:
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)

    df = clean(path)
    flag_df = build_anomaly_flags(df, cfg)
    write_log(df, flag_df)

    bad_mask = flag_df[["date_null", "absence", "late_early"]].any(axis=1)
    df = df[~bad_mask].copy()
    df = _calc_overtime(df, cfg)
    return df.drop(columns=["raw_row"])