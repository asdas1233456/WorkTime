def _plain_text_prompt(**ctx) -> str:
    return (
        f"今天是 {ctx['today']}，本月 KPI 要求加班 {ctx['required']}h，"
        f"目前已加班 {ctx['already']:.1f}h，缺口 {ctx['need']:.1f}h。\n"
        f"回答时务必在显眼位置先写一句“本月已加班 {ctx['already']:.1f}h”。"
        f"本月还剩 {ctx['days_left']} 个工作日，{ctx['saturdays_left']} 个周六。\n"
        f"请给出一份人性化的加班计划，并用轻松幽默治愈的语气鼓励我。\n"
        f"周六上班已经很痛苦了还没有钱安慰我一下\n"
    )

# 月末冲刺
def _plain_rush_prompt(**ctx) -> str:
    return (
        f"紧急！今天是 {ctx['today']}，本月已加班 {ctx['already']:.1f}h，"
        f"加班缺口 {ctx['need']:.1f}h，剩余工作日 {ctx['days_left']} 天。\n"
        f"光靠工作日已无法完成 KPI。请给出一份“月末冲刺”方案，"
        f"包括周末需要加班多少小时，以及如何调整心态。"
        f"回答时务必在显眼位置先写一句“本月已加班 {ctx['already']:.1f}h”。"
    )