# advisor.py
from __future__ import annotations

import datetime as dt
import functools
import logging
import os
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

import chinese_calendar as cc
import pandas as pd
import requests
import yaml

# ---------- 工具 ----------
def _today() -> dt.date:
    return dt.date.today()

def _workdays_left_this_month(from_date: dt.date) -> int:
    month_end = (from_date.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)
    return sum(1 for d in pd.date_range(from_date, month_end, freq='D')
               if cc.is_workday(d.date()))

# ---------- 当年节假日 ----------
@functools.lru_cache(maxsize=1)
def load_this_year_holidays() -> Dict[dt.date, str]:
    holidays = {}
    year = _today().year
    for m in range(1, 13):
        for d in range(1, 32):
            try:
                date = dt.date(year, m, d)
            except ValueError:
                continue
            if cc.is_holiday(date):
                _, holiday_name = cc.get_holiday_detail(date)
                holidays[date] = holiday_name
    return holidays

HOLIDAYS_THIS_YEAR = load_this_year_holidays()

# ---------- 彩蛋文案 ----------
def holiday_egg(today: dt.date) -> dict:
    _EN2CN = {
        "New Year's Day": "元旦",
        "Spring Festival": "春节",
        "Tomb-sweeping Day": "清明",
        "Labour Day": "劳动节",
        "Dragon Boat Festival": "端午节",
        "Mid-Autumn Festival": "中秋节",
        "National Day": "国庆节",
        "Mid-autumn Festival": "中秋节",
    }

    def cn(name: str) -> str:
        return _EN2CN.get(name, name)

    holidays = {d: cn(HOLIDAYS_THIS_YEAR[d]) for d in HOLIDAYS_THIS_YEAR if HOLIDAYS_THIS_YEAR.get(d)}

    this_month = [d for d in holidays if d.year == today.year and d.month == today.month]
    this_month_names = [holidays[d] for d in this_month]
    this_month_txt = (
        "🎉 本月还有假期：" + "、".join(this_month_names) + "！"
        if this_month_names
        else "📅 本月无官方公共假期，继续搬砖！"
    )

    prev_date = max((d for d in holidays if d <= today), default=None)
    if prev_date:
        prev_name = holidays[prev_date]
        prev_days = (today - prev_date).days
        prev_txt = f"⏳ 上一个假期【{prev_name}】已过去 {prev_days} 天，怀念ing～"
    else:
        prev_txt = "⏳ 今年还没放过假，冲鸭！"

    next_date = min((d for d in holidays if d > today), default=None)
    if next_date:
        next_name = holidays[next_date]
        next_days = (next_date - today).days
        next_txt = f"🚀 下一个假期【{next_name}】还有 {next_days} 天，倒计时开始！"
    else:
        next_txt = "🚀 今年已无官方假期，明年见！"

    return {
        "this_month_holiday": this_month_txt,
        "prev_holiday": prev_txt,
        "next_holiday": next_txt,
    }

# ---------- 内置兜底模板 ----------
_BUILTIN = {
    "intro": [
        "今天是 {today}，掐指一算，{phase}已经悄悄上线🫣。",
        "叮！{today} 打卡，{phase}模式已就位。",
        "{today} 了喂，{phase}的加班余额还剩多少？🧮",
    ],
    "stat": [
        "当前已肝 {already:.1f}h / {required}h，缺口 {need:.1f}h，相当于 {eq_days:.1f} 个《甄嬛传》全集😵‍💫。",
        "已攒 {already:.1f}h，离 KPI 还有 {need:.1f}h —— 别慌，宇宙会听见你的 Ctrl+S。",
    ],
    "work_plan": [
        "工作日方案：每天 18:00 往后加 {daily:.1f}h，大概 {end_clock} 收工，坚持 {days_left} 天就能上岸！",
        "工作日：18:00 → {end_clock}（{daily:.1f}h×{days_left}天），就当多蹭公司空调💨。",
    ],
    "sat_plan": [
        "周六方案：还有 {saturdays_left} 个周六，每趟 ≥6h，共可回血 ≥{sat_total_hours:.0f}h。",
        "周六冲量：{saturdays_left} 个 6h 周末，把 KPI 按在地上摩擦！",
    ],
    "month_end_rush": [
        "⚠️ 月末最后冲刺！只剩 {days_left} 个工作日，缺口 {need}h，仅靠工作日已无力回天。",
        "周末连轴转：周六+周日，每天 ≥{weekend_hours}h，共需额外 {remaining}h。",
        "如果周末也不够，请立刻向主管申请 **跨月结转** 或 **临时调休**，别硬刚！",
    ],
    "stat_done": [
        "🎉 本月已加班 {already:.1f}h，KPI 早被甩在身后！再加班就是对 KPI 的不尊重～",
    ],
    "plan_done": [
        "接下来请进入「养生模式」：每天 18:00 准时跑路，周末安心躺平，偶尔回个邮件意思一下就好！",
        "🍃 恭喜下班自由！接下来请严格执行「三不政策」：不加钟、不内卷、不回头！",
        "🛋️ 工时已达标，开启躺平人生：工位咖啡变奶茶，电脑壁纸换成海岛，老板路过自动隐身！",
        "🎣 正式开启摸鱼季：键盘声当白噪音，带薪上厕所 20 分钟起步，周末连公司 Wi-Fi 都懒得连！",
        "🕺 KPI 说拜拜，快乐说嗨嗨！建议把加班灯关掉，把养生壶打开，枸杞泡起！",
        "🌈 加班额度已爆表，老板再喊你就用「下个月再说」魔法攻击，百试百灵！"
],
    "phase_tip": {
        "月初": "月初别浪，周六先攒点余粮，工作日还能摸鱼🐟。",
        "月中": "月中进入拉锯战，周六+工作日双线程，别掉线！",
        "月末": "月末冲刺！周六狂飙+工作日补刀，胜利在望🚩。",
    }

}

# ---------- YAML 热加载 ----------
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts.yml"
_LAST_MTIME = 0

@functools.lru_cache(maxsize=1)
def _load_templates() -> Dict:
    try:
        with open(_PROMPT_FILE, encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
    except Exception as e:
        logging.warning(f"YAML 加载失败: {e}，使用内置模板")
        loaded = {}
    for k, v in _BUILTIN.items():
        loaded.setdefault(k, v)
    return loaded

def _templates() -> Dict:
    global _LAST_MTIME
    try:
        mtime = os.path.getmtime(_PROMPT_FILE)
    except OSError:
        mtime = 0
    if mtime != _LAST_MTIME:
        _load_templates.cache_clear()
        _LAST_MTIME = mtime
    return _load_templates()

# ---------- 文案渲染 ----------
def _render(key: str, **ctx) -> str:
    lines = _templates().get(key, ["(文案缺失)"])
    template = random.choice(lines)
    return template.format_map(defaultdict(lambda: "<?>", ctx))

def _humanize_text(**ctx) -> str:
    ctx.setdefault("eq_days", ctx["need"] / 1.5)
    if ctx["need"] <= 0:        # 已达标
        parts = [
            _render("intro", **ctx),
            _render("stat_done", **ctx),
            _render("plan_done", **ctx),
            _templates()["phase_tip"].get(ctx["phase"], "")
        ]
    else:                       # 仍有缺口
        parts = [
            _render("intro", **ctx),
            _render("stat", **ctx),
            _render("work_plan", **ctx),
            _render("sat_plan", **ctx),
            _templates()["phase_tip"].get(ctx["phase"], "")
        ]
    return "\n".join(parts)

def _humanize_rush(**ctx) -> str:
    ctx.setdefault("remaining", ctx["need"])
    return _render("month_end_rush", **ctx)

# ---------- AI ----------
import traceback
import sys

def _ask_ai(prompt: str, cfg: Dict) -> Tuple[str | None, str]:
    url = cfg["ai"]["api_base"].rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {cfg['ai']['api_key']}"}
    data = {
        "model": cfg["ai"]["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": cfg.get("max_tokens", 400),
        "temperature": cfg.get("temperature", 0.6)
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=cfg.get("timeout", 30))
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"], ""
    except Exception as e:
        traceback.print_exc(file=sys.stdout)   # 完整异常链
        return None, str(e)

# ---------- Prompt 工厂 ----------
def _plain_text_prompt(**ctx) -> str:
    if ctx["need"] <= 0:
        return (
            f"今天是 {ctx['today']}，本月 KPI 要求 {ctx['required']}h，"
            f"你已加班 {ctx['already']:.1f}h，超额完成！"
            f"请用 3 句话幽默地夸我，并给出一条「如何优雅地摸鱼到下月」的建议。"
        )
    return (
        f"今天是 {ctx['today']}，本月 KPI 要求加班 {ctx['required']}h，"
        f"目前已加班 {ctx['already']:.1f}h，缺口 {ctx['need']:.1f}h。\n"
        f"本月还剩 {ctx['days_left']} 个工作日，{ctx['saturdays_left']} 个周六。\n"
        f"请给出一份人性化的加班计划，并用轻松幽默治愈的语气鼓励我。"
        f"周六上班已经很痛苦了还没有钱安慰我一下"
        f"回答时务必在显眼位置先写一句“本月已加班 {ctx['already']:.1f}h”。"
    )

def _plain_rush_prompt(**ctx) -> str:
    return (
        f"紧急！今天是 {ctx['today']}，本月已加班 {ctx['already']:.1f}h，"
        f"加班缺口 {ctx['need']:.1f}h，剩余工作日 {ctx['days_left']} 天。\n"
        f"光靠工作日已无法完成 KPI。请给出一份“月末冲刺”方案，"
        f"包括周末需要加班多少小时，以及如何调整心态。"
        f"回答时务必在显眼位置先写一句“本月已加班 {ctx['already']:.1f}h”。"
    )

# ---------- 主函数 ----------
def make_plan(df: pd.DataFrame, cfg: Dict) -> Tuple[pd.DataFrame, str, Dict]:
    today = _today()
    required = cfg["office"]["required_overtime_hours_monthly"]

    # 仅统计当前月份加班时长
    current_month = pd.Timestamp(today).to_period('M')
    already = float(
        df.loc[
            pd.to_datetime(df["date"]).dt.to_period('M') == current_month,
            "overtime_hours"
        ].sum()
    )
    need = max(required - already, 0)

    # ── 2️⃣ 未达标：继续原有逻辑 ───────────────────────────
    days_total = _workdays_left_this_month(dt.date(today.year, today.month, 1))
    days_left = _workdays_left_this_month(today)
    ratio = 1 - days_left / max(days_total, 1)
    phase = "月初" if ratio < 0.33 else "月中" if ratio < 0.66 else "月末"

    saturdays_left = len(
        pd.date_range(today,
                      (today.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1),
                      freq='W-SAT')
    )
    sat_total_hours = saturdays_left * 6
    remain_after_sat = max(need - sat_total_hours, 0)

    base_cols = {
        "当前日期": today.isoformat(),
        "阶段": phase,
        "已加班小时数": round(already, 1),
        "剩余需加班": round(need, 1),
        "剩余工作日": days_left,
        "工作日每日目标(h)": None,
        "周六剩余": saturdays_left,
        "周末冲刺(h)": None,
        "来源": None,
        "AI错误": None
    }

    holiday_info = holiday_egg(today)
    base_cols.update(holiday_info)
    holiday_emoji_block = "\n".join(holiday_info.values())

    if days_left == 0 or (days_left and remain_after_sat / days_left > 12):
        weekend_hours = max(need / 2, 6)
        prompt = _plain_rush_prompt(
            today=today, already=already, need=need, days_left=days_left,
            weekend_hours=round(weekend_hours, 1)
        ) + f"\n\n假期彩蛋（保留 emoji）：\n{holiday_emoji_block}"
        ai_text, err = _ask_ai(prompt, cfg)
        advice = ai_text if ai_text else (
            _humanize_rush(days_left=days_left, need=need, weekend_hours=round(weekend_hours, 1), remaining=need)
            + "\n\n" + holiday_emoji_block
        )
        base_cols.update({
            "阶段": "月末冲刺",
            "工作日每日目标(h)": "-",
            "周末冲刺(h)": round(weekend_hours, 1),
            "来源": "AI" if ai_text else "兜底",
            "AI错误": err or None
        })
    else:
        daily = max(round(remain_after_sat / max(days_left, 1), 1), 0) if days_left else 0
        end_clock = (dt.datetime.combine(today, dt.time(18, 0))
                     + dt.timedelta(hours=daily)).strftime("%H:%M")
        prompt = _plain_text_prompt(
            today=today, required=required, already=already, need=need,
            days_left=days_left, daily=daily, saturdays_left=saturdays_left
        ) + f"\n\n假期彩蛋（保留 emoji）：\n{holiday_emoji_block}"
        ai_text, err = _ask_ai(prompt, cfg)
        if ai_text:
            advice = ai_text
            src = "AI"
        else:
            advice = (
                _humanize_text(
                    today=today, phase=phase, need=need, already=already,
                    required=required, daily=daily, days_left=days_left,
                    end_clock=end_clock, saturdays_left=saturdays_left,
                    sat_total_hours=sat_total_hours
                )
                + "\n\n" + holiday_emoji_block
            )
            src = "兜底"
        base_cols.update({
            "工作日每日目标(h)": str(daily) if days_left else "-",
            "周末冲刺(h)": "-",
            "来源": src,
            "AI错误": err or None
        })

    json_result = {
        "current_date": today.isoformat(),
        **{k: str(v) for k, v in base_cols.items()},
        "already_overtime_hours": round(already, 1),
        "advice": advice
    }
    summary_df = pd.DataFrame([base_cols])
    return summary_df, advice, json_result