# core.py
import json
import re
from datetime import datetime, timedelta

import chinese_calendar as ccal
import pandas as pd
from openai import OpenAI

from config import CFG


# ---------- 工具函数 ----------
def parse_time(date, time_str):
    return pd.to_datetime(str(date)).tz_localize(None) + pd.to_timedelta(str(time_str))

def calc_ot(row):
    date = pd.to_datetime(str(row["date"])).date()
    on = parse_time(date, row["on_duty"])
    off_str = str(row["off_duty"]).strip()
    if not off_str or off_str.lower() == "nan":
        return 0.0, 0.0
    off = parse_time(date, off_str)
    if off.hour == 0 and off.minute == 0:
        off += timedelta(days=1)
    dur = (off - on).total_seconds() / 3600

    std_start = on.replace(hour=9, minute=0, second=0)
    effective_start = max(on, std_start)

    if ccal.is_workday(date):
        ot_old = max(0, dur - 9)
        ot_after_9 = max(0, (off - effective_start).total_seconds() / 3600 - 9)
    else:
        ot_old = max(0, dur - CFG["nonworkday_deduct"] if dur >= 5 else dur)
        ot_after_9 = ot_old
    return ot_old, ot_after_9

# ---------- 阶段 & 剩余工作日 ----------
def current_stage():
    today = datetime.today()
    month_days = (datetime(today.year, today.month % 12 + 1, 1) - timedelta(days=1)).day
    day = today.day
    if day <= month_days // 3:
        return "月初"
    elif day <= 2 * month_days // 3:
        return "月中"
    return "月末"

def remaining_workdays_of_month():
    today = datetime.today()
    last_day = datetime(today.year, today.month % 12 + 1, 1) - timedelta(days=1)
    return [d for d in range((last_day - today).days + 1)
            if ccal.is_workday(today + timedelta(days=d))]

# ---------- AI 建议 ----------
# ---------- 替换 ai_stage_advice ----------
def ai_stage_advice(current: dict, stage: str, days_left: list) -> dict:
    """current: {'姓名': 已加班(9点后)小时}"""
    try:
        # 1. 把配置打出来，确认和调试脚本一致
        print("[debug] api_key =", repr(CFG.get("api_key")))
        print("[debug] model   =", repr(CFG.get("ai_model")))
        print("[debug] current =", current)

        client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=CFG["api_key"],
        )

        prompt = f"""
当前阶段：{stage}
剩余工作日：{len(days_left)} 天
已加班(9点后)小时：{current}

【要求】
1. 无每日上限，按剩余工作日均摊
2. 每人给一句健康建议
3. 仅返回一段合法 JSON，不要添加 Markdown 或多余文字：
{{
  "张三": {{"再分配": 2.5, "建议": "多喝水"}},
  "李四": {{"再分配": 3.0, "建议": "早点睡"}}
}}
"""
        print("[debug] prompt 长度 =", len(prompt))

        # 2. 真正发请求
        resp = client.chat.completions.create(
            model=CFG["ai_model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content or ""
        print("[debug] 原始返回 >>>")
        print(raw)
        print("[debug] <<< 原始返回结束")

        # 3. 解析 JSON
        raw = re.sub(r'^```(?:json)?\s*|```$', '', raw.strip(), flags=re.M | re.I)
        raw = raw.replace("“", '"').replace("”", '"').replace("'", '"')
        parsed = json.loads(raw)
        print("[debug] 解析成功 >>>", parsed)
        return parsed

    except OpenAIError as e:          # 网络 / 鉴权 / 限流
        print("[debug] OpenAIError:", e)
    except json.JSONDecodeError as e: # 返回不是合法 JSON
        print("[debug] JSONDecodeError:", e)
    except Exception as e:            # 兜底
        print("[debug] 其他异常:", e)

    # 任何异常都回到本地兜底
    print("[debug] 进入兜底逻辑")
    return _fallback_advice(current, days_left)

# ---------- 本地兜底 ----------
def _fallback_advice(current: dict, days_left: list) -> dict:
    days = max(len(days_left), 1)
    advice = {}
    for name, hrs in current.items():
        per_day = max(0, (40 - hrs) / days)
        advice[name] = {
            "再分配": round(per_day, 2),
            "建议": "保持作息规律，多喝热水"
        }
    return advice