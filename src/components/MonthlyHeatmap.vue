<template>
  <div class="heatmap">
    <!-- 星期表头 -->
    <div class="heatmap-header">
      <div class="header-item">一</div>
      <div class="header-item">二</div>
      <div class="header-item">三</div>
      <div class="header-item">四</div>
      <div class="header-item">五</div>
      <div class="header-item">六</div>
      <div class="header-item">日</div>
    </div>

    <!-- 热力图网格 -->
    <div class="heatmap-grid">
      <!-- 月初空白占位 -->
      <div class="heatmap-cell empty" v-for="(empty, idx) in emptyDays" :key="`empty-${idx}`"></div>

      <!-- 日期单元格 -->
      <div
        class="heatmap-cell"
        v-for="(day, idx) in monthDays"
        :key="`day-${idx}`"
        :style="{ backgroundColor: getCellColor(day) }"
        @mouseenter="showTooltip(day)"
        @mouseleave="hideTooltip()"
      >
        <span class="day-number">{{ day }}</span>

        <!-- 悬停提示框 -->
        <div class="tooltip" v-if="showTooltipFlag && currentDay === day">
          <p>日期：{{ yearMonth }}-{{ day.toString().padStart(2, '0') }}</p>
          <p>加班时长：{{ getOvertimeHours(day) }}h</p>
        </div>
      </div>
    </div>

    <!-- 图例说明 -->
    <div class="heatmap-legend">
      <div class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: '#f7fafc' }"></span>
        <span class="legend-text">0h</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: '#b8e986' }"></span>
        <span class="legend-text">0-3h</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: '#7ed321' }"></span>
        <span class="legend-text">3-6h</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: '#4a90e2' }"></span>
        <span class="legend-text">6-9h</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: '#2962ff' }"></span>
        <span class="legend-text">9h+</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 接收父组件参数
const props = defineProps({
  yearMonth: {
    type: String,
    required: true,
    validator: (val) => /^\d{4}-\d{2}$/.test(val)
  },
  data: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

// 解析年月
const [year, month] = props.yearMonth.split('-').map(Number)

// 计算当月天数
const monthDays = computed(() => {
  const dayCount = new Date(year, month, 0).getDate()
  return Array.from({ length: dayCount }, (_, i) => i + 1)
})

// 计算月初空白天数
const emptyDays = computed(() => {
  const firstDay = new Date(year, month - 1, 1).getDay()
  return firstDay === 0 ? 6 : firstDay - 1
})

// 提示框控制
const showTooltipFlag = ref(false)
const currentDay = ref(null)

const showTooltip = (day) => {
  showTooltipFlag.value = true
  currentDay.value = day
}

const hideTooltip = () => {
  showTooltipFlag.value = false
  currentDay.value = null
}

// 获取某天的加班小时数
const getOvertimeHours = (day) => {
  const dateKey = `${props.yearMonth}-${day.toString().padStart(2, '0')}`
  return props.data[dateKey] || 0
}

// 根据小时数获取单元格颜色
const getCellColor = (day) => {
  const hours = getOvertimeHours(day)
  if (hours === 0) return '#f7fafc'
  if (hours <= 3) return '#b8e986'
  if (hours <= 6) return '#7ed321'
  if (hours <= 9) return '#4a90e2'
  return '#2962ff'
}
</script>

<style scoped>
.heatmap {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

/* 星期表头 */
.heatmap-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}

.header-item {
  text-align: center;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  padding: 4px 0;
}

/* 热力图网格 */
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

/* 单元格样式 */
.heatmap-cell {
  aspect-ratio: 1/1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #333;
  position: relative;
  cursor: pointer;
  border: 1px solid #eee;
}

.heatmap-cell.empty {
  background-color: #f7fafc;
  cursor: default;
}

.day-number {
  z-index: 1;
}

/* 悬停提示框 */
.tooltip {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
  z-index: 10;
  min-width: 120px;
  text-align: center;
}

.tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px 6px 0;
  border-style: solid;
  border-color: #333 transparent transparent;
}

/* 图例 */
.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  margin-right: 6px;
  border: 1px solid #eee;
}

/* 响应式调整 */
@media (max-width: 640px) {
  .heatmap-legend {
    gap: 10px;
  }

  .legend-item {
    font-size: 11px;
  }
}
</style>