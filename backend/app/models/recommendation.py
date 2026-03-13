from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Recommendation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    checkin_id: int = Field(foreign_key="checkin.id")
    stage: int                         # 1-4
    confidence: float
    reasons: str                       # JSON-serialized list
    stage_scores: str                  # JSON-serialized dict
    primary_task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    backup_task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    intervention_title: str
    intervention_body: str
    intervention_action: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
