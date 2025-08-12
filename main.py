from pathlib import Path

from jinja2 import Template  # pip install jinja2

from core import calc_ot, current_stage, ai_stage_advice, remaining_workdays_of_month
from data_io import load_data

ROOT = Path(__file__).parent

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
          <thead class="table-light"><tr><th>姓名</th><th>月份</th><th>9点前</th><th>9点后</th></tr></thead>
          <tbody>{% for r in rows %}<tr><td>{{ r.person }}</td><td>{{ r.date }}</td><td>{{ "%.1f"|format(r.overtime) }}</td><td>{{ "%.1f"|format(r.overtime_after_9) }}</td></tr>{% endfor %}</tbody>
        </table>
      </div>
      <div class="col-md-6"><div id="bar" style="height:260px;"></div></div>
    </div>
    {{ ai_table }}
  </div>
  <script>
    var chart = echarts.init(document.getElementById('bar'));
    chart.setOption({title:{text:'9点后加班对比',left:'center'},tooltip:{},xAxis:{type:'category',data:{{ names | tojson }}},yAxis:{type:'value'},series:[{data:{{ vals | tojson }},type:'bar',itemStyle:{color:'#5470c6'}}]});
  </script>
</body>
</html>
    """)
    return tpl.render(rows=rows, names=names, vals=vals, ai_table=ai_rows)

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

    stage = current_stage()
    days_left = remaining_workdays_of_month()

    # 1. 拼 AI 建议的 html
    ai_rows = ""
    if days_left:
        current = monthly.set_index("person")["overtime_after_9"].to_dict()
        try:
            advice = ai_stage_advice(current, stage, days_left)
            # 保证每个人都要有数据，缺失补 0
            for p in current:
                advice.setdefault(p, {"再分配": 0.0, "建议": "-"})
            # 按姓名排序，生成表格行
            ai_rows = "".join(
                f"<tr><td>{p}</td><td>{current[p]:.1f}</td>"
                f"<td>{advice[p]['再分配']:.1f}</td>"
                f"<td>{advice[p]['建议']}</td></tr>"
                for p in sorted(current)
            )
        except Exception as e:
            ai_rows = (
                "<tr><td colspan='4' class='table-warning text-center'>"
                f"<small class='text-danger'>AI 调用失败：{e}</small>"
                "</td></tr>"
            )
    else:
        ai_rows = (
            "<tr><td colspan='4' class='text-center text-muted'>"
            "本月已无剩余工作日，无需 AI 建议"
            "</td></tr>"
        )

    # 2. 整个 html 模板
    html = build_html(
        monthly,
        f"""
        <h4>当前阶段：{stage} &nbsp;&nbsp; 剩余工作日：{len(days_left)} 天</h4>
        <table class="table table-sm table-bordered">
          <thead class="table-light">
            <tr>
              <th>姓名</th>
              <th>已加班</th>
              <th>再分配</th>
              <th>建议</th>
            </tr>
          </thead>
          <tbody>
            {ai_rows}
          </tbody>
        </table>
        """
    )

    (Path(__file__).parent / "report.html").write_text(html, encoding="utf-8")
    print(f"[OK] 文件已生成 → {Path(__file__).parent / 'report.html'}")

if __name__ == "__main__":
    main()