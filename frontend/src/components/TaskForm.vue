<template>
  <div class="task-form">
    <h2>{{ isSubtask ? 'Add Subtask' : 'Add Task' }}</h2>
    <form @submit.prevent="submitTask">
      <div class="form-group">
        <label for="task">Task Name:</label>
        <input 
          type="text" 
          id="task" 
          v-model="task.Task" 
          required
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="responsibility">Responsibility:</label>
        <input 
          type="text" 
          id="responsibility" 
          v-model="task.Responsibility" 
          required
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="startDate">Start Date:</label>
        <input 
          type="date" 
          id="startDate" 
          v-model="task.Start_date" 
          required
          class="form-control"
        >
      </div>

      <div class="form-group">
        <label for="endDate">End Date:</label>
        <input 
          type="date" 
          id="endDate" 
          v-model="task.End_Date" 
          required
          class="form-control"
          :min="task.Start_date"
        >
      </div>

      <div class="form-group">
        <label for="progress">Progress (%):</label>
        <input 
          type="number" 
          id="progress" 
          v-model="task.progress" 
          min="0"
          max="100"
          required
          class="form-control progress-input"
        >
      </div>

      <div v-if="!isSubtask" class="subtasks-section">
        <h3>Subtasks</h3>
        <div v-if="task.subtasks.length > 0" class="subtasks-list">
          <div v-for="(subtask, index) in task.subtasks" :key="subtask.id" class="subtask-item">
            <div class="subtask-header">
              <span>{{ subtask.Task }}</span>
              <button type="button" class="btn-icon" @click="removeSubtask(index)">🗑️</button>
            </div>
            <div class="subtask-details">
              <span>{{ subtask.Responsibility }}</span>
              <span>{{ formatDate(subtask.Start_date) }} - {{ formatDate(subtask.End_Date) }}</span>
              <span>Progress: {{ subtask.progress }}%</span>
            </div>
          </div>
        </div>
        <button type="button" class="btn-secondary" @click="showSubtaskForm = true">
          Add Subtask
        </button>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary">
          {{ isSubtask ? 'Add Subtask' : 'Add Task' }}
        </button>
        <button v-if="isSubtask" type="button" class="btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
      </div>
    </form>

    <!-- Subtask Modal -->
    <div v-if="showSubtaskForm" class="modal">
      <div class="modal-content">
        <TaskForm 
          :is-subtask="true"
          @task-added="addSubtask"
          @cancel="showSubtaskForm = false"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Task } from '../types'

const props = defineProps<{
  isSubtask?: boolean
}>()

const emit = defineEmits<{
  (e: 'task-added', task: Task): void
  (e: 'cancel'): void
}>()

const showSubtaskForm = ref(false)

const task = ref<Task>({
  id: Date.now(),
  Task: '',
  Responsibility: '',
  Start_date: '',
  End_Date: '',
  progress: 0,
  subtasks: [],
  is_subtask: props.isSubtask || false,
  parent_id: undefined
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

const updateParentDates = () => {
  if (task.value.subtasks.length === 0) return

  // Find earliest start date and latest end date among subtasks
  const startDates = task.value.subtasks.map(subtask => new Date(subtask.Start_date).getTime())
  const endDates = task.value.subtasks.map(subtask => new Date(subtask.End_Date).getTime())

  const earliestStart = new Date(Math.min(...startDates))
  const latestEnd = new Date(Math.max(...endDates))

  // Update parent task dates
  task.value.Start_date = earliestStart.toISOString().split('T')[0]
  task.value.End_Date = latestEnd.toISOString().split('T')[0]
}

const addSubtask = (subtask: Task) => {
  task.value.subtasks.push({
    ...subtask,
    parent_id: task.value.id,
    is_subtask: true
  })
  updateParentDates()
  showSubtaskForm.value = false
}

const removeSubtask = (index: number) => {
  task.value.subtasks.splice(index, 1)
  updateParentDates()
}

const submitTask = () => {
  const newTask = { 
    ...task.value,
    id: Date.now()
  }

  // Calculate progress based on subtasks if they exist
  if (newTask.subtasks.length > 0) {
    const totalProgress = newTask.subtasks.reduce((sum, subtask) => sum + subtask.progress, 0)
    newTask.progress = Math.round(totalProgress / newTask.subtasks.length)
  }

  emit('task-added', newTask)

  // Reset form
  task.value = {
    id: Date.now(),
    Task: '',
    Responsibility: '',
    Start_date: '',
    End_Date: '',
    progress: 0,
    subtasks: [],
    is_subtask: props.isSubtask || false,
    parent_id: undefined
  }
}
</script>

<style scoped>
.task-form {
  max-width: 500px;
  margin: 0 auto;
  padding: 24px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #E5E7EB;
}

.task-form h2 {
  color: #1F2937;
  margin-bottom: 24px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

label {
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
  font-size: 0.95em;
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

.progress-input {
  width: 120px;
}

.subtasks-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #E5E7EB;
}

.subtasks-section h3 {
  color: #374151;
  margin-bottom: 16px;
  font-size: 1.1em;
}

.subtasks-list {
  margin-bottom: 16px;
}

.subtask-item {
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}

.subtask-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.subtask-header span {
  font-weight: 500;
  color: #374151;
}

.subtask-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9em;
  color: #6B7280;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary {
  background: #6366F1;
  color: white;
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95em;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(99, 102, 241, 0.15);
}

.btn-secondary {
  background: #F3F4F6;
  color: #374151;
  padding: 10px 24px;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95em;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #4F46E5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.btn-secondary:hover {
  background: #E5E7EB;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #E5E7EB;
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
  .task-form {
    padding: 16px;
    margin: 0 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
  }
}
</style>
