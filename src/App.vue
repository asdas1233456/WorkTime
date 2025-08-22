<template>
  <div class="dashboard">
    <!-- 1. 顶部标题区 -->
    <header class="dashboard-header">
      <h1>2025 年 8 月加班看板</h1>
      <p>数据更新时间：{{ planData.current_date }} | 来源：{{ planData.来源 }}</p>
    </header>

    <!-- 2. 核心内容区（分2块：概览 + 记录） -->
    <main class="dashboard-main">
      <!-- 2.1 左侧：加班概览（用你的「加班计划.json」字段） -->
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

        <!-- 假期信息 -->
        <div class="holiday-info">
          <h3>假期提醒</h3>
          <p>{{ planData.this_month_holiday }}</p>
          <p>{{ planData.prev_holiday }}</p>
          <p>{{ planData.next_holiday }}</p>
        </div>
      </div>

      <!-- 2.2 右侧：加班记录（用你的「overtime_report.json」字段） -->
      <div class="card records-card">
        <h2>加班记录详情</h2>
        <div class="records-table">
          <!-- 表头 -->
          <div class="table-header">
            <div class="table-cell">日期</div>
            <div class="table-cell">类型</div>
            <div class="table-cell">开始时间</div>
            <div class="table-cell">结束时间</div>
            <div class="table-cell">加班时长</div>
          </div>
          <!-- 表体（循环你的记录数据） -->
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
    </main>

    <!-- 3. 底部建议区（用你的 AI 建议） -->
    <footer class="dashboard-footer">
      <div class="advice-card">
        <h2>AI 建议</h2>
        <div class="advice-content" v-html="formattedAdvice"></div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 1. 导入你的两个 JSON 文件（路径必须和结构一致！）
import planData from '../data/加班计划.json' // 你的加班计划
import reportData from '../data/overtime_report.json' // 你的加班记录

// 2. 格式化 AI 建议（处理换行和加粗）
const formattedAdvice = computed(() => {
  // 把 JSON 里的 \n 换成 <br>，**加粗**换成 <strong>
  return planData.advice
    ? planData.advice.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    : '暂无建议'
})

// 3. 调试用：确认数据已加载（打开控制台看）
onMounted(() => {
  console.log('✅ 加班计划数据加载成功：', planData)
  console.log('✅ 加班记录数据加载成功：', reportData)
})
</script>

<style scoped>
/* 基础样式：保证看得清，后续可优化 */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
  background-color: #f5f5f5;
}

/* 顶部标题 */
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

/* 核心内容区：左右分栏 */
.dashboard-main {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  margin-bottom: 20px;
}

/* 卡片通用样式 */
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

/* 左侧概览卡片 */
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

/* 假期信息 */
.holiday-info {
  padding-top: 20px;
  border-top: 1px solid #eee;
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
}

/* 右侧记录表格 */
.records-table {
  width: 100%;
  border-collapse: collapse;
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
}

.table-cell {
  padding: 12px 8px;
  font-size: 14px;
}

/* 工作日/周末标签 */
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

/* 底部建议区 */
.advice-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.advice-card h2 {
  margin: 0 0 15px;
  font-size: 18px;
  color: #333;
}

.advice-content {
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

.advice-content strong {
  color: #333;
}

/* 响应式：小屏幕不分栏 */
@media (max-width: 768px) {
  .dashboard-main {
    grid-template-columns: 1fr;
  }
}
</style>