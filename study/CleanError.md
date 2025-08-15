# 📚 打卡数据清洗「问题发生 → 逐步解决」知识库  

---

## 🧭 时间线 & 逐步复盘

| 时间 | 现象/报错 | 关键动作 | 根因定位 | 修复方案 |
|---|---|---|---|---|
| **T0** | 运行后拿到 `Empty DataFrame` | 打印 `len(df)` 发现 0 行 | 数据在某一步被全部过滤 | 在 `clean()` 插入 4 个 `print("【步骤】行数:", len(df))` |
| **T1** | 【去日期空值后】行数 = 0 | 打印 `df_raw.columns` 与 `df_raw.iloc[0]` | 列名正确，但整列日期为 `NaT` | 发现 `_normalize_date` 二次 `to_datetime` + 错误 `origin` |
| **T2** | `_normalize_date` 返回全 `NaT` | 打印 `df_raw[date_col].head()` | 源数据已是 `"2025-08-01 00:00:00"` 字符串 | 去掉 `origin`，只 `.normalize()` |
| **T3** | 时间列出现 `1900-01-01 20:42:00` | 查看 `_normalize_time` 返回类型 | `pd.to_datetime` 自动补日期 1900-01-01 | 改为返回 `"HH:MM"` 字符串 |
| **T4** | 排序/去重逻辑失效 | 检查 `df["end_ord"]` 类型 | 字符串无法直接排序 | 排序前临时 `pd.to_datetime(time_str, format="%H:%M")` |
| **T5** | 担心异常中断 | 询问 | 未加异常捕获 | 外层包 `safe_clean()`，写 `log/clean_error.log` |

---

## 🔁 标准化排查 5 步法（30 秒定位）

1. **读文件**  
   ```python
   df_raw = pd.read_excel(file, dtype=str)
   print("原始行数:", len(df_raw))
   print("列名:", list(df_raw.columns))
看首行
Python
复制
print("首行原始值：", df_raw.iloc[0].to_dict())
看脏值
Python
复制
print("日期列前5行：\n", df_raw["日期"].head())
看类型
Python
复制
print("清洗后 dtypes：\n", df.dtypes)
看空值
Python
复制
print("空值统计：\n", df.isna().sum())
🛠️ 可复用最小函数库
Python
复制
# 1. 通用读取
```def load_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path, dtype=str)
    enc = chardet.detect(open(path, "rb").read(100_000))["encoding"] or "utf-8"
    return pd.read_csv(path, dtype=str, encoding=enc)
```

# 2. 日期清洗（保留日期 00:00:00）
```def norm_date(x):
    return pd.to_datetime(x, errors="coerce").normalize()
```
# 3. 时间清洗（HH:MM 字符串）
```def norm_time(x):
    ts = pd.to_datetime(x, errors="coerce")
    return ts.strftime("%H:%M") if pd.notna(ts) else None
```
# 4. 排序去重（时间列是字符串时）
```def dedup_day_latest(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["end_ord"]  = pd.to_datetime(df["actual_end"],   format="%H:%M")
    df["start_ord"] = pd.to_datetime(df["actual_start"], format="%H:%M")
    return (df.sort_values(["date", "end_ord", "start_ord"])
              .drop_duplicates(subset=["date"], keep="last")
              .drop(columns=["end_ord", "start_ord"]))
```
✅ 上线前 10 秒 Checklist
[ ] 打印 len(df_raw) 与列名  

[ ] 打印首行原始值确认列名  

[ ] 日期列 → datetime64[ns]  

[ ] 时间列 → "HH:MM" 字符串  

[ ] 排序/去重前用 format="%H:%M" 转临时 datetime64  

[ ] 空值日志文件正常生成

[ ] 外层 safe_clean() 捕获异常

📌 一句话口诀
“先数行，再看列，三看脏值，四看类型，五看空值，30 秒定位 99% 问题。”