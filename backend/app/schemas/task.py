from typing import Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    urgency: int = Field(default=3, ge=1, le=5)
    importance: int = Field(default=3, ge=1, le=5)
    energy_required: int = Field(default=3, ge=1, le=5)
    estimated_minutes: int = Field(default=30)
    context: str = Field(default="any")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    urgency: Optional[int] = Field(default=None, ge=1, le=5)
    importance: Optional[int] = Field(default=None, ge=1, le=5)
    energy_required: Optional[int] = Field(default=None, ge=1, le=5)
    estimated_minutes: Optional[int] = None
    context: Optional[str] = None
    completed: Optional[bool] = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    urgency: int
    importance: int
    energy_required: int
    estimated_minutes: int
    context: str
    completed: bool

    model_config = {"from_attributes": True}
