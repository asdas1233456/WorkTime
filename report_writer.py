import os, pandas as pd

def write_logs(df, flag_df, path="log/异常汇总.txt"):
    os.makedirs("log", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for title, mask in [("缺勤", flag_df["absence"]),
                            ("迟到", flag_df["late"]),
                            ("早退", flag_df["early"])]:
            sub = df[mask]
            if sub.empty: continue
            f.write(f"\n{title}\n")
            for _, r in sub.iterrows():
                f.write(f"{r['date'].strftime('%Y-%m-%d')} "
                        f"{r['actual_start']}-{r['actual_end']}  {title}\n")

def write_excel(df, path="overtime_report.xlsx"):
    df.to_excel(path, index=False)