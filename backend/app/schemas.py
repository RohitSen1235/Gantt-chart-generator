from pydantic import BaseModel, validator
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
    parent_id: Optional[int] = None
    subtasks: List['Task'] = []
    is_subtask: bool = False

    @validator('End_Date')
    def end_date_must_be_after_start(cls, v, values):
        if 'Start_date' in values and v < values['Start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('progress')
    def progress_must_be_between_0_and_100(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Progress must be between 0 and 100')
        return v

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

# This is needed for the forward reference in Task.subtasks
Task.update_forward_refs()
