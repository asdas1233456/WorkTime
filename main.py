# main.py
import json, datetime as dt, chinese_calendar as calendar
from pathlib import Path
from jinja2 import Template   # pip install jinja2
from data_io import load_data
from core import calc_ot, ai_allocate
from config import CFG

ROOT = Path(__file__).parent

# ---------- HTML 生成 ----------
def build_html(monthly, ai_rows=""):
    names = list(monthly["person"])
    vals = list(monthly["overtime_after_9"])
    rows = monthly.to_dict(orient="records")
    tpl = Template("""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <title>加班仪表盘</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
  <style>body{padding:2rem;background:#f6f8fa}</style>
</head>
<body>
  <div class="container">
    <h2 class="mb-3">📊 加班统计</h2>
    <div class="row">
      <div class="col-md-6">
        <table class="table table-hover table-sm align-middle">
          <thead class="table-light">
            <tr><th>姓名</th><th>月份</th><th>含早到</th><th>9点后</th></tr>
          </thead>
          <tbody>
            {% for r in rows %}
            <tr>
              <td>{{ r.person }}</td>
              <td>{{ r.date }}</td>
              <td>{{ "%.1f"|format(r.overtime) }}</td>
              <td>{{ "%.1f"|format(r.overtime_after_9) }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="col-md-6">
        <div id="bar" style="height:260px;"></div>
      </div>
    </div>
    {{ ai_table }}
  </div>
  <script>
    var chart = echarts.init(document.getElementById('bar'));
    chart.setOption({
      title:{text:'9点后加班对比',left:'center'},
      tooltip:{},
      xAxis:{type:'category',data:{{ names | tojson }}},
      yAxis:{type:'value'},
      series:[{data:{{ vals | tojson }},type:'bar',itemStyle:{color:'#5470c6'}}]
    });
  </script>
</body>
</html>
    """)
    return tpl.render(rows=rows, names=names, vals=vals, ai_table=ai_rows)

# ---------- 主流程 ----------
def main():
    file_path = Path(__file__).parent / "log.xlsx"
    if not file_path.exists():
        file_path = Path(__file__).parent / "log.csv"
    if not file_path.exists():
        raise FileNotFoundError("请把 log.xlsx 或 log.csv 放到脚本同目录！")

    df = load_data(file_path)
    df[["overtime", "overtime_after_9"]] = df.apply(calc_ot, axis=1, result_type="expand")
    monthly = (df.groupby(["person", df.date.dt.to_period("M")])
                   .agg(overtime=("overtime", "sum"),
                        overtime_after_9=("overtime_after_9", "sum"))
                   .reset_index())

    today = dt.date.today()
    days_left = len([d for d in [today + dt.timedelta(days=i) for i in range(31)]
                     if d.month == today.month and calendar.is_workday(d)])

    ai_rows = ""
    if days_left > 0:
        current = monthly.set_index("person")["overtime_after_9"].to_dict()
        try:
            ai_plan = ai_allocate(current, days_left)
            ai_rows = "".join(
                f"<tr><td>{p}</td><td>{current[p]:.1f}</td><td>{ai[p]['再分配']:.1f}</td>"
                f"<td>{ai[p]['健康提醒']}</td><td>{ai[p]['预计完成日期']}</td></tr>"
                for p, ai in ai_plan.items()
            )
        except Exception as e:
            ai_rows = f"<tr><td colspan='5' class='text-danger'>AI 调用失败：{e}</td></tr>"

    html = build_html(monthly, f"""
    <h3 class="mt-4">AI 再分配 & 健康建议</h3>
    <table class="table table-sm">
      <thead class="table-light">
        <tr><th>姓名</th><th>已加班</th><th>再分配</th><th>健康提醒</th><th>预计完成日期</th></tr>
      </thead>
      <tbody>{ai_rows}</tbody>
    </table>
    """)

    output_path = Path(__file__).parent.resolve() / "report.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 文件已生成 → {output_path}")

if __name__ == "__main__":
    main()