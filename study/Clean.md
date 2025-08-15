## 数据清理层技术要点

| 技术点 | 代码片段 | 注意坑 |
|---|---|---|
| 统一读取 | `pd.read_excel(path, dtype=str)` / `chardet.detect` | CSV 需先探测编码 |
| 日期清洗 | `pd.to_datetime(x, errors="coerce").normalize()` | 去掉 `origin` 避免二次解析 |
| 时间清洗 | `pd.to_datetime(x).strftime("%H:%M")` | 字符串格式更直观 |
| 空值过滤 | `df.dropna(subset=["date"])` | 先写日志再 drop，行号对应 |
| 排序键 | `pd.to_datetime(time_str, format="%H:%M")` | 临时列，用完即删 |
| 异常兜底 | `try/except` → `traceback.format_exc()` 写入日志 | 业务层可用空 DataFrame |