from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CheckInCreate(BaseModel):
    mood: int = Field(ge=1, le=5)
    focus: int = Field(ge=1, le=5)
    energy: int = Field(ge=1, le=5)
    overwhelm: int = Field(ge=1, le=5)
    anxiety: int = Field(ge=1, le=5)
    available_minutes: int = Field(default=60)
    current_context: str = Field(default="any")
    notes: Optional[str] = None

class CheckInRead(BaseModel):
    id: int
    mood: int
    focus: int
    energy: int
    overwhelm: int
    anxiety: int
    available_minutes: int
    current_context: str
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
