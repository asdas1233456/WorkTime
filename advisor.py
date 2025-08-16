# advisor.py  （完整整合版，直接替换原文件即可）
import datetime as dt
import functools
import logging
import os
import random
from collections import defaultdict
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

# ---------- 内置兜底模板 ----------
_BUILTIN = {
    "intro": [
        "今天是 {today}，掐指一算，{phase}已经悄悄上线🫣。",
        "叮！{today} 打卡，{phase}模式已就位。",
        "{today} 了喂，{phase}的加班余额还剩多少？🧮"
    ],
    "stat": [
        "当前已肝 {already:.1f}h / {required}h，缺口 {need:.1f}h，相当于 {eq_days:.1f} 个《甄嬛传》全集😵‍💫。",
        "已攒 {already:.1f}h，离 KPI 还有 {need:.1f}h —— 别慌，宇宙会听见你的 Ctrl+S。"
    ],
    "work_plan": [
        "工作日方案：每天 18:00 往后加 {daily:.1f}h，大概 {end_clock} 收工，坚持 {days_left} 天就能上岸！",
        "工作日：18:00 → {end_clock}（{daily:.1f}h×{days_left}天），就当多蹭公司空调💨。"
    ],
    "sat_plan": [
        "周六方案：还有 {saturdays_left} 个周六，每趟 ≥6h，共可回血 ≥{sat_total_hours:.0f}h。",
        "周六冲量：{saturdays_left} 个 6h 周末，把 KPI 按在地上摩擦！"
    ],
    "phase_tip": {
        "月初": "月初别浪，周六先攒点余粮，工作日还能摸鱼🐟。",
        "月中": "月中进入拉锯战，周六+工作日双线程，别掉线！",
        "月末": "月末冲刺！周六狂飙+工作日补刀，胜利在望🚩。"
    }
}

# ---------- YAML 热加载 ----------
_PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts.yml")
_LAST_MTIME = 0

@functools.lru_cache(maxsize=1)
def _load_templates() -> dict:
    """加载 YAML；若失败或缺失字段，用 _BUILTIN 补全"""
    try:
        with open(_PROMPT_FILE, encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
    except Exception as e:
        logging.warning(f"YAML 加载失败: {e}，使用内置模板")
        loaded = {}
    # 补全缺失 key
    for k, v in _BUILTIN.items():
        loaded.setdefault(k, v)
    return loaded

def _templates() -> dict:
    """支持热更新（开发时可每分钟自动重载）"""
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
    """从模板池随机取一行，并安全格式化"""
    lines = _templates().get(key, ["(文案缺失)"])
    template = random.choice(lines)
    return template.format_map(defaultdict(lambda: "<?>", ctx))

def _humanize_text(**ctx) -> str:
    """组装完整兜底文案"""
    ctx.setdefault("eq_days", ctx["need"] / 1.5)  # 1.5h ≈ 一集电视剧
    parts = [
        _render("intro", **ctx),
        _render("stat", **ctx),
        _render("work_plan", **ctx),
        _render("sat_plan", **ctx),
        _templates()["phase_tip"].get(ctx["phase"], "")
    ]
    return "\n".join(parts)

# ---------- AI ----------
def _ask_ai(prompt: str, cfg: dict) -> tuple[str | None, str]:
    try:
        url = cfg["ai"]["api_base"].rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {cfg['ai']['api_key']}"}
        data = {
            "model": cfg["ai"]["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": cfg.get("max_tokens", 400),
            "temperature": cfg.get("temperature", 0.6)
        }
        resp = requests.post(url, headers=headers, json=data, timeout=cfg.get("timeout", 30))
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"], ""
    except Exception as e:
        return None, str(e)

# ---------- 主函数 ----------
def make_plan(df: pd.DataFrame, cfg: dict):
    import chinese_calendar as cc  # 延迟导入，避免循环

    today = _today()
    required = cfg["office"]["required_overtime_hours_monthly"]
    already = df["overtime_hours"].sum()
    need = max(required - already, 0)

    # 阶段 & 周六
    days_total = _workdays_left_this_month(dt.date(today.year, today.month, 1))
    days_left = _workdays_left_this_month(today)
    ratio = 1 - days_left / max(days_total, 1)
    phase = "月初" if ratio < 0.33 else "月中" if ratio < 0.66 else "月末"

    saturdays_left = len(pd.date_range(today,
                                       (today.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1),
                                       freq='W-SAT'))
    sat_total_hours = saturdays_left * 6
    remain_after_sat = max(need - sat_total_hours, 0)

    daily = round(remain_after_sat / days_left, 1) if days_left else 0
    end_clock = (dt.datetime.combine(today, dt.time(18, 0))
                 + dt.timedelta(hours=daily)).strftime("%H:%M")

    # 组装提示并请求 AI
    prompt = _humanize_text(
        today=today,
        phase=phase,
        need=need,
        already=already,
        required=required,
        daily=daily,
        days_left=days_left,
        end_clock=end_clock,
        saturdays_left=saturdays_left,
        sat_total_hours=sat_total_hours
    )
    ai_text, err_msg = _ask_ai(prompt, cfg)
    advice = ai_text if ai_text else prompt

    # 结构化 JSON
    json_result = {
        "current_date": today.isoformat(),
        "phase": phase,
        "need_hours": need,
        "workdays_left": days_left,
        "daily_work_hour": daily if days_left else None,
        "saturdays_left": saturdays_left,
        "source": "AI" if ai_text else "兜底",
        "advice": advice,
        "ai_error": err_msg if err_msg else None
    }

    # DataFrame 摘要
    summary_df = pd.DataFrame([{
        "当前日期": today,
        "阶段": phase,
        "剩余需加班": need,
        "剩余工作日": days_left,
        "每日目标(h)": daily if days_left else "-",
        "周六剩余": saturdays_left,
        "来源": "AI" if ai_text else "兜底",
        "AI错误": err_msg if err_msg else None
    }])
    return summary_df, advice, json_result