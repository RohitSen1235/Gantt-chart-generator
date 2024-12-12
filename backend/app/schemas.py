from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Task(BaseModel):
    id: Optional[int] = None
    Task: str
    Responsibility: str
    Start_date: date
    End_Date: date
    progress: Optional[float] = 0
    dependencies: Optional[List[int]] = []

class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    tasks: List[Task] = []
    created_at: Optional[date] = None

class ProjectList(BaseModel):
    projects: List[Project]

class TaskList(BaseModel):
    tasks: List[Task]
