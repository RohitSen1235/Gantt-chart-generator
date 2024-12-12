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
        >
      </div>

      <div class="form-group">
        <label for="responsibility">Responsibility:</label>
        <input 
          type="text" 
          id="responsibility" 
          v-model="task.Responsibility" 
          required
        >
      </div>

      <div class="form-group">
        <label for="startDate">Start Date:</label>
        <input 
          type="date" 
          id="startDate" 
          v-model="task.Start_date" 
          required
        >
      </div>

      <div class="form-group">
        <label for="endDate">End Date:</label>
        <input 
          type="date" 
          id="endDate" 
          v-model="task.End_Date" 
          required
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
        >
      </div>

      <button type="submit" class="submit-btn">Add Task</button>
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
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

input[type="number"] {
  width: 100px;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.submit-btn:hover {
  background-color: #45a049;
}
</style>
