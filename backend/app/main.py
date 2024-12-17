from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import timedelta, date
import os
import json
from app.schemas import Task, TaskList, Project, ProjectList
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECTS_FILE = "projects.json"

def validate_task_dates(task: Task, parent_task: Task = None) -> bool:
    """Validate task dates against parent task if it exists"""
    if parent_task:
        if task.Start_date < parent_task.Start_date or task.End_Date > parent_task.End_Date:
            return False
    return task.Start_date <= task.End_Date

def calculate_task_progress(task: Task) -> float:
    """Calculate task progress including subtasks"""
    if not task.subtasks:
        return task.progress or 0
    
    subtask_progress = sum(calculate_task_progress(subtask) for subtask in task.subtasks)
    return subtask_progress / len(task.subtasks)

def validate_and_process_tasks(tasks: list[Task], parent: Task = None) -> list[Task]:
    """Recursively validate and process tasks and their subtasks"""
    processed_tasks = []
    
    for task in tasks:
        # Validate dates
        if not validate_task_dates(task, parent):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date range for task: {task.Task}"
            )
        
        # Process subtasks if they exist
        if task.subtasks:
            task.subtasks = validate_and_process_tasks(task.subtasks, task)
            # Update progress based on subtasks
            task.progress = calculate_task_progress(task)
        
        processed_tasks.append(task)
    
    return processed_tasks

def load_projects() -> list[Project]:
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            data = json.load(f)
            return [Project(**project) for project in data]
    return []

def save_projects(projects: list[Project]):
    projects_data = []
    for project in projects:
        project_dict = project.model_dump()
        if project_dict.get('created_at'):
            project_dict['created_at'] = project_dict['created_at'].isoformat()
        
        def process_tasks(tasks):
            for task in tasks:
                task['Start_date'] = task['Start_date'].isoformat()
                task['End_Date'] = task['End_Date'].isoformat()
                if task.get('subtasks'):
                    process_tasks(task['subtasks'])
            return tasks
        
        project_dict['tasks'] = process_tasks(project_dict.get('tasks', []))
        projects_data.append(project_dict)
    
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects_data, f, indent=2)

def create_gantt_chart(tasks: list[Task]) -> str:
    # Flatten tasks for visualization
    def flatten_tasks(task_list: list[Task], level: int = 0) -> list[tuple[Task, int]]:
        flattened = []
        for task in task_list:
            flattened.append((task, level))
            if task.subtasks:
                flattened.extend(flatten_tasks(task.subtasks, level + 1))
        return flattened

    flat_tasks = flatten_tasks(tasks)
    
    # Sort tasks by start date
    flat_tasks.sort(key=lambda x: x[0].Start_date, reverse=True)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, max(8, len(flat_tasks) * 0.5)))

    # Assign different colors to responsibilities
    responsibilities = set(task.Responsibility for task, _ in flat_tasks)
    colors = plt.colormaps["tab20c"](np.linspace(0, 1, len(responsibilities)))

    # Convert dates to matplotlib format
    start_dates = [mdates.date2num(task.Start_date) for task, _ in flat_tasks]
    end_dates = [mdates.date2num(task.End_Date) for task, _ in flat_tasks]

    # Set the y-axis limits
    ax.set_ylim(0, len(flat_tasks))

    # Set the y-ticks and labels with indentation
    yticks = range(len(flat_tasks))
    ytick_labels = [f"{'  ' * level}{task.Task}" for task, level in flat_tasks]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels)

    # Plot the tasks
    for i, (task, level) in enumerate(flat_tasks):
        start_date = mdates.date2num(task.Start_date)
        end_date = mdates.date2num(task.End_Date)
        duration = end_date - start_date

        responsibility = task.Responsibility
        color = colors[list(responsibilities).index(responsibility)]
        alpha = 0.7 if task.is_subtask else 1.0

        # Task bar
        ax.broken_barh(
            [(start_date, duration)],
            (i - 0.3, 0.6),
            facecolors=color,
            edgecolor='black',
            alpha=alpha
        )

        # Progress bar
        if task.progress > 0:
            progress_width = duration * (task.progress / 100)
            ax.broken_barh(
                [(start_date, progress_width)],
                (i - 0.3, 0.6),
                facecolors='green',
                alpha=0.5
            )

    # Set the x-axis limits and ticks
    min_date = min(start_dates)
    max_date = max(end_dates)
    ax.set_xlim(min_date - 1, max_date + 1)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    # Add vertical lines for each day
    for date in mdates.drange(
        mdates.num2date(min_date),
        mdates.num2date(max_date) + timedelta(days=1),
        timedelta(days=1)
    ):
        ax.axvline(date, color='gray', linestyle='--', linewidth=0.5)

    # Set the chart title and labels
    plt.title("Project Timeline")
    plt.xlabel("Timeline")
    plt.ylabel("Task")

    # Create a legend for responsibilities
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i, r in enumerate(responsibilities)]
    labels = list(responsibilities)
    plt.legend(handles, labels, loc="upper right")

    # Adjust the layout and padding
    plt.tight_layout()

    # Save the plot
    chart_path = "gantt_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()

    return chart_path

# Project endpoints
@app.get("/projects/", response_model=ProjectList)
async def get_projects():
    projects = load_projects()
    return ProjectList(projects=projects)

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: int):
    projects = load_projects()
    for project in projects:
        if project.id == project_id:
            return project
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/projects/", response_model=Project)
async def create_project(project: Project):
    try:
        logger.info(f"Received project data: {project.model_dump()}")
        
        # Process dates recursively
        def process_dates(tasks: list[Task]):
            for task in tasks:
                if isinstance(task.Start_date, str):
                    task.Start_date = date.fromisoformat(task.Start_date)
                if isinstance(task.End_Date, str):
                    task.End_Date = date.fromisoformat(task.End_Date)
                if task.subtasks:
                    process_dates(task.subtasks)
        
        process_dates(project.tasks)
        
        # Validate and process all tasks
        project.tasks = validate_and_process_tasks(project.tasks)
        
        projects = load_projects()
        # Generate new ID
        project.id = max([p.id or 0 for p in projects], default=0) + 1
        project.created_at = date.today()
        
        logger.info(f"Processed project data: {project.model_dump()}")
        
        projects.append(project)
        save_projects(projects)
        return project
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: int, updated_project: Project):
    try:
        logger.info(f"Updating project {project_id} with data: {updated_project.model_dump()}")
        
        # Process dates recursively
        def process_dates(tasks: list[Task]):
            for task in tasks:
                if isinstance(task.Start_date, str):
                    task.Start_date = date.fromisoformat(task.Start_date)
                if isinstance(task.End_Date, str):
                    task.End_Date = date.fromisoformat(task.End_Date)
                if task.subtasks:
                    process_dates(task.subtasks)
        
        process_dates(updated_project.tasks)
        
        # Validate and process all tasks
        updated_project.tasks = validate_and_process_tasks(updated_project.tasks)
        
        projects = load_projects()
        for i, project in enumerate(projects):
            if project.id == project_id:
                updated_project.id = project_id
                updated_project.created_at = project.created_at
                projects[i] = updated_project
                save_projects(projects)
                return updated_project
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    projects = load_projects()
    projects = [p for p in projects if p.id != project_id]
    save_projects(projects)
    return {"message": "Project deleted"}

# Chart endpoints
@app.post("/generate-chart/")
async def generate_chart(task_list: TaskList):
    try:
        chart_path = create_gantt_chart(task_list.tasks)
        return {"message": "Chart generated successfully", "chart_path": chart_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-chart/")
async def download_chart():
    chart_path = "gantt_chart.png"
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(chart_path, media_type="image/png", filename="gantt_chart.png")

@app.get("/")
async def root():
    return {"message": "Gantt Chart Generator API"}
