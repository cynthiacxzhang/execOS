from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class CheckIn(SQLModel, table=True):
    __tablename__ = "checkin"
    id: Optional[int] = Field(default=None, primary_key=True)
    mood: int = Field(ge=1, le=5)           # 1=very low, 5=very high
    focus: int = Field(ge=1, le=5)          # 1=scattered, 5=laser
    energy: int = Field(ge=1, le=5)         # 1=depleted, 5=high
    overwhelm: int = Field(ge=1, le=5)      # 1=none, 5=paralyzed
    anxiety: int = Field(ge=1, le=5)        # 1=calm, 5=panic
    available_minutes: int = Field(default=60)
    current_context: str = Field(default="any")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
