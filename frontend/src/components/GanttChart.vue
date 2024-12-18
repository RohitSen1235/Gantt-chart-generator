<template>
  <div class="chart-wrapper">
    <div class="download-buttons">
      <button @click="downloadSVG">Download SVG</button>
      <button @click="downloadJPEG">Download JPEG</button>
    </div>
    <div ref="chartContainer" class="gantt-chart"></div>

    <!-- Subtask Modal -->
    <div v-if="selectedTask" class="modal" @click.self="selectedTask = null">
      <div class="modal-content">
        <SubtaskGanttChart 
          :parent-task="selectedTask" 
          @close="selectedTask = null"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as d3 from 'd3'
import type { Task } from '../types'
import SubtaskGanttChart from './SubtaskGanttChart.vue'

const props = defineProps<{
  tasks: Task[]
}>()

const chartContainer = ref<HTMLElement | null>(null)
const selectedTask = ref<Task | null>(null)

// Filter out subtasks for main view
const mainTasks = computed(() => 
  props.tasks.filter(task => !task.is_subtask)
)

const downloadSVG = () => {
  const svgElement = chartContainer.value?.querySelector('svg')
  if (!svgElement) return

  const svgCopy = svgElement.cloneNode(true) as SVGElement
  svgCopy.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  
  const svgString = new XMLSerializer().serializeToString(svgCopy)
  
  const downloadLink = document.createElement('a')
  downloadLink.href = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString)
  downloadLink.download = 'gantt-chart.svg'
  
  document.body.appendChild(downloadLink)
  downloadLink.click()
  document.body.removeChild(downloadLink)
}

const downloadJPEG = () => {
  const svgElement = chartContainer.value?.querySelector('svg')
  if (!svgElement) return

  const canvas = document.createElement('canvas')
  const svgRect = svgElement.getBoundingClientRect()
  canvas.width = svgRect.width
  canvas.height = svgRect.height

  const svgString = new XMLSerializer().serializeToString(svgElement)
  const svg = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svg)

  const img = new Image()
  img.onload = () => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)

    const jpegUrl = canvas.toDataURL('image/jpeg', 1.0)
    const downloadLink = document.createElement('a')
    downloadLink.href = jpegUrl
    downloadLink.download = 'gantt-chart.jpg'
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)

    URL.revokeObjectURL(url)
  }
  img.src = url
}

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

const calculateTextWidth = (text: string, fontSize: number = 12): number => {
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
  if (!chartContainer.value || !mainTasks.value.length) return

  // Clear previous chart
  d3.select(chartContainer.value).selectAll('*').remove()

  const tasks = mainTasks.value
  const leftMargin = calculateLeftMargin(tasks)
  
  const margin = { 
    top: 60, 
    right: 40, 
    bottom: 40, 
    left: leftMargin 
  }

  // Calculate time extent with type safety
  const dates = tasks.flatMap(task => [new Date(task.Start_date), new Date(task.End_Date)])
  const timeExtent: [Date, Date] = [
    new Date(Math.min(...dates.map(d => d.getTime()))),
    new Date(Math.max(...dates.map(d => d.getTime())))
  ]
  
  // Start from Monday of the first task's week
  const startDate = getPreviousMonday(timeExtent[0])
  const endDate = getNextMonday(timeExtent[1])
  
  const weekInMillis = 7 * 24 * 60 * 60 * 1000
  const totalWeeks = Math.ceil((endDate.getTime() - startDate.getTime()) / weekInMillis)
  const minWidthPerWeek = 60
  const totalWidth = totalWeeks * minWidthPerWeek
  
  const minHeightPerTask = 40
  const height = Math.max(tasks.length * minHeightPerTask, 360)

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

  // Draw task bars
  tasks.forEach((task: Task) => {
    const barGroup = chartGroup.append('g')
      .attr('class', 'task-group')

    // Main task bar
    const mainBar = barGroup.append('rect')
      .attr('class', 'task-bar')
      .attr('x', timeScale(new Date(task.Start_date)))
      .attr('y', taskScale(task.Task)!)
      .attr('width', timeScale(new Date(task.End_Date)) - timeScale(new Date(task.Start_date)))
      .attr('height', taskScale.bandwidth())
      .attr('fill', '#2196F3')
      .attr('rx', 3)
      .attr('ry', 3)
      .style('opacity', 0.9)
      .style('cursor', task.subtasks.length ? 'pointer' : 'default')

    // Add click handler to main bar if task has subtasks
    if (task.subtasks.length) {
      mainBar.on('click', () => {
        selectedTask.value = task
      })
    }

    // Progress bar with click handler for tasks with subtasks
    const progressBar = barGroup.append('rect')
      .attr('class', 'progress')
      .attr('x', timeScale(new Date(task.Start_date)))
      .attr('y', taskScale(task.Task)!)
      .attr('width', (timeScale(new Date(task.End_Date)) - timeScale(new Date(task.Start_date))) * (task.progress / 100))
      .attr('height', taskScale.bandwidth())
      .attr('fill', '#4CAF50')
      .attr('rx', 3)
      .attr('ry', 3)
      .style('cursor', task.subtasks.length ? 'pointer' : 'default')

    if (task.subtasks.length) {
      progressBar.on('click', () => {
        selectedTask.value = task
      })
    }

    // Task label
    barGroup.append('text')
      .attr('class', 'task-label')
      .attr('x', timeScale(new Date(task.Start_date)) + 5)
      .attr('y', (taskScale(task.Task)! + taskScale.bandwidth() / 2))
      .attr('dy', '0.35em')
      .text(task.Responsibility)
      .attr('fill', 'white')
      .attr('font-size', '14.4px')

    // Subtask indicator
    if (task.subtasks.length) {
      barGroup.append('text')
        .attr('class', 'subtask-indicator')
        .attr('x', timeScale(new Date(task.End_Date)) + 8)
        .attr('y', taskScale(task.Task)! + taskScale.bandwidth() / 2)
        .attr('dy', '0.35em')
        .text(`(${task.subtasks.length} subtasks)`)
        .attr('fill', '#6B7280')
        .attr('font-size', '14.4px')
    }
  })
}

// Debounce function for resize handling
const debounce = (fn: Function, ms = 300) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return function (this: any, ...args: any[]) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), ms)
  }
}

onMounted(() => {
  drawChart()
  const debouncedDrawChart = debounce(drawChart)
  window.addEventListener('resize', debouncedDrawChart)
})

watch(() => props.tasks, () => {
  drawChart()
}, { deep: true })

onUnmounted(() => {
  window.removeEventListener('resize', drawChart)
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  max-width: 100%;
  position: relative;
  margin: 0 auto;
}

.gantt-chart {
  width: 100%;
  min-height: 400px;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 20px;
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: #3F51B5 #E0E0E0;
  max-width: 100%;
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

.download-buttons {
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.download-buttons button {
  padding: 0.5rem 1rem;
  background-color: #3F51B5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 120px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.download-buttons button:hover {
  background-color: #303F9F;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow: auto;
}

:deep(.x-axis), :deep(.y-axis) {
  font-size: 14.4px;
  color: #757575;
}

:deep(.x-axis text) {
  font-weight: 700;
  fill: #757575;
}

:deep(.y-axis text) {
  text-anchor: end;
  font-weight: 700;
  fill: #757575;
  dominant-baseline: middle;

  font-size: 14.4px !important;
  /* Add text wrapping for long task names */
  inline-size: 180px;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

:deep(.task-bar) {
  opacity: 0.9;
  transition: opacity 0.2s;
}

:deep(.task-bar:hover) {
  opacity: 1;
}

:deep(.task-label) {
  font-size: 14.4px !important; /* Increased by 20% from 12px */
}

:deep(.subtask-indicator) {
  font-size: 14.4px !important; /* Increased by 20% from 12px */
}

:deep(.grid line) {
  stroke-dasharray: 2,2;
}

@media (max-width: 768px) {
  .download-buttons {
    flex-direction: column;
    align-items: stretch;
}

  .download-buttons button {
    width: 100%;
  }

  :deep(.x-axis text) {
    font-size: 12px; /* Increased by 20% from 10px */
  }

  :deep(.y-axis text) {
    font-size: 12px; /* Increased by 20% from 10px */
  }
}

:deep(svg) {
  height: auto;
}
</style>
