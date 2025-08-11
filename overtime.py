#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import chinese_calendar as calendar
import pulp as pl

# ---------------- 配置 ----------------
CFG = {
    "std_start": "09:00",
    "std_end": "18:00",
    "break_hours": 1,
    "nonworkday_deduct": 1,
    "remaining_total": 50  # 本月剩余需分配加班小时，可改成 0 关闭
}

# ---------------- 工具 ----------------
ROOT = Path(__file__).parent

def load_data(path):
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path)
    else:
        for enc in ("utf-8-sig", "gbk", "utf-8"):
            try:
                df = pd.read_csv(path, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("无法识别的编码")
    df.columns = df.columns.str.strip().str.lower()
    required = {"date", "on_duty", "off_duty", "person"}
    if not required.issubset(df.columns):
        raise ValueError(f"缺少列：{required - set(df.columns)}")
    return df

def parse(date, time_str):
    return pd.to_datetime(date.strftime("%Y-%m-%d") + " " + str(time_str).strip())

def calc_ot(row):
    date, on_str, off_str = row["date"], row["on_duty"], str(row["off_duty"])
    on = parse(date, on_str)
    off_str = off_str.strip()
    if off_str == "" or off_str.lower() == "nan":
        return 0.0, 0.0
    off = parse(date, off_str)
    if off.hour == 0 and off.minute == 0:
        off += pd.Timedelta(days=1)
    if off.hour == 0:
        return 0.0, 0.0

    dur = (off - on).total_seconds() / 3600
    std_start = parse(date, CFG["std_start"])
    effective_start = max(on, std_start)

    if calendar.is_workday(date):
        # 旧逻辑：含早到
        ot_old = max(0, dur - 9)
        # 新逻辑：仅 09:00 之后
        ot_after_9 = max(0, (off - effective_start).total_seconds()/3600 - 9)
    else:
        ot_old   = max(0, dur - CFG["nonworkday_deduct"] if dur >= 5 else dur)
        ot_after_9 = ot_old
    return ot_old, ot_after_9

# ---------------- 主流程 ----------------
file_path = next((ROOT / n for n in ("logs.xlsx", "logs.csv") if (ROOT / n).exists()), None)
if not file_path:
    raise FileNotFoundError("请把 log.xlsx 或 log.csv 放到脚本同目录！")

df = load_data(file_path)
df[["overtime", "overtime_after_9"]] = df.apply(calc_ot, axis=1, result_type="expand")

# 月度汇总
monthly = (
    df.groupby(["person", df.date.dt.to_period("M")])
      .agg(overtime=("overtime", "sum"),
           overtime_after_9=("overtime_after_9", "sum"))
      .reset_index()
)

# ---------------- HTML 报表 ----------------
with open(ROOT / "report.html", "w", encoding="utf-8") as f:
    f.write("""<!doctype html><html lang="zh-CN"><head>
<meta charset="utf-8"><title>加班报表</title></head><body>
<h2>月度加班汇总（小时）</h2>
<table border=1 cellpadding=6>
<tr><th>姓名</th><th>月份</th><th>加班(含早到)</th><th>加班(9点后)</th></tr>""")
    for r in monthly.itertuples():
        f.write(f"<tr><td>{r.person}</td><td>{r.date}</td>"
                f"<td>{r.overtime:.1f}</td><td>{r.overtime_after_9:.1f}</td></tr>")
    f.write("</table>")

# ---------------- 剩余加班再分配 ----------------
if CFG["remaining_total"] > 0:
    current = monthly.set_index("person")["overtime_after_9"].to_dict()
    persons = list(current.keys())
    P = pl.LpVariable.dicts("add", persons, lowBound=0)
    prob = pl.LpProblem("fair", pl.LpMinimize)
    diffs = []
    for i in persons:
        for j in persons:
            d = pl.LpVariable(f"d_{i}_{j}", lowBound=0)
            prob += d >= (current[i] + P[i]) - (current[j] + P[j])
            prob += d >= (current[j] + P[j]) - (current[i] + P[i])
            diffs.append(d)
    prob += pl.lpSum(diffs)
    prob += pl.lpSum(P[p] for p in persons) == CFG["remaining_total"]
    prob.solve(pl.PULP_CBC_CMD(msg=False))

    with open(ROOT / "report.html", "a", encoding="utf-8") as f:
        f.write("<h2>本月剩余加班分配建议（9点后）</h2><table border=1 cellpadding=6>"
                "<tr><th>姓名</th><th>已加班</th><th>再分配</th><th>月末累计</th></tr>")
        for p in sorted(persons):
            add = P[p].varValue
            f.write(f"<tr><td>{p}</td><td>{current[p]:.1f}</td>"
                    f"<td>{add:.1f}</td><td>{current[p]+add:.1f}</td></tr>")
        f.write("</table></body></html>")

print("[OK] report.html 已生成")