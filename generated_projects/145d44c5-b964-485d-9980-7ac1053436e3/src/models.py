from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# Data Model for Task Creation
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=100, example="Complete the project")
    description: Optional[str] = Field(None, max_length=500, example="Need to finish the backend and frontend by the end of the week")
    due_date: Optional[datetime] = Field(None, example="2023-12-31T23:59:59")

# Data Model for Task Update
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

# Data Model for Task in Response
class Task(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    completed: bool = Field(False)

    class Config:
        orm_mode = True

# Data Model for Listing Tasks Response
class TaskList(BaseModel):
    tasks: List[Task]