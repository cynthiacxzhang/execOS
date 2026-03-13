from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime

class GenerateRequest(BaseModel):
    checkin_id: int

class InterventionCard(BaseModel):
    title: str
    body: str
    action: str

class RecommendationRead(BaseModel):
    id: int
    checkin_id: int
    stage: int
    confidence: float
    reasons: list[str]
    stage_scores: dict[str, float]
    primary_task_id: Optional[int]
    backup_task_id: Optional[int]
    intervention: InterventionCard
    created_at: datetime

    model_config = {"from_attributes": True}
