<template>
  <div class="dashboard">
    <!-- 顶部标题栏 -->
    <header class="dashboard-header">
      <h1>2025年8月加班看板</h1>
      <p>数据更新时间：{{ planData.current_date }} | 来源：{{ planData.来源 }}</p>
    </header>

    <!-- 主要内容区 -->
    <main class="dashboard-content">
      <!-- 左侧边栏：概览和假期 -->
      <aside class="sidebar">
        <!-- 加班概览卡片 -->
        <div class="sidebar-card">
          <h3>加班概览</h3>
          <ul class="overview-list">
            <li>
              <span class="label">当前阶段：</span>
              <span class="value">{{ planData.阶段 }}</span>
            </li>
            <li>
              <span class="label">已加班小时数：</span>
              <span class="value">{{ planData.已加班小时数 }}h</span>
            </li>
            <li>
              <span class="label">剩余需加班：</span>
              <span class="value">{{ planData.剩余需加班 }}h</span>
            </li>
            <li>
              <span class="label">剩余工作日：</span>
              <span class="value">{{ planData.剩余工作日 }}天</span>
            </li>
            <li>
              <span class="label">含周六：</span>
              <span class="value">{{ planData.周六剩余 }}个</span>
            </li>
            <li>
              <span class="label">每日目标：</span>
              <span class="value">{{ planData["每日目标(h)"] }}h</span>
            </li>
          </ul>
        </div>

        <!-- 假期提醒卡片 -->
        <div class="sidebar-card holiday-card">
          <h3>假期提醒</h3>
          <p>{{ planData.this_month_holiday }}</p>
          <p>{{ planData.prev_holiday }}</p>
          <p>{{ planData.next_holiday }}</p>
        </div>
      </aside>

      <!-- 右侧主内容：热力图和记录 -->
      <div class="main-area">
        <!-- 热力图区域 -->
        <div class="card heatmap-card">
          <h2>8月加班热力图</h2>
          <MonthlyHeatmap
            year-month="2025-08"
            :data="heatmapData"
          />
        </div>

        <!-- 统计摘要 -->
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

        <!-- 加班记录列表（带滚动） -->
        <div class="card records-card">
          <h2>加班记录详情</h2>
          <div
            class="records-list"
            :style="{
              maxHeight: shouldShowScroll ? '320px' : 'auto',
              overflowY: shouldShowScroll ? 'auto' : 'visible'
            }"
          >
            <!-- 表头 -->
            <div class="list-header">
              <div class="list-col">日期</div>
              <div class="list-col">类型</div>
              <div class="list-col">时间段</div>
              <div class="list-col">时长</div>
            </div>

            <!-- 记录内容 -->
            <div
              class="list-row"
              v-for="(record, index) in reportData"
              :key="index"
            >
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

        <!-- AI建议区域 -->
        <div class="card advice-card">
          <h2>AI建议</h2>
          <div class="advice-content" v-html="formattedAdvice"></div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MonthlyHeatmap from './components/MonthlyHeatmap.vue'
import planData from '../data/加班计划.json'
import reportData from '../data/overtime_report.json'

// 转换加班记录数据为热力图所需格式
const heatmapData = computed(() => {
  const data = {}
  reportData.forEach(record => {
    const date = record.date.trim()
    data[date] = Number(record.overtime_hours)
  })
  return data
})

// 计算是否需要显示滚动条（记录数 > 5 时）
const shouldShowScroll = computed(() => {
  return Array.isArray(reportData) && reportData.length > 5
})

// 统计数据计算
const maxOvertimeHours = computed(() => {
  if (!Array.isArray(reportData) || reportData.length === 0) return '0'
  return Math.max(...reportData.map(r => r.overtime_hours)).toFixed(2)
})

const averageOvertime = computed(() => {
  if (!Array.isArray(reportData) || reportData.length === 0) return '0'
  const total = reportData.reduce((sum, r) => sum + Number(r.overtime_hours), 0)
  return (total / reportData.length).toFixed(2)
})

// 格式化AI建议
const formattedAdvice = computed(() => {
  return planData.advice
    ? planData.advice.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    : '暂无建议'
})

// 组件挂载时验证数据
onMounted(() => {
  console.log('加班计划数据:', planData)
  console.log('加班记录数据:', reportData)
  console.log('热力图数据:', heatmapData.value)
})
</script>

<style scoped>
/* 全局样式 */
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: #f5f7fa;
  color: #333;
}

/* 头部样式 */
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

/* 主要内容区布局 */
.dashboard-content {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}

/* 侧边栏样式 */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sidebar-card h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #1e293b;
  padding-bottom: 8px;
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

/* 主内容区域 */
.main-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 通用卡片样式 */
.card {
  background: white;
  border-radius: 8px;
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

/* 热力图卡片 */
.heatmap-card {
  padding-bottom: 24px;
}

/* 统计数据容器 */
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
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

/* 记录列表样式 */
.records-list {
  margin-top: 12px;
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
  color: #64748b;
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

/* 响应式调整 */
@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .stats-container {
    grid-template-columns: 1fr 1fr;
  }

  .stats-container .stat-item:nth-child(3) {
    grid-column: 1 / 3;
  }
}

@media (max-width: 640px) {
  .stats-container {
    grid-template-columns: 1fr;
  }

  .stats-container .stat-item:nth-child(3) {
    grid-column: 1;
  }

  .list-header, .list-row {
    grid-template-columns: 80px 70px 1fr 60px;
  }

  .card {
    padding: 16px;
  }
}
</style>