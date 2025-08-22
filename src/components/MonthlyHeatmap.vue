<template>
  <div class="heatmap-container">
    <!-- 星期标题 -->
    <div class="weekdays">
      <div class="weekday">一</div>
      <div class="weekday">二</div>
      <div class="weekday">三</div>
      <div class="weekday">四</div>
      <div class="weekday">五</div>
      <div class="weekday">六</div>
      <div class="weekday">日</div>
    </div>

    <!-- 热力图网格 -->
    <div class="heatmap-grid">
      <!-- 月初前的空白单元格 -->
      <div class="heatmap-cell empty" v-for="i in emptyDays" :key="'empty-' + i"></div>

      <!-- 当月日期单元格 -->
      <div
        class="heatmap-cell"
        v-for="day in monthDays"
        :key="'day-' + day"
        :style="{ backgroundColor: getCellColor(day) }"
        @mouseenter="showTooltip(day)"
        @mouseleave="hideTooltip"
      >
        <span class="day-number">{{ day }}</span>

        <!-- 悬停提示框 -->
        <div class="tooltip" v-if="activeDay === day">
          <div class="tooltip-date">{{ formatDate(day) }}</div>
          <div class="tooltip-hours">{{ getOvertimeHours(day) }} 小时</div>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="heatmap-legend">
      <div class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: '#f7fafc' }"></div>
        <div class="legend-text">0小时</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: '#b8e986' }"></div>
        <div class="legend-text">0-3小时</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: '#7ed321' }"></div>
        <div class="legend-text">3-6小时</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: '#4a90e2' }"></div>
        <div class="legend-text">6-9小时</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: '#2962ff' }"></div>
        <div class="legend-text">9小时以上</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 接收父组件传递的参数
const props = defineProps({
  yearMonth: {
    type: String,
    required: true,
    validator: (value) => {
      // 验证格式为 YYYY-MM
      return /^\d{4}-\d{2}$/.test(value)
    }
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
  // 获取当月的总天数
  const daysInMonth = new Date(year, month, 0).getDate()
  // 生成1到当月天数的数组
  return Array.from({ length: daysInMonth }, (_, i) => i + 1)
})

// 计算月初前的空白天数
const emptyDays = computed(() => {
  // 获取当月第一天是星期几（0是周日，1是周一，...，6是周六）
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay()

  // 转换为以周一为一周的第一天计算空白天数
  // 如果第一天是周日（0），则前面有6个空白；如果是周一（1），则0个空白
  return firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1
})

// 提示框相关状态
const activeDay = ref(null)

const showTooltip = (day) => {
  activeDay.value = day
}

const hideTooltip = () => {
  activeDay.value = null
}

// 获取指定日期的加班小时数
const getOvertimeHours = (day) => {
  // 格式化日期为 YYYY-MM-DD
  const dateStr = `${props.yearMonth}-${String(day).padStart(2, '0')}`
  // 返回对应的加班小时数，默认为0
  return props.data[dateStr] || 0
}

// 获取单元格颜色
const getCellColor = (day) => {
  const hours = getOvertimeHours(day)

  // 根据加班小时数返回不同颜色
  if (hours === 0) return '#f7fafc'
  if (hours <= 3) return '#b8e986'
  if (hours <= 6) return '#7ed321'
  if (hours <= 9) return '#4a90e2'
  return '#2962ff'
}

// 格式化日期显示
const formatDate = (day) => {
  return `${props.yearMonth}-${String(day).padStart(2, '0')}`
}
</script>

<style scoped>
.heatmap-container {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

/* 星期标题样式 */
.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  color: #666;
  padding: 4px 0;
}

/* 热力图网格样式 */
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

/* 单元格样式 */
.heatmap-cell {
  aspect-ratio: 1 / 1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}

.heatmap-cell:hover {
  transform: scale(1.05);
}

.heatmap-cell.empty {
  background-color: #f7fafc;
  cursor: default;
}

.heatmap-cell.empty:hover {
  transform: none;
}

.day-number {
  z-index: 1;
  color: #333;
  font-weight: 500;
}

/* 提示框样式 */
.tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-5px);
  background-color: #333;
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

/* 提示框箭头 */
.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}

.tooltip-date {
  font-weight: bold;
  margin-bottom: 3px;
}

/* 图例样式 */
.heatmap-legend {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
  padding-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 5px;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .heatmap-grid {
    gap: 4px;
  }

  .day-number {
    font-size: 10px;
  }

  .legend-item {
    font-size: 10px;
  }
}
</style>