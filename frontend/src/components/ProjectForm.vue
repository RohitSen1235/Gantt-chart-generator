<template>
  <div class="project-form">
    <h3>{{ editMode ? 'Edit Project' : 'Create Project' }}</h3>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">Project Name:</label>
        <input
          type="text"
          id="name"
          v-model="projectData.name"
          required
          class="form-control"
        />
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea
          id="description"
          v-model="projectData.description"
          class="form-control"
        ></textarea>
      </div>

      <div class="tasks-section">
        <h4>Tasks</h4>
        <div v-for="(task, index) in projectData.tasks" :key="index" class="task-item">
          <div class="task-header" @click="toggleTask(index)">
            <div class="task-summary">
              <h5>Task {{ index + 1 }}: {{ task.Task }}</h5>
              <span class="task-info">
                {{ task.subtasks.length }} subtask{{ task.subtasks.length !== 1 ? 's' : '' }}
              </span>
              <span class="expand-icon">{{ expandedTasks[index] ? '▼' : '▶' }}</span>
            </div>
            <button type="button" @click.stop="removeTask(index)" class="btn-remove">×</button>
          </div>
          
          <div v-show="expandedTasks[index]" class="task-details">
            <div class="form-group">
              <label :for="'task-name-' + index">Task Name:</label>
              <input
                :id="'task-name-' + index"
                v-model="task.Task"
                required
                class="form-control"
              />
            </div>

            <div class="form-group">
              <label :for="'responsibility-' + index">Responsibility:</label>
              <input
                :id="'responsibility-' + index"
                v-model="task.Responsibility"
                required
                class="form-control"
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label :for="'start-date-' + index">Start Date:</label>
                <input
                  :id="'start-date-' + index"
                  type="date"
                  v-model="task.Start_date"
                  required
                  class="form-control"
                  :disabled="task.subtasks.length > 0"
                />
              </div>

              <div class="form-group">
                <label :for="'end-date-' + index">End Date:</label>
                <input
                  :id="'end-date-' + index"
                  type="date"
                  v-model="task.End_Date"
                  required
                  class="form-control"
                  :disabled="task.subtasks.length > 0"
                />
              </div>

              <div class="form-group">
                <label :for="'progress-' + index">Progress:</label>
                <input
                  :id="'progress-' + index"
                  type="number"
                  v-model="task.progress"
                  min="0"
                  max="100"
                  class="form-control"
                  :disabled="task.subtasks.length > 0"
                />
              </div>
            </div>

            <!-- Subtasks Section -->
            <div class="subtasks-section">
              <h5>Subtasks</h5>
              <div v-if="task.subtasks.length > 0" class="subtasks-list">
                <div v-for="(subtask, subtaskIndex) in task.subtasks" :key="subtaskIndex" class="subtask-item">
                  <div class="subtask-header">
                    <span>{{ subtask.Task }}</span>
                    <button type="button" @click="removeSubtask(index, subtaskIndex)" class="btn-remove-subtask">×</button>
                  </div>
                  <div class="subtask-details">
                    <span>{{ subtask.Responsibility }}</span>
                    <span>{{ formatDate(subtask.Start_date) }} - {{ formatDate(subtask.End_Date) }}</span>
                    <span>Progress: {{ subtask.progress }}%</span>
                  </div>
                </div>
              </div>
              <button type="button" @click="addSubtask(index)" class="btn-add-subtask">Add Subtask</button>
            </div>
          </div>
        </div>

        <button type="button" @click="addTask" class="btn-add">Add Task</button>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary">{{ editMode ? 'Update' : 'Create' }}</button>
        <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
      </div>
    </form>

    <!-- Task Form Modal -->
    <div v-if="showTaskForm" class="modal">
      <div class="modal-content">
        <TaskForm 
          :is-subtask="true"
          @task-added="handleSubtaskAdded"
          @cancel="showTaskForm = false"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Project, Task } from '../types'
import TaskForm from './TaskForm.vue'

const props = defineProps<{
  project: Project | undefined
}>()

const emit = defineEmits<{
  (e: 'submit', project: Project): void
  (e: 'cancel'): void
}>()

const editMode = ref(false)
const projectData = ref<Project>({
  name: '',
  description: '',
  tasks: []
})

const expandedTasks = ref<{ [key: number]: boolean }>({})
const showTaskForm = ref(false)
const activeTaskIndex = ref<number | null>(null)

onMounted(() => {
  if (props.project) {
    editMode.value = true
    projectData.value = JSON.parse(JSON.stringify(props.project))
    // Initialize all tasks as collapsed
    projectData.value.tasks.forEach((_, index) => {
      expandedTasks.value[index] = false
    })
  }
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

const toggleTask = (index: number) => {
  expandedTasks.value[index] = !expandedTasks.value[index]
}

const updateTaskDates = (taskIndex: number) => {
  const task = projectData.value.tasks[taskIndex]
  if (task.subtasks.length === 0) return

  // Find earliest start date and latest end date among subtasks
  const startDates = task.subtasks.map(subtask => new Date(subtask.Start_date).getTime())
  const endDates = task.subtasks.map(subtask => new Date(subtask.End_Date).getTime())

  const earliestStart = new Date(Math.min(...startDates))
  const latestEnd = new Date(Math.max(...endDates))

  // Update parent task dates
  task.Start_date = earliestStart.toISOString().split('T')[0]
  task.End_Date = latestEnd.toISOString().split('T')[0]

  // Update progress based on subtasks
  const totalProgress = task.subtasks.reduce((sum, subtask) => sum + subtask.progress, 0)
  task.progress = Math.round(totalProgress / task.subtasks.length)
}

const addTask = () => {
  const newIndex = projectData.value.tasks.length
  projectData.value.tasks.push({
    id: Date.now(),
    Task: '',
    Responsibility: '',
    Start_date: '',
    End_Date: '',
    progress: 0,
    subtasks: [],
    is_subtask: false
  })
  // Auto-expand newly added task
  expandedTasks.value[newIndex] = true
}

const removeTask = (index: number) => {
  projectData.value.tasks.splice(index, 1)
  // Clean up expanded state
  delete expandedTasks.value[index]
  // Reindex remaining tasks' expanded states
  for (let i = index; i < projectData.value.tasks.length; i++) {
    expandedTasks.value[i] = expandedTasks.value[i + 1]
  }
}

const addSubtask = (taskIndex: number) => {
  activeTaskIndex.value = taskIndex
  showTaskForm.value = true
}

const handleSubtaskAdded = (subtask: Task) => {
  if (activeTaskIndex.value === null) return

  const taskIndex = activeTaskIndex.value
  const parentTask = projectData.value.tasks[taskIndex]

  parentTask.subtasks.push({
    ...subtask,
    parent_id: parentTask.id,
    is_subtask: true
  })

  updateTaskDates(taskIndex)
  showTaskForm.value = false
  activeTaskIndex.value = null
}

const removeSubtask = (taskIndex: number, subtaskIndex: number) => {
  projectData.value.tasks[taskIndex].subtasks.splice(subtaskIndex, 1)
  updateTaskDates(taskIndex)
}

const handleSubmit = () => {
  emit('submit', projectData.value)
}
</script>

<style scoped>
.project-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.project-form h3 {
  color: #1F2937;
  margin-bottom: 24px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 0.95em;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  background: #F9FAFB;
  color: #1F2937;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: white;
}

.form-control:disabled {
  background: #F3F4F6;
  cursor: not-allowed;
  opacity: 0.7;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.tasks-section {
  margin-top: 32px;
  border-top: 1px solid #E5E7EB;
  padding-top: 24px;
}

.tasks-section h4 {
  color: #1F2937;
  margin-bottom: 16px;
  font-weight: 600;
}

.task-item {
  background-color: white;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  cursor: pointer;
  user-select: none;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.task-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.task-summary h5 {
  margin: 0;
  color: #1F2937;
  font-weight: 500;
}

.task-info {
  color: #6B7280;
  font-size: 0.9em;
}

.expand-icon {
  color: #6B7280;
  font-size: 0.8em;
}

.task-details {
  padding-top: 16px;
  border-top: 1px solid #E5E7EB;
}

.subtasks-section {
  margin-top: 20px;
  padding: 16px;
  background: #F9FAFB;
  border-radius: 6px;
}

.subtasks-section h5 {
  color: #374151;
  margin-bottom: 16px;
  font-weight: 500;
}

.subtask-item {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

.subtask-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.btn-remove, .btn-remove-subtask {
  background: #EF4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s;
}

.btn-remove-subtask {
  width: 24px;
  height: 24px;
  font-size: 16px;
}

.btn-remove:hover, .btn-remove-subtask:hover {
  background: #DC2626;
  transform: scale(1.05);
}

.btn-add, .btn-add-subtask {
  background: #10B981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(16, 185, 129, 0.1);
}

.btn-add-subtask {
  background: #6366F1;
  font-size: 0.9em;
  padding: 8px 16px;
}

.btn-add:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

.btn-add-subtask:hover {
  background: #4F46E5;
  transform: translateY(-1px);
}

.form-actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary {
  background: #6366F1;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(99, 102, 241, 0.15);
}

.btn-primary:hover {
  background: #4F46E5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.btn-secondary {
  background: #9CA3AF;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #6B7280;
  transform: translateY(-1px);
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.task-header:hover {
  background-color: #F3F4F8;
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .project-form {
    padding: 16px;
  }
}
</style>
