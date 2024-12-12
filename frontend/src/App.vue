<template>
  <div class="app">
    <header>
      <h1>Project Gantt Chart</h1>
      <button @click="showProjectForm = true" class="btn-primary">New Project</button>
    </header>

    <div class="main-content">
      <div class="projects-sidebar" v-if="projects.length > 0">
        <h2>Projects</h2>
        <div class="project-list">
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-item"
            :class="{ active: selectedProject?.id === project.id }"
            @click="selectProject(project)"
          >
            <div class="project-info">
              <h3>{{ project.name }}</h3>
              <p>{{ project.description }}</p>
              <small>Tasks: {{ project.tasks.length }}</small>
            </div>
            <div class="project-actions">
              <button @click.stop="editProject(project)" class="btn-icon">✏️</button>
              <button @click.stop="deleteProject(project.id)" class="btn-icon">🗑️</button>
            </div>
          </div>
        </div>
      </div>

      <div class="content-area">
        <div v-if="selectedProject" class="project-view">
          <h2>{{ selectedProject.name }}</h2>
          <p>{{ selectedProject.description }}</p>
          <GanttChart
            v-if="selectedProject.tasks.length > 0"
            :tasks="sortedTasks"
            @update:tasks="updateProjectTasks"
          />
          <div v-else class="no-tasks">
            <p>No tasks in this project yet.</p>
            <button @click="editProject(selectedProject)" class="btn-primary">Add Tasks</button>
          </div>
        </div>
        <div v-else class="welcome-message">
          <h2>Welcome to Project Gantt Chart</h2>
          <p v-if="projects.length === 0">
            Get started by creating your first project!
          </p>
          <p v-else>
            Select a project from the sidebar to view its Gantt chart.
          </p>
        </div>
      </div>
    </div>

    <!-- Project Form Modal -->
    <div v-if="showProjectForm" class="modal">
      <div class="modal-content">
        <ProjectForm
          :project="editingProject"
          @submit="saveProject"
          @cancel="closeProjectForm"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { Project, Task } from './types'
import GanttChart from './components/GanttChart.vue'
import ProjectForm from './components/ProjectForm.vue'

const projects = ref<Project[]>([])
const selectedProject = ref<Project | null>(null)
const showProjectForm = ref(false)
const editingProject = ref<Project | undefined>(undefined)

const sortedTasks = computed(() => {
  if (!selectedProject.value) return []
  return [...selectedProject.value.tasks].sort((a, b) => {
    return new Date(a.Start_date).getTime() - new Date(b.Start_date).getTime()
  })
})

const API_BASE = 'http://localhost:8000'

onMounted(async () => {
  await loadProjects()
})

async function loadProjects() {
  try {
    const response = await fetch(`${API_BASE}/projects/`)
    const data = await response.json()
    projects.value = data.projects
  } catch (error) {
    console.error('Error loading projects:', error)
  }
}

async function saveProject(project: Project) {
  try {
    const url = project.id
      ? `${API_BASE}/projects/${project.id}`
      : `${API_BASE}/projects/`
    const method = project.id ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(project),
    })
    
    if (!response.ok) throw new Error('Failed to save project')
    
    await loadProjects()
    closeProjectForm()
    
    if (!project.id) {
      // If it was a new project, select it
      const newProject = await response.json()
      selectProject(newProject)
    }
  } catch (error) {
    console.error('Error saving project:', error)
  }
}

async function deleteProject(projectId?: number) {
  if (!projectId || !confirm('Are you sure you want to delete this project?')) return
  
  try {
    await fetch(`${API_BASE}/projects/${projectId}`, {
      method: 'DELETE',
    })
    
    if (selectedProject.value?.id === projectId) {
      selectedProject.value = null
    }
    
    await loadProjects()
  } catch (error) {
    console.error('Error deleting project:', error)
  }
}

function selectProject(project: Project) {
  selectedProject.value = project
}

function editProject(project: Project) {
  editingProject.value = project
  showProjectForm.value = true
}

function closeProjectForm() {
  showProjectForm.value = false
  editingProject.value = undefined
}

async function updateProjectTasks(tasks: Task[]) {
  if (!selectedProject.value) return
  
  const updatedProject = {
    ...selectedProject.value,
    tasks,
  }
  
  await saveProject(updatedProject)
}
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  min-height: calc(100vh - 100px);
}

.projects-sidebar {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.project-item {
  background: white;
  padding: 15px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.project-item.active {
  border-color: #007bff;
  box-shadow: 0 0 0 1px #007bff;
}

.project-info h3 {
  margin: 0 0 5px 0;
  font-size: 1.1em;
}

.project-info p {
  margin: 0 0 5px 0;
  font-size: 0.9em;
  color: #666;
}

.project-info small {
  color: #888;
}

.project-actions {
  display: flex;
  gap: 5px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f0f0f0;
}

.content-area {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.welcome-message {
  text-align: center;
  padding: 40px;
}

.no-tasks {
  text-align: center;
  padding: 40px;
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
  border-radius: 8px;
  max-height: 90vh;
  overflow-y: auto;
  width: 90%;
  max-width: 800px;
}

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #0056b3;
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .projects-sidebar {
    order: 1;
  }
  
  .content-area {
    order: 2;
  }
}
</style>
