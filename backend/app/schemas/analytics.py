from pydantic import BaseModel

class StageSummary(BaseModel):
    stage: int
    label: str
    count: int
    helped_count: int
    help_rate: float

class AnalyticsSummary(BaseModel):
    total_checkins: int
    total_recommendations: int
    total_outcomes: int
    completion_rate: float
    intervention_help_rate: float
    stage_breakdown: list[StageSummary]
