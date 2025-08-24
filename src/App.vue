<template>
  <div class="dashboard">
    <!-- 顶部标题栏 -->
    <header class="dashboard-header">
      <h1>{{ currentMonth.slice(5) }}月加班看板</h1>
      <p>数据更新时间：{{ planData.current_date }} | 来源：{{ planData.来源 }}</p>
    </header>

    <!-- 核心三栏布局（无改动） -->
    <main class="dashboard-content">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-card">
          <h3>加班概览</h3>
          <ul class="overview-list">
            <li><span class="label">当前阶段：</span><span class="value">{{ planData.阶段 }}</span></li>
            <li><span class="label">已加班小时数：</span><span class="value">{{ planData.已加班小时数 }}h</span></li>
            <li><span class="label">剩余需加班：</span><span class="value">{{ planData.剩余需加班 }}h</span></li>
            <li><span class="label">剩余工作日：</span><span class="value">{{ planData.剩余工作日 }}天</span></li>
            <li><span class="label">含周六：</span><span class="value">{{ planData.周六剩余 }}天</span></li>
            <li><span class="label">工作日每日目标：</span><span class="value">{{ planData["工作日每日目标(h)"] }}h</span></li>
          </ul>
        </div>

        <div class="sidebar-card holiday-card">
          <h3>假期提醒</h3>
          <p>{{ planData.this_month_holiday }}</p>
          <p>{{ planData.prev_holiday }}</p>
          <p>{{ planData.next_holiday }}</p>
        </div>
      </aside>

      <!-- 中间区域 -->
      <div class="middle-area">
        <div class="stats-container">
          <div class="stat-item">
            <span class="stat-label">总记录数</span>
            <span class="stat-value">{{ reportData.length }}条</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最长加班</span>
            <span class="stat-value">{{ maxOvertimeHours }}h</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均时长</span>
            <span class="stat-value">{{ averageOvertime }}h</span>
          </div>
        </div>

        <div class="card records-card">
          <h2>{{ currentMonth.slice(5) }}月加班记录详情</h2>
          <div class="records-list"
               :style="{ maxHeight: reportData.length > 5 ? '320px' : 'auto',
                         overflowY: reportData.length > 5 ? 'auto' : 'visible' }">
            <div class="list-header">
              <div class="list-col">日期</div>
              <div class="list-col">类型</div>
              <div class="list-col">时间段</div>
              <div class="list-col">时长</div>
            </div>
            <div class="list-row" v-for="(record, index) in currentMonthRecords" :key="index">
              <div class="list-col">{{ record.date }}</div>
              <div class="list-col">
                <span :class="record.is_workday ? 'tag workday' : 'tag weekend'">
                  {{ record.is_workday ? '工作日' : '周末' }}
                </span>
              </div>
              <div class="list-col">{{ record.actual_start }} - {{ record.actual_end }}</div>
              <div class="list-col">{{ record.overtime_hours }}h</div>
            </div>
          </div>
        </div>

        <div class="card advice-card">
          <h2>AI建议</h2>
          <div class="advice-content" v-html="formattedAdvice"></div>
        </div>
      </div>

      <!-- 右侧热力图 -->
      <div class="right-area">
        <div class="card heatmap-card">
          <h2>{{ currentMonth.slice(5) }}月加班热力图</h2>

<!--          &lt;!&ndash; 月份选择器 &ndash;&gt;-->
<!--          <select v-model="currentMonth" style="margin-bottom:8px;">-->
<!--            <option v-for="m in 12" :key="m"-->
<!--                    :value="`2025-${m.toString().padStart(2,'0')}`">-->
<!--              2025-{{ m.toString().padStart(2,'0') }}-->
<!--            </option>-->
<!--          </select>-->

          <MonthlyHeatmap
            :year-month="currentMonth"
            :data="heatmapData"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MonthlyHeatmap from './components/MonthlyHeatmap.vue'
import planData from '../data/加班计划.json'
import reportData from '../data/overtime_report.json'

// 当前月份（动态）
const currentMonth = ref('2025-08')

// 当月记录过滤
const currentMonthRecords = computed(() =>
  reportData.filter(r => r.date.startsWith(currentMonth.value))
)

// 热力图数据
const heatmapData = computed(() => {
  const data = {}
  currentMonthRecords.value.forEach(r => {
    data[r.date] = Number(r.overtime_hours)
  })
  return data
})

// 统计值仅针对当前月
const maxOvertimeHours = computed(() => {
  if (!currentMonthRecords.value.length) return '0.00'
  return Math.max(...currentMonthRecords.value.map(r => Number(r.overtime_hours))).toFixed(2)
})
const averageOvertime = computed(() => {
  if (!currentMonthRecords.value.length) return '0.00'
  const total = currentMonthRecords.value.reduce((s, r) => s + Number(r.overtime_hours), 0)
  return (total / currentMonthRecords.value.length).toFixed(2)
})

// AI 建议
const formattedAdvice = computed(() =>
  planData.advice
    ? planData.advice.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    : '暂无加班建议，可根据剩余工作日合理安排时长~'
)
</script>


<style scoped>
/* 全局基础样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.dashboard {
  max-width: 1600px;
  margin: 0 auto;
  padding: 16px;
  font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: #f5f7fa;
  color: #333;
}

/* 加班记录 */
.records-card {
  height: 437px;          /* 固定高度 */
  /* 或 max-height: 480px; 让内容少时自动收缩 */
  display: flex;
  flex-direction: column;
}


/* 顶部标题栏 */
.dashboard-header {
  background: white;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.dashboard-header h1 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #1a1a2e;
}

.dashboard-header p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

/* 核心三栏布局 */
.dashboard-content {
  display: grid;
  grid-template-columns: 280px 1fr 1fr; /* 左280px固定，中右自适应 */
  gap: 20px;
  align-items: stretch;
}

/* 左侧边栏 */
.sidebar,
.middle-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;            /* 占满网格单元高度 */
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sidebar-card h3 {
  margin: 0 0 16px;
  font-size: 18px; /* 增大字号 */
  text-align: center; /* 居中对齐 */
  color: #1e293b;
  padding-bottom: 10px;
  border-bottom: 1px solid #f1f5f9;
}

.overview-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.overview-list li {
  padding: 8px 0;
  border-bottom: 1px dashed #f1f5f9;
  display: flex;
  flex-wrap: wrap;
}

.overview-list li:last-child {
  border-bottom: none;
}

.label {
  flex: 0 0 100px;
  color: #64748b;
  font-size: 14px;
}

.value {
  flex: 1;
  font-size: 14px;
  color: #1e293b;
}

.holiday-card p {
  margin: 8px 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

/* 中间区域 */
.middle-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 统计容器 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

/* 通用卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  text-align: center; /* 居中对齐 */
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card h2 {
  margin: 0 0 16px;
  font-size: 18px;
  color: #1e293b;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

/* 加班记录列表 */
.records-list {
  scrollbar-width: thin;
  scrollbar-color: #ddd #f5f5f5;
}

.records-list::-webkit-scrollbar {
  width: 6px;
}

.records-list::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.records-list::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

.list-header {
  display: grid;
  grid-template-columns: 120px 80px 1fr 80px;
  font-weight: 600;
  color: #6b7280;
  padding: 12px 8px;
  background-color: #f8fafc;
  border-radius: 4px 4px 0 0;
  font-size: 14px;
}

.list-row {
  display: grid;
  grid-template-columns: 120px 80px 1fr 80px;
  padding: 12px 8px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
  transition: background-color 0.2s;
}

.list-row:hover {
  background-color: #f8fafc;
}

.list-col {
  word-break: keep-all;
  align-self: center;
}

/* 标签样式 */
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.workday {
  background-color: #3b82f6;
}

.weekend {
  background-color: #f97316;
}

/* AI建议区域 */
.advice-content {
  margin-top: 12px;
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
}

.advice-content strong {
  color: #1e293b;
}

/* 右侧热力图区域 */
.right-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 320px; /* 防止热力图压缩 */
}

.heatmap-card {
  padding-bottom: 24px;
}

/* 响应式适配（原逻辑不变） */
@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 280px 1fr;
    grid-template-areas:
      "sidebar right"
      "sidebar middle";
  }
  .sidebar { grid-area: sidebar; }
  .right-area { grid-area: right; }
  .middle-area { grid-area: middle; }
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    grid-template-areas:
      "sidebar"
      "right"
      "middle";
  }
  .right-area { min-width: auto; }
  .stats-container {
    grid-template-columns: 1fr 1fr;
  }
  .stats-container .stat-item:nth-child(3) {
    grid-column: 1 / 3;
  }
  .list-header, .list-row {
    grid-template-columns: 80px 70px 1fr 60px;
  }
}

@media (max-width: 640px) {
  .stats-container {
    grid-template-columns: 1fr;
  }
  .stats-container .stat-item:nth-child(3) {
    grid-column: 1;
  }
  .card {
    padding: 16px;
  }
}
</style>