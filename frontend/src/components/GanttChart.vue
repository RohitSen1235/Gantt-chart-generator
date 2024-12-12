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
  while (current <= end) {
    ticks.push(new Date(current))
    // Add 14 days
    current.setDate(current.getDate() + 14)
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
  
  // Calculate container width
  const containerWidth = chartContainer.value.clientWidth
  
  // Calculate dynamic width based on container size
  const width = Math.max(containerWidth - margin.left - margin.right, 400)
  
  // Calculate time extent with padding
  const timeExtent = d3.extent(props.tasks.flatMap(d => [new Date(d.Start_date), new Date(d.End_Date)])) as [Date, Date]
  const timePadding = 7 * 24 * 60 * 60 * 1000 // 7 days padding
  const paddedStartDate = new Date(timeExtent[0].getTime() - timePadding)
  const paddedEndDate = new Date(timeExtent[1].getTime() + timePadding)

  // Calculate dynamic height based on number of tasks
  const minHeightPerTask = 30
  const height = Math.max(props.tasks.length * minHeightPerTask, 200)

  // Create responsive SVG
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
    .attr('preserveAspectRatio', 'xMinYMin meet')
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const timeScale = d3.scaleTime()
    .domain([paddedStartDate, paddedEndDate])
    .range([0, width])

  const taskScale = d3.scaleBand()
    .domain(props.tasks.map(d => d.Task))
    .range([0, height])
    .padding(0.2)

  // Generate ticks for every two weeks
  const ticks = generateTicks(paddedStartDate, paddedEndDate)

  // Create axes with custom ticks
  const xAxis = d3.axisTop(timeScale)
    .tickValues(ticks)
    .tickFormat(d3.timeFormat("%b %d") as (date: Date | d3.NumberValue, i: number) => string)

  const yAxis = d3.axisLeft(taskScale)
    .ticks(props.tasks.length)

  // Add x-axis with rotated labels
  const xAxisGroup = svg.append('g')
    .attr('class', 'x-axis')
    .call(xAxis)

  // Rotate and position x-axis labels
  xAxisGroup.selectAll('text')
    .style('text-anchor', 'start')
    .attr('dx', '0.8em')
    .attr('dy', '-0.5em')
    .attr('transform', 'rotate(-45)')

  // Add y-axis
  svg.append('g')
    .attr('class', 'y-axis')
    .call(yAxis)

  // Add vertical grid lines
  svg.append('g')
    .attr('class', 'grid')
    .selectAll('line')
    .data(ticks)
    .enter()
    .append('line')
    .attr('x1', d => timeScale(d))
    .attr('x2', d => timeScale(d))
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', '#f0f0f0')
    .attr('stroke-width', 1)

  // Add bars
  svg.selectAll('.task-bar')
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
  svg.selectAll('.progress')
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
  svg.selectAll('.responsibility')
    .data(props.tasks)
    .enter()
    .append('text')
    .attr('class', 'responsibility')
    .attr('x', d => timeScale(new Date(d.Start_date)) + 5)
    .attr('y', d => (taskScale(d.Task) || 0) + taskScale.bandwidth() / 2)
    .attr('dy', '0.35em')
    .text(d => d.Responsibility)
    .attr('fill', 'brown')
    .attr('font-size', `${Math.min(taskScale.bandwidth() * 0.4, 12)}px`)
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
  /* Smooth scrolling for better UX */
  scroll-behavior: smooth;
  /* Show scrollbar only when needed */
  scrollbar-width: thin;
  scrollbar-color: #2196F3 #f0f0f0;
  /* Prevent content from expanding container */
  max-width: 100%;
  -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
}

/* Custom scrollbar styling for webkit browsers */
.gantt-chart::-webkit-scrollbar {
  height: 8px;
}

.gantt-chart::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 4px;
}

.gantt-chart::-webkit-scrollbar-thumb {
  background: #2196F3;
  border-radius: 4px;
}

.gantt-chart::-webkit-scrollbar-thumb:hover {
  background: #1976D2;
}

.download-buttons {
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.download-buttons button {
  padding: 0.5rem 1rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 120px;
}

.download-buttons button:hover {
  background-color: #1976D2;
}

:deep(.x-axis), :deep(.y-axis) {
  font-size: 12px;
}

:deep(.x-axis) line,
:deep(.y-axis) line {
  stroke: #ddd;
}

:deep(.x-axis) path,
:deep(.y-axis) path {
  stroke: #ddd;
}

:deep(.task-bar) {
  opacity: 0.8;
  transition: opacity 0.2s;
}

:deep(.task-bar:hover) {
  opacity: 1;
}

:deep(.y-axis text) {
  text-anchor: end;
  font-size: 12px;
}

:deep(.x-axis text) {
  font-weight: 500;
}

:deep(.grid line) {
  stroke-dasharray: 2,2;
}

/* Responsive styles */
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

/* Ensure SVG is responsive */
:deep(svg) {
  width: 100%;
  height: auto;
}
</style>
