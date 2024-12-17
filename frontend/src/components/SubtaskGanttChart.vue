<template>
  <div class="subtask-gantt">
    <div class="subtask-header">
      <h3>{{ parentTask.Task }} - Subtasks</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    <div class="chart-container">
      <div ref="chartContainer" class="gantt-chart"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import type { Task } from '../types'

const props = defineProps<{
  parentTask: Task
}>()

defineEmits<{
  (e: 'close'): void
}>()

const chartContainer = ref<HTMLElement | null>(null)

const getNextMonday = (date: Date): Date => {
  const result = new Date(date)
  const day = result.getDay()
  if (day === 0) { // Sunday
    result.setDate(result.getDate() + 1)
  } else if (day > 1) { // Tuesday-Saturday
    result.setDate(result.getDate() + (8 - day))
  }
  // If it's already Monday (day === 1), no change needed
  return result
}

const getPreviousMonday = (date: Date): Date => {
  const result = new Date(date)
  const day = result.getDay()
  if (day === 0) { // Sunday
    result.setDate(result.getDate() - 6)
  } else if (day > 1) { // Tuesday-Saturday
    result.setDate(result.getDate() - (day - 1))
  }
  // If it's already Monday (day === 1), no change needed
  return result
}

const generateTicks = (start: Date, end: Date): Date[] => {
  const ticks: Date[] = []
  const current = new Date(getPreviousMonday(start))
  
  while (current <= end) {
    ticks.push(new Date(current))
    current.setDate(current.getDate() + 7) // Add one week
  }
  return ticks
}

const calculateTextWidth = (text: string, fontSize: number = 14.4): number => {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  if (!context) return 0
  
  context.font = `${fontSize}px Arial`
  return context.measureText(text).width
}

const calculateLeftMargin = (tasks: Task[]): number => {
  if (!tasks.length) return 150
  
  const longestTask = tasks.reduce((longest, task) => 
    task.Task.length > longest.length ? task.Task : longest
  , tasks[0].Task)
  
  // Increase the padding significantly to ensure long text is visible
  const textWidth = calculateTextWidth(longestTask, 14.4)
  return Math.max(Math.ceil(textWidth) + 100, 200) // Increased minimum margin and padding
}

const drawChart = () => {
  if (!chartContainer.value || !props.parentTask.subtasks.length) return

  // Clear previous chart
  d3.select(chartContainer.value).selectAll('*').remove()

  const tasks = props.parentTask.subtasks
  const leftMargin = calculateLeftMargin(tasks)
  
  const margin = { 
    top: 60, 
    right: 40, 
    bottom: 20, 
    left: leftMargin 
  }
  
  // Use parent task dates as boundaries
  const startDate = getPreviousMonday(new Date(props.parentTask.Start_date))
  const endDate = getNextMonday(new Date(props.parentTask.End_Date))
  
  const weekInMillis = 7 * 24 * 60 * 60 * 1000
  const totalWeeks = Math.ceil((endDate.getTime() - startDate.getTime()) / weekInMillis)
  const minWidthPerWeek = 80
  const totalWidth = totalWeeks * minWidthPerWeek
  
  const minHeightPerTask = 40
  const height = Math.max(tasks.length * minHeightPerTask, 120)

  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', totalWidth + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)

  // Create a background rect for the chart area
  const chartGroup = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Add white background to chart area
  chartGroup.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', totalWidth)
    .attr('height', height)
    .attr('fill', 'white')

  const timeScale = d3.scaleTime()
    .domain([startDate, endDate])
    .range([0, totalWidth])

  const taskScale = d3.scaleBand()
    .domain(tasks.map(d => d.Task))
    .range([0, height])
    .padding(0.2)

  const ticks = generateTicks(startDate, endDate)

  // Draw grid lines first (behind the axes and tasks)
  chartGroup.append('g')
    .attr('class', 'grid')
    .selectAll('line')
    .data(ticks)
    .enter()
    .append('line')
    .attr('x1', d => timeScale(d))
    .attr('x2', d => timeScale(d))
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', '#E0E0E0')
    .attr('stroke-width', 1)
    .attr('stroke-dasharray', '2,2')

  const xAxis = d3.axisTop(timeScale)
    .tickValues(ticks)
    .tickFormat(d3.timeFormat("%b %d") as (date: Date | d3.NumberValue, i: number) => string)

  const yAxis = d3.axisLeft(taskScale)
    .ticks(tasks.length)

  // Add axes after grid lines
  const xAxisGroup = chartGroup.append('g')
    .attr('class', 'x-axis')
    .call(xAxis)

  xAxisGroup.selectAll('text')
    .style('text-anchor', 'start')
    .attr('dx', '0.8em')
    .attr('dy', '-0.5em')
    .attr('transform', 'rotate(-45)')

  chartGroup.append('g')
    .attr('class', 'y-axis')
    .call(yAxis)

  // Use a different color scheme for subtasks
  const subtaskColors = {
    bar: '#FF9800',
    progress: '#F57C00'
  }

  // Draw task bars
  tasks.forEach((task: Task) => {
    const barGroup = chartGroup.append('g')
      .attr('class', 'task-group')

    // Main task bar
    barGroup.append('rect')
      .attr('class', 'task-bar')
      .attr('x', timeScale(new Date(task.Start_date)))
      .attr('y', taskScale(task.Task)!)
      .attr('width', timeScale(new Date(task.End_Date)) - timeScale(new Date(task.Start_date)))
      .attr('height', taskScale.bandwidth())
      .attr('fill', subtaskColors.bar)
      .attr('rx', 3)
      .attr('ry', 3)
      .style('opacity', 0.9)

    // Progress bar
    barGroup.append('rect')
      .attr('class', 'progress')
      .attr('x', timeScale(new Date(task.Start_date)))
      .attr('y', taskScale(task.Task)!)
      .attr('width', (timeScale(new Date(task.End_Date)) - timeScale(new Date(task.Start_date))) * (task.progress / 100))
      .attr('height', taskScale.bandwidth())
      .attr('fill', subtaskColors.progress)
      .attr('rx', 3)
      .attr('ry', 3)

    // Task label
    barGroup.append('text')
      .attr('class', 'task-label')
      .attr('x', timeScale(new Date(task.Start_date)) + 5)
      .attr('y', (taskScale(task.Task)! + taskScale.bandwidth() / 2))
      .attr('dy', '0.35em')
      .text(task.Responsibility)
      .attr('fill', 'white')
      .attr('font-size', '14.4px')
  })
}

onMounted(() => {
  drawChart()
})

watch(() => props.parentTask, () => {
  drawChart()
}, { deep: true })
</script>

<style scoped>
.subtask-gantt {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.subtask-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #E5E7EB;
  flex-shrink: 0;
}

.subtask-header h3 {
  margin: 0;
  color: #1F2937;
  font-weight: 600;
  font-size: 18px;
  /* Add text wrapping for long task names in header */
  max-width: calc(100% - 40px);
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6B7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  line-height: 1;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #1F2937;
  background: #F3F4F6;
}

.chart-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  padding: 20px;
}

.gantt-chart {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 20px;
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: #3F51B5 #E0E0E0;
  -webkit-overflow-scrolling: touch;
}

.gantt-chart::-webkit-scrollbar {
  height: 8px;
}

.gantt-chart::-webkit-scrollbar-track {
  background: #E0E0E0;
  border-radius: 4px;
}

.gantt-chart::-webkit-scrollbar-thumb {
  background: #3F51B5;
  border-radius: 4px;
}

.gantt-chart::-webkit-scrollbar-thumb:hover {
  background: #303F9F;
}

:deep(.x-axis), :deep(.y-axis) {
  font-size: 14.4px;
  color: #6B7280;
}

:deep(.x-axis text) {
  font-weight: 700;
  fill: #6B7280;
}

:deep(.y-axis text) {
  text-anchor: end;
  font-weight: 700;
  fill: #6B7280;
  dominant-baseline: middle;
  font-size: 14.4px !important;
  /* Add text wrapping for long task names */
  inline-size: 180px;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

:deep(.task-bar) {
  transition: opacity 0.2s;
}

:deep(.task-bar:hover) {
  opacity: 1;
}

:deep(.task-label) {
  font-size: 14.4px !important;
}

:deep(.grid line) {
  stroke-dasharray: 2,2;
}

@media (max-width: 768px) {
  :deep(.x-axis text) {
    font-size: 12px;
  }

  :deep(.y-axis text) {
    font-size: 12px;
  }
}
</style>
