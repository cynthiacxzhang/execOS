from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class OutcomeCreate(BaseModel):
    recommendation_id: int
    task_id: int
    started: bool = False
    completed: bool = False
    helped: Optional[bool] = None
    notes: Optional[str] = None

class OutcomeRead(BaseModel):
    id: int
    recommendation_id: int
    task_id: int
    started: bool
    completed: bool
    helped: Optional[bool]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
