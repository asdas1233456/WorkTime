<template>
  <h2 style="text-align:center;margin-top:40px;">2025 年 8 月加班热力图</h2>
  <MonthlyHeatmap year-month="2025-08" :data="values" />
</template>
<script setup>
import rawData from '/data/overtime_report.json'
import MonthlyHeatmap from './MonthlyHeatmap.vue'

/* 调试：把数据转成对象再打印 */
const values = rawData.reduce((o, cur) => {
  const key = cur.date.trim()        // 去掉首尾空格
  o[key] = cur.overtime_hours
  return o
}, {})

/* 浏览器控制台查看 key 是否正确 */
console.table(values)
</script>
