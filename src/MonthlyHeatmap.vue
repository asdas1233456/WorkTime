<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  yearMonth: { type: String, required: true },
  data:      { type: Object, default: () => ({}) }
})

const weekHead = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const cells = computed(() => {
  const start = dayjs(props.yearMonth)
  const days  = start.daysInMonth()
  const first = (start.day() + 6) % 7   // 把周日 0→6，周一 0
  const arr   = []

  for (let i = 0; i < first; i++) arr.push(null)          // 空白占位
  for (let d = 1; d <= days; d++) {
    const date = start.date(d).format('YYYY-MM-DD')
    arr.push({ date, day: d, value: props.data[date] ?? 0 })
  }
  return arr
})

const level = v => {
  if (v === 0) return 0
  if (v <= 1)  return 1
  if (v <= 3)  return 2
  if (v <= 6)  return 3
  return 4
}
const colors = ['#f4f5f7', '#dff0d8', '#a3d3a4', '#5cb85c', '#2e7d32']
</script>

<template>
  <div class="wrapper">
    <!-- 星期栏 -->
    <div class="week-header">
      <span v-for="w in weekHead" :key="w">{{ w }}</span>
    </div>

    <!-- 日历格子 -->
    <div class="month-grid">
      <div
        v-for="(cell, idx) in cells"
        :key="idx"
        :class="['cell', { blank: !cell }]"
        :style="cell && { backgroundColor: colors[level(cell.value)] }"
      >
        <template v-if="cell">
          <span class="day-text">{{ cell.day }}</span>
          <!-- 即时 tooltip -->
          <span class="tooltip">
            {{ cell.date }} 加班 {{ cell.value }} 小时
          </span>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 整体居中 */
.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
}

/* 星期栏 */
.week-header {
  display: grid;
  grid-template-columns: repeat(7, 40px);
  gap: 4px;
  font-size: 12px;
  color: #586069;
  font-weight: 600;
  text-align: center;
}

/* 日历网格 */
.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 40px);
  gap: 4px;
}

.cell {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  position: relative;
  transition: transform 0.15s;
}
.cell:hover:not(.blank) {
  transform: scale(1.05);
}

/* 数字颜色深浅自适应 */
.day-text {
  color: #24292e;
  font-weight: 500;
}

/* 即时 tooltip */
.tooltip {
  position: absolute;
  top: -34px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  color: #333;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
  z-index: 9;
}
.cell:hover .tooltip {
  opacity: 1;
}

/* 空白格子：完全无边框、无阴影 */
.blank {
  background: transparent;
  border: none;
  box-shadow: none;
  pointer-events: none;
}
</style>