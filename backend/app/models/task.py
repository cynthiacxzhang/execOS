from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    urgency: int = Field(default=3, ge=1, le=5)      # 1-5
    importance: int = Field(default=3, ge=1, le=5)   # 1-5
    energy_required: int = Field(default=3, ge=1, le=5)  # 1=low, 5=high
    estimated_minutes: int = Field(default=30)
    context: str = Field(default="any")  # "desk", "phone", "outside", "any"
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
