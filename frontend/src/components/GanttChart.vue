<template>
  <div class="chart-wrapper">
    <div class="download-buttons">
      <button @click="downloadSVG">Download SVG</button>
      <button @click="downloadJPEG">Download JPEG</button>
    </div>
    <div ref="chartContainer" class="gantt-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as d3 from 'd3'
import type { Task } from '../types'

const props = defineProps<{
  tasks: Task[]
}>()

const chartContainer = ref<HTMLElement | null>(null)

const downloadSVG = () => {
  const svgElement = chartContainer.value?.querySelector('svg')
  if (!svgElement) return

  // Create a copy of the SVG element
  const svgCopy = svgElement.cloneNode(true) as SVGElement
  
  // Set the XML namespace
  svgCopy.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  
  // Convert SVG to string
  const svgString = new XMLSerializer().serializeToString(svgCopy)
  
  // Create download link
  const downloadLink = document.createElement('a')
  downloadLink.href = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString)
  downloadLink.download = 'gantt-chart.svg'
  
  // Trigger download
  document.body.appendChild(downloadLink)
  downloadLink.click()
  document.body.removeChild(downloadLink)
}

const downloadJPEG = () => {
  const svgElement = chartContainer.value?.querySelector('svg')
  if (!svgElement) return

  // Create a canvas element
  const canvas = document.createElement('canvas')
  const svgRect = svgElement.getBoundingClientRect()
  canvas.width = svgRect.width
  canvas.height = svgRect.height

  // Convert SVG to string
  const svgString = new XMLSerializer().serializeToString(svgElement)
  const svg = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svg)

  // Create image from SVG
  const img = new Image()
  img.onload = () => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Draw image to canvas
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)

    // Convert to JPEG and download
    const jpegUrl = canvas.toDataURL('image/jpeg', 1.0)
    const downloadLink = document.createElement('a')
    downloadLink.href = jpegUrl
    downloadLink.download = 'gantt-chart.jpg'
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)

    // Clean up
    URL.revokeObjectURL(url)
  }
  img.src = url
}

const generateTicks = (start: Date, end: Date): Date[] => {
  const ticks: Date[] = []
  const current = new Date(start)
  // Ensure we start at the beginning of the week
  current.setDate(current.getDate() - current.getDay())
  
  while (current <= end) {
    ticks.push(new Date(current))
    // Add 7 days (one week)
    current.setDate(current.getDate() + 7)
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
  if (!tasks.length) return 150 // Default margin if no tasks
  
  // Find the longest task name
  const longestTask = tasks.reduce((longest, task) => 
    task.Task.length > longest.length ? task.Task : longest
  , tasks[0].Task)
  
  // Calculate width with some padding (40px for safety margin)
  const textWidth = calculateTextWidth(longestTask)
  return Math.max(Math.ceil(textWidth) + 40, 120) // Minimum margin of 120px
}

const drawChart = () => {
  if (!chartContainer.value || !props.tasks.length) return

  // Clear previous chart
  d3.select(chartContainer.value).selectAll('*').remove()

  // Calculate dynamic left margin based on longest task name
  const leftMargin = calculateLeftMargin(props.tasks)
  
  // Set up margins with dynamic left margin
  const margin = { 
    top: 60, 
    right: 20, 
    bottom: 40, 
    left: leftMargin 
  }
  
  // Calculate time extent with padding
  const timeExtent = d3.extent(props.tasks.flatMap(d => [new Date(d.Start_date), new Date(d.End_Date)])) as [Date, Date]
  const weekInMillis = 7 * 24 * 60 * 60 * 1000
  const startDate = new Date(timeExtent[0].getTime() - weekInMillis)
  const endDate = new Date(timeExtent[1].getTime() + weekInMillis)
  
  // Calculate the number of weeks between start and end
  const totalWeeks = Math.ceil((endDate.getTime() - startDate.getTime()) / weekInMillis)
  
  // Set minimum width per week (in pixels)
  const minWidthPerWeek = 100
  const totalWidth = totalWeeks * minWidthPerWeek
  
  // Calculate dynamic height based on number of tasks
  const minHeightPerTask = 40
  const height = Math.max(props.tasks.length * minHeightPerTask, 200)

  // Create responsive SVG with fixed width based on weeks
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', totalWidth + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)

  // Create a clip path to ensure grid lines don't extend beyond the chart area
  svg.append('defs')
    .append('clipPath')
    .attr('id', 'chart-area')
    .append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', totalWidth)
    .attr('height', height)

  // Create main chart group
  const mainGroup = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const timeScale = d3.scaleTime()
    .domain([startDate, endDate])
    .range([0, totalWidth])

  const taskScale = d3.scaleBand()
    .domain(props.tasks.map(d => d.Task))
    .range([0, height])
    .padding(0.2)

  // Generate ticks for every week
  const ticks = generateTicks(startDate, endDate)

  // Create axes with custom ticks
  const xAxis = d3.axisTop(timeScale)
    .tickValues(ticks)
    .tickFormat(d3.timeFormat("%b %d") as (date: Date | d3.NumberValue, i: number) => string)

  const yAxis = d3.axisLeft(taskScale)
    .ticks(props.tasks.length)

  // Add x-axis with rotated labels
  const xAxisGroup = mainGroup.append('g')
    .attr('class', 'x-axis')
    .call(xAxis)

  // Rotate and position x-axis labels
  xAxisGroup.selectAll('text')
    .style('text-anchor', 'start')
    .attr('dx', '0.8em')
    .attr('dy', '-0.5em')
    .attr('transform', 'rotate(-45)')

  // Add y-axis
  mainGroup.append('g')
    .attr('class', 'y-axis')
    .call(yAxis)

  // Add vertical grid lines with clip path
  mainGroup.append('g')
    .attr('class', 'grid')
    .attr('clip-path', 'url(#chart-area)')
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

  // Add bars
  mainGroup.selectAll('.task-bar')
    .data(props.tasks)
    .enter()
    .append('rect')
    .attr('class', 'task-bar')
    .attr('x', d => timeScale(new Date(d.Start_date)))
    .attr('y', d => taskScale(d.Task) || 0)
    .attr('width', d => {
      const start = timeScale(new Date(d.Start_date))
      const end = timeScale(new Date(d.End_Date))
      return end - start
    })
    .attr('height', taskScale.bandwidth())
    .attr('fill', '#2196F3')
    .attr('rx', 3)
    .attr('ry', 3)

  // Add progress indicators
  mainGroup.selectAll('.progress')
    .data(props.tasks)
    .enter()
    .append('rect')
    .attr('class', 'progress')
    .attr('x', d => timeScale(new Date(d.Start_date)))
    .attr('y', d => (taskScale(d.Task) || 0))
    .attr('width', d => {
      const start = timeScale(new Date(d.Start_date))
      const end = timeScale(new Date(d.End_Date))
      return (end - start) * (d.progress / 100)
    })
    .attr('height', taskScale.bandwidth())
    .attr('fill', '#4CAF50')
    .attr('rx', 3)
    .attr('ry', 3)

  // Add responsibility labels with dynamic font size
  mainGroup.selectAll('.responsibility')
    .data(props.tasks)
    .enter()
    .append('text')
    .attr('class', 'responsibility')
    .attr('x', d => timeScale(new Date(d.Start_date)) + 5)
    .attr('y', d => (taskScale(d.Task) || 0) + taskScale.bandwidth() / 2)
    .attr('dy', '0.5em')
    .text(d => d.Responsibility)
    .attr('fill', 'black')
    .attr('font-size', `${Math.min(taskScale.bandwidth() * 0.6, 12)}px`)
}

// Debounce function for resize handling
const debounce = (fn: Function, ms = 300) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return function (this: any, ...args: any[]) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), ms)
  }
}

// Draw chart on mount and when tasks change
onMounted(() => {
  drawChart()
  const debouncedDrawChart = debounce(drawChart)
  window.addEventListener('resize', debouncedDrawChart)
})

watch(() => props.tasks, () => {
  drawChart()
}, { deep: true })

// Clean up event listener
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

:deep(.x-axis), :deep(.y-axis) {
  font-size: 12px;
  color: #757575;
}

:deep(.x-axis) line,
:deep(.y-axis) line {
  stroke: #E0E0E0;
}

:deep(.x-axis) path,
:deep(.y-axis) path {
  stroke: #E0E0E0;
}

:deep(.task-bar) {
  opacity: 0.9;
  transition: opacity 0.2s;
}

:deep(.task-bar:hover) {
  opacity: 1;
}

:deep(.y-axis text) {
  text-anchor: end;
  font-size: 12px;
  fill: #757575;
}

:deep(.x-axis text) {
  font-weight: 500;
  fill: #757575;
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
    font-size: 10px;
  }

  :deep(.y-axis text) {
    font-size: 10px;
  }
}

:deep(svg) {
  height: auto;
}
</style>
