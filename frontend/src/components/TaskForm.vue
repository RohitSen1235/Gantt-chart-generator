<template>
  <div class="task-form">
    <h2>Add New Task</h2>
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

      <button type="submit" class="btn-primary">Add Task</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Task } from '../types'

const emit = defineEmits<{
  (e: 'task-added', task: Task): void
}>()

const task = ref<Task>({
  id: Date.now(),
  Task: '',
  Responsibility: '',
  Start_date: '',
  End_Date: '',
  progress: 0
})

const submitTask = () => {
  const newTask = { 
    ...task.value,
    id: Date.now() // Generate new ID for each task
  }
  emit('task-added', newTask)
  task.value = {
    id: Date.now(),
    Task: '',
    Responsibility: '',
    Start_date: '',
    End_Date: '',
    progress: 0
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

.btn-primary:hover {
  background: #4F46E5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

@media (max-width: 768px) {
  .task-form {
    padding: 16px;
    margin: 0 16px;
  }
}
</style>
