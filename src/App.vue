<template>
  <div class="dashboard">
    <!-- 顶部标题区 -->
    <header class="dashboard-header">
      <h1>2025 年 8 月加班看板</h1>
      <p>数据更新时间：{{ planData.current_date }} | 来源：{{ planData.来源 }}</p>
    </header>

    <!-- 核心内容区 -->
    <main class="dashboard-main">
      <!-- 左侧：加班概览和热力图 -->
      <div class="card overview-card">
        <h2>加班概览</h2>
        <div class="overview-list">
          <div class="overview-item">
            <span class="label">当前阶段：</span>
            <span class="value">{{ planData.阶段 }}</span>
          </div>
          <div class="overview-item">
            <span class="label">已加班小时数：</span>
            <span class="value">{{ planData.已加班小时数 }}h</span>
          </div>
          <div class="overview-item">
            <span class="label">剩余需加班：</span>
            <span class="value">{{ planData.剩余需加班 }}h</span>
          </div>
          <div class="overview-item">
            <span class="label">剩余工作日：</span>
            <span class="value">{{ planData.剩余工作日 }}天（含{{ planData.周六剩余 }}个周六）</span>
          </div>
          <div class="overview-item">
            <span class="label">每日目标：</span>
            <span class="value">{{ planData["每日目标(h)"] }}h</span>
          </div>
        </div>

        <!-- 热力图区域 -->
        <div class="heatmap-section">
          <h3>8月加班热力图</h3>
          <MonthlyHeatmap
            year-month="2025-08"
            :data="heatmapData"
          />
        </div>

        <!-- 假期信息 -->
        <div class="holiday-info">
          <h3>假期提醒</h3>
          <p>{{ planData.this_month_holiday }}</p>
          <p>{{ planData.prev_holiday }}</p>
          <p>{{ planData.next_holiday }}</p>
        </div>
      </div>

      <!-- 右侧：加班记录和AI建议 -->
      <div class="right-column">
        <!-- 加班记录 -->
        <div class="card records-card">
          <h2>加班记录详情</h2>
          <div class="records-table">
            <div class="table-header">
              <div class="table-cell">日期</div>
              <div class="table-cell">类型</div>
              <div class="table-cell">开始时间</div>
              <div class="table-cell">结束时间</div>
              <div class="table-cell">加班时长</div>
            </div>
            <div
              class="table-row"
              v-for="(record, index) in reportData"
              :key="index"
            >
              <div class="table-cell">{{ record.date }}</div>
              <div class="table-cell">
                <span :class="record.is_workday ? 'workday-tag' : 'weekend-tag'">
                  {{ record.is_workday ? '工作日' : '周末' }}
                </span>
              </div>
              <div class="table-cell">{{ record.actual_start }}</div>
              <div class="table-cell">{{ record.actual_end }}</div>
              <div class="table-cell">{{ record.overtime_hours }}h</div>
            </div>
          </div>
        </div>

        <!-- AI建议 -->
        <div class="card advice-card">
          <h2>AI 建议</h2>
          <div class="advice-content" v-html="formattedAdvice"></div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="dashboard-footer">
      <p>© 2025 加班管理看板 | 数据仅供参考</p>
    </footer>
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
    // 确保日期格式正确
    const date = record.date.trim()
    // 确保加班小时数为数字类型
    data[date] = Number(record.overtime_hours)
  })
  return data
})

// 格式化AI建议内容
const formattedAdvice = computed(() => {
  if (!planData.advice) return '暂无建议'

  // 处理换行和加粗格式
  return planData.advice
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
})

// 调试信息
onMounted(() => {
  console.log('加班计划数据:', planData)
  console.log('加班记录数据:', reportData)
  console.log('热力图数据:', heatmapData.value)
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
  min-height: 100vh;
  box-sizing: border-box;
}

.dashboard-header {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.dashboard-header h1 {
  margin: 0 0 10px;
  color: #333;
}

.dashboard-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.dashboard-main {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  margin-bottom: 20px;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card h2 {
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  color: #333;
  font-size: 18px;
}

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.overview-item {
  display: flex;
  flex-wrap: wrap;
}

.overview-item .label {
  flex: 0 0 120px;
  color: #666;
  font-weight: 500;
}

.overview-item .value {
  flex: 1;
  color: #333;
}

.heatmap-section {
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin: 20px 0;
}

.heatmap-section h3 {
  margin: 0 0 15px;
  font-size: 16px;
  color: #333;
  text-align: center;
}

.holiday-info {
  padding-top: 20px;
}

.holiday-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #333;
}

.holiday-info p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 120px 80px 100px 100px 100px;
  background-color: #f8f8f8;
  font-weight: 500;
  color: #666;
}

.table-row {
  display: grid;
  grid-template-columns: 120px 80px 100px 100px 100px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f9f9f9;
}

.table-cell {
  padding: 12px 8px;
  font-size: 14px;
}

.workday-tag {
  display: inline-block;
  padding: 3px 8px;
  background-color: #e6f7ff;
  color: #1890ff;
  border-radius: 12px;
  font-size: 12px;
}

.weekend-tag {
  display: inline-block;
  padding: 3px 8px;
  background-color: #fff2e8;
  color: #fa8c16;
  border-radius: 12px;
  font-size: 12px;
}

.advice-content {
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

.advice-content strong {
  color: #333;
}

.dashboard-footer {
  text-align: center;
  padding: 15px;
  color: #666;
  font-size: 13px;
  border-top: 1px solid #eee;
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-main {
    grid-template-columns: 1fr;
  }

  .table-header, .table-row {
    grid-template-columns: repeat(5, 1fr);
  }

  .table-cell {
    font-size: 12px;
    padding: 8px 4px;
  }
}
</style>