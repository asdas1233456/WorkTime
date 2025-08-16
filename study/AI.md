
# 加班计划顾问 `advisor.py` 知识库 🗂️

> 一键生成 **本月加班计划**（阶段 + 周六 + 工作日），AI 失败自动兜底，全部参数可配置。

---
## 📦 文件结构
project/

├─ config.json# AI & 业务参数

├─ overtime_report.xlsx  # 由 report_overtime.py 生成

├─ advisor.py            # ← 本文件

└─ main.py               # 唯一入口
复制

---

## 🧠 功能一览

| 功能 | 说明 |
|---|---|
| **阶段判定** | 月初 / 月中 / 月末 |
| **周六保底** | 每月剩余周六 ≥ 6 h，无上限 |
| **工作日兜底** | 18:00 起算，缺口二次分摊 |
| **AI/兜底切换** | 失败原因自动回显 |
| **配置热加载** | max_tokens/temperature/timeout 写在 `config.json` |

---

## 🔧 配置示例 (`config.json`)

```json
{
  "office": {
    "work_start": "09:00",
    "work_end": "18:00",
    "lunch_break_minutes": 60,
    "required_overtime_hours_monthly": 20
  },
  "ai": {
    "api_base": "https://api.siliconflow.cn/v1",
    "model": "deepseek-ai/DeepSeek-V3",
    "api_key": "sk-xxx",
    "max_tokens": 400,
    "temperature": 0.6,
    "timeout": 30
  }
}
```
🚀 快速使用
```
from advisor import make_plan
summary_df, advice = make_plan(df, cfg)
summary_df.to_excel("加班计划.xlsx", index=False)
with open("加班计划.txt", "w", encoding="utf-8") as f:
    f.write(advice)
```
### 📊 输出字段

| 字段           | 类型  | 说明                           |
|----------------|-------|--------------------------------|
| 当前日期       | date  | 运行当天                       |
| 阶段           | str   | 月初 / 月中 / 月末             |
| 剩余需加班     | float | 还需多少小时                   |
| 剩余工作日     | int   | 本月剩余工作日数               |
| 每日目标(h)    | float | 工作日每日需加班小时           |
| 周六剩余       | int   | 本月剩余周六数（≥6h/次）       |
| 来源           | str   | AI / 兜底                      |

---

### 📈 阶段 & 周六推荐

| 阶段 | 周六策略                     | 工作日策略               |
|------|------------------------------|--------------------------|
| 月初 | 优先排满周六，减轻工作日压力 | 可少量或无需工作日加班   |
| 月中 | 周六 + 工作日并行            | 每日 18:00 起补足剩余   |
| 月末 | 周六多排（≥6h/次）           | 工作日冲刺收尾           |

🛠️ 核心算法
```
# 周六剩余数（无视是否法定）
saturdays_left = len(pd.date_range(today,
                                   today.replace(day=28)+pd.Timedelta(days=4),
                                   freq='W-SAT'))

# 周六总可用 ≥ 6 h × saturdays_left
sat_total = saturdays_left * 6
remain_after_sat = max(need - sat_total, 0)
```

🚩 AI 失败回显
```
复制
【AI 调用失败】HTTPSConnectionPool(host='api.siliconflow.cn', port=443): Read timed out.
```
