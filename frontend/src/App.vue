<template>
  <div class="app">
    <div class="container">
      <!-- Project List View -->
      <div v-if="!selectedProject" class="projects-grid">
        <header class="main-header">
          <h1>Project Gantt Chart</h1>
          <button @click="showProjectForm = true" class="btn-primary">New Project</button>
        </header>

        <div class="project-tiles">
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-tile"
            @click="selectProject(project)"
          >
            <div class="project-tile-header">
              <h3>{{ project.name }}</h3>
              <button @click.stop="deleteProject(project.id)" class="btn-icon" title="Delete Project">🗑️</button>
            </div>
            <p>{{ project.description }}</p>
            <div class="project-stats">
              <span>Tasks: {{ project.tasks.length }}</span>
              <div class="project-actions">
                <button @click.stop="editProject(project)" class="btn-icon" title="Edit Project">✏️</button>
              </div>
            </div>
          </div>

          <div v-if="projects.length === 0" class="empty-state">
            <h2>Welcome to Project Gantt Chart</h2>
            <p>Get started by creating your first project!</p>
            <button @click="showProjectForm = true" class="btn-primary">Create Project</button>
          </div>
        </div>
      </div>

      <!-- Project Detail View with Gantt Chart -->
      <div v-else class="project-detail-view">
        <header class="detail-header">
          <button @click="closeProject" class="btn-back">← Back to Projects</button>
          <div class="project-title">
            <h2>{{ selectedProject.name }}</h2>
            <p>{{ selectedProject.description }}</p>
          </div>
          <div class="project-actions">
            <button @click="editProject(selectedProject)" class="btn-primary">Edit Project</button>
          </div>
        </header>

        <div class="gantt-container">
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

function closeProject() {
  selectedProject.value = null
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
  min-height: 100vh;
  background: #F3F4F8;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.main-header {
  padding: 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.main-header h1 {
  color: #1F2937;
  font-weight: 600;
}

.projects-grid {
  padding: 20px 0;
}

.project-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-tile {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.project-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
}

.project-tile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.project-tile-header h3 {
  margin: 0;
  color: #1F2937;
  font-weight: 600;
}

.project-tile p {
  margin: 0 0 15px 0;
  color: #4B5563;
  font-size: 0.95em;
  line-height: 1.5;
}

.project-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #6B7280;
  font-size: 0.9em;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  opacity: 0.7;
  transition: all 0.2s;
}

.btn-icon:hover {
  opacity: 1;
  background: #F3F4F8;
}

.project-detail-view {
  min-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin: 20px 0;
}

.detail-header {
  padding: 24px;
  border-bottom: 1px solid #E5E7EB;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 24px;
  background: white;
  border-radius: 12px 12px 0 0;
}

.btn-back {
  background: none;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 1em;
  color: #4B5563;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-back:hover {
  color: #1F2937;
  background: #F3F4F8;
}

.project-title {
  margin: 0;
}

.project-title h2 {
  margin: 0 0 6px 0;
  color: #1F2937;
  font-weight: 600;
}

.project-title p {
  margin: 0;
  color: #4B5563;
  font-size: 0.95em;
}

.gantt-container {
  flex: 1;
  padding: 24px;
  background: white;
  border-radius: 0 0 12px 12px;
}

.empty-state {
  text-align: center;
  padding: 48px;
  grid-column: 1 / -1;
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
}

.empty-state h2 {
  color: #1F2937;
  margin-bottom: 12px;
}

.empty-state p {
  color: #4B5563;
  margin-bottom: 24px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-height: 90vh;
  overflow-y: auto;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.btn-primary {
  background: #6366F1;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(99, 102, 241, 0.15);
}

.btn-primary:hover {
  background: #4F46E5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.no-tasks {
  text-align: center;
  padding: 48px;
  background: white;
  border-radius: 12px;
}

.no-tasks p {
  color: #4B5563;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 20px;
  }

  .project-tiles {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    grid-template-columns: 1fr;
    gap: 12px;
    text-align: center;
  }
  
  .btn-back {
    justify-content: center;
  }
  
  .project-actions {
    justify-content: center;
  }
}
</style>
