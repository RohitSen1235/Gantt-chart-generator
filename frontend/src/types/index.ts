export interface Task {
  id?: number
  Task: string
  Responsibility: string
  Start_date: string
  End_Date: string
  progress: number
  dependencies?: number[]
  parent_id?: number
  subtasks: Task[]
  is_subtask: boolean
}

export interface Project {
  id?: number
  name: string
  description?: string
  tasks: Task[]
  created_at?: string
}

export interface GanttChartData {
  tasks: Task[]
}

export interface ProjectList {
  projects: Project[]
}
