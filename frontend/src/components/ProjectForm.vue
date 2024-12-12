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
                />
              </div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Project, Task } from '../types'

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

const toggleTask = (index: number) => {
  expandedTasks.value[index] = !expandedTasks.value[index]
}

const addTask = () => {
  const newIndex = projectData.value.tasks.length
  projectData.value.tasks.push({
    Task: '',
    Responsibility: '',
    Start_date: '',
    End_Date: '',
    progress: 0,
    dependencies: []
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

const handleSubmit = () => {
  emit('submit', projectData.value)
}
</script>

<style scoped>
.project-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.tasks-section {
  margin-top: 20px;
  border-top: 1px solid #ddd;
  padding-top: 20px;
}

.task-item {
  background-color: #f9f9f9;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  cursor: pointer;
  user-select: none;
}

.task-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.task-summary h5 {
  margin: 0;
}

.expand-icon {
  color: #666;
  font-size: 0.8em;
}

.task-details {
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.btn-remove {
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-add {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.task-header:hover {
  background-color: #f0f0f0;
  border-radius: 4px;
}
</style>
