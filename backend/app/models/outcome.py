from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Outcome(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recommendation_id: int = Field(foreign_key="recommendation.id")
    task_id: int = Field(foreign_key="task.id")
    started: bool = Field(default=False)
    completed: bool = Field(default=False)
    helped: Optional[bool] = None       # did the intervention help?
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
