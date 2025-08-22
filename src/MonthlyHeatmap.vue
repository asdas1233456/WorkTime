<template>
  <div class="heatmap">
    <!-- 星期标题 -->
    <div class="weekdays flex mb-1">
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">一</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">二</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">三</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">四</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">五</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">六</div>
      <div class="weekday text-center text-xs text-gray-500 w-8 h-8 flex items-center justify-center">日</div>
    </div>

    <!-- 热力图网格 -->
    <div class="grid grid-cols-7 gap-1">
      <div
        v-for="(cell, index) in cells"
        :key="index"
        :class="['cell', { 'empty': !cell }]"
        :style="cell ? {
          backgroundColor: getColor(cell.value),
          cursor: 'pointer'
        } : { backgroundColor: '#f9fafb' }"
        @mouseover="handleMouseOver(cell)"
        @mouseleave="handleMouseLeave"
      >
        <div v-if="cell" class="text-xs p-1 text-gray-700">
          {{ cell.day }}
        </div>
      </div>
    </div>

    <!-- 悬停提示 -->
    <div
      v-if="tooltipData"
      class="tooltip absolute bg-gray-800 text-white text-xs p-2 rounded shadow-lg z-10"
      :style="{
        left: tooltipX + 'px',
        top: tooltipY + 'px'
      }"
    >
      <div>{{ tooltipData.date }}</div>
      <div>加班时长: {{ tooltipData.value }}小时</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import dayjs from 'dayjs'

const props = {
  yearMonth: {
    type: String,
    required: true,
    validator: (value) => {
      return /^\d{4}-\d{2}$/.test(value)
    }
  },
  data: {
    type: Object,
    default: () => ({})
  }
}

// 颜色配置
const colors = [
  '#f4f5f7', // 0小时
  '#dff0d8', // 1小时以内
  '#a3d3a4', // 1-3小时
  '#5cb85c', // 3-6小时
  '#2e7d32'  // 6小时以上
]

// 生成日历单元格数据
const cells = computed(() => {
  const [year, month] = props.yearMonth.split('-').map(Number)
  const start = dayjs(`${year}-${month}-01`)
  const daysInMonth = start.daysInMonth()

  // 计算当月第一天是星期几 (1-7, 1=周一, 7=周日)
  const firstDayOfWeek = (start.day() || 7)  // day()返回0-6, 0是周日, 转换为1-7

  // 生成月初的空白格子
  const cells = []
  for (let i = 1; i < firstDayOfWeek; i++) {
    cells.push(null)
  }

  // 生成当月的日期格子
  for (let day = 1; day <= daysInMonth; day++) {
    const date = start.date(day).format('YYYY-MM-DD')
    const value = props.data[date] || 0

    cells.push({
      day,
      date,
      value
    })
  }

  return cells
})

// 根据值获取颜色
const getColor = (value) => {
  if (value === 0) return colors[0]
  if (value < 1) return colors[1]
  if (value < 3) return colors[2]
  if (value < 6) return colors[3]
  return colors[4]
}

// 悬停提示功能
const tooltipData = ref(null)
const tooltipX = ref(0)
const tooltipY = ref(0)

const handleMouseOver = (cell, e) => {
  if (!cell) return

  tooltipData.value = cell

  // 计算提示框位置
  if (e) {
    tooltipX.value = e.pageX + 10
    tooltipY.value = e.pageY + 10
  }
}

const handleMouseLeave = () => {
  tooltipData.value = null
}
</script>

<style scoped>
.heatmap {
  position: relative;
  display: inline-block;
}

.cell {
  width: 28px;
  height: 28px;
  border-radius: 3px;
  transition: transform 0.2s;
}

.cell:hover {
  transform: scale(1.1);
}

.empty {
  width: 28px;
  height: 28px;
}

.tooltip {
  pointer-events: none;
  white-space: nowrap;
}
</style>
