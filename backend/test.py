import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 1. 原始数据
raw = [
    {"date": "2025-08-01", "overtime_hours": 4.87},
    {"date": "2025-08-02", "overtime_hours": 7.12},
    {"date": "2025-08-04", "overtime_hours": 3.28},
    {"date": "2025-08-05", "overtime_hours": 3.27},
    {"date": "2025-08-08", "overtime_hours": 1.48},
    {"date": "2025-08-09", "overtime_hours": 8.33}
]

# 2. 补全整月
df = pd.DataFrame(raw)
df['date'] = pd.to_datetime(df['date'])
# 以日期为索引，缺失填 0
df = (df.set_index('date')
        .reindex(pd.date_range('2025-08-01', '2025-08-31'))
        .fillna(0))

# 3. 计算日历网格
start = pd.Timestamp('2025-08-01')
first_weekday = start.weekday()          # 0=Mon ... 6=Sun
days_in_month = 31
total_cells = first_weekday + days_in_month
rows = (total_cells + 6) // 7            # 向上取整

# 先做一个 (rows*7) 的 0 数组，再填充
calendar = np.zeros(rows * 7)
calendar[first_weekday: first_weekday + days_in_month] = df['overtime_hours'].values
calendar = calendar.reshape(rows, 7)

# 4. 画图
fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(
    calendar,
    annot=np.arange(1, rows*7+1).reshape(rows, 7),  # 写日期
    fmt="d",
    cmap="Reds",
    cbar_kws={'label': '加班小时'},
    linewidths=.5,
    linecolor='gray',
    ax=ax
)

# 把超出 31 的格子设成空白
for r in range(rows):
    for c in range(7):
        day = r * 7 + c - first_weekday + 1
        if day < 1 or day > 31:
            ax.text(c + 0.5, r + 0.5, "", ha='center', va='center')

ax.set_title("2025-08 加班日历热力图")
ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.set_yticklabels([])
plt.tight_layout()
plt.show()