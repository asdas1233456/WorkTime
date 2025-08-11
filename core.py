# core.py  —— 加班计算 + AI 再分配
import json, datetime as dt, re, chinese_calendar as calendar
import os

import pandas as pd
from openai import OpenAI
from config import CFG

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
        off += dt.timedelta(days=1)
    if off.hour == 0:
        return 0.0, 0.0

    dur = (off - on).total_seconds() / 3600
    std_start = parse(date, CFG["std_start"])
    effective_start = max(on, std_start)

    if calendar.is_workday(date):
        ot_old = max(0, dur - 9)
        ot_after_9 = max(0, (off - effective_start).total_seconds()/3600 - 9)
    else:
        ot_old = max(0, dur - CFG["nonworkday_deduct"] if dur >= 5 else dur)
        ot_after_9 = ot_old
    return ot_old, ot_after_9

def ai_allocate(current: dict, days_left: int) -> dict:
    client = OpenAI(base_url="https://api.siliconflow.cn/v1",
                    api_key=os.environ["SILICONFLOW_KEY"])
    prompt = f"""
现有员工已加班(9点后)小时数：{current}  
本月剩余工作日：{days_left} 天  
健康提示阈值：{CFG['health_threshold']} h  
要求：  
1. 无每日上限，按 {days_left} 天合理分摊  
2. 每人再分配小时 ≥0，保留 1 位小数  
3. 已加班 ≥{CFG['health_threshold']} h 的人给出健康提醒  
4. 输出 JSON：{"姓名": {"再分配": 小时, "健康提醒": "文本", "预计完成日期": "YYYY-MM-DD"}}
"""
    resp = client.chat.completions.create(model=CFG["ai_model"],
                                          messages=[{"role": "user", "content": prompt}],
                                          max_tokens=1024, temperature=0.3)
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r'```(?:json)?|```', '', raw, flags=re.IGNORECASE)
    raw = raw.replace("“", '"').replace("”", '"').replace("'", '"')
    return json.loads(raw)