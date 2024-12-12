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

.expand-icon {
  color: #6B7280;
  font-size: 0.8em;
}

.task-details {
  padding-top: 16px;
  border-top: 1px solid #E5E7EB;
}

.btn-remove {
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

.btn-remove:hover {
  background: #DC2626;
  transform: scale(1.05);
}

.btn-add {
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

.btn-add:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
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
