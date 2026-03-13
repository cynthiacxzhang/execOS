from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.db.session import get_db
from app.models.recommendation import Recommendation
from app.models.outcome import Outcome
from app.models.checkin import CheckIn
from app.schemas.analytics import AnalyticsSummary, StageSummary

STAGE_LABELS = {
    1: "Initiation Failure",
    2: "Decision Paralysis",
    3: "Overwhelm Freeze",
    4: "Urgency Dependency",
}

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    total_checkins = db.exec(select(func.count()).select_from(CheckIn)).one()
    total_recs = db.exec(select(func.count()).select_from(Recommendation)).one()

    outcomes = db.exec(select(Outcome)).all()
    total_outcomes = len(outcomes)

    completed = sum(1 for o in outcomes if o.completed)
    completion_rate = round(completed / total_outcomes, 3) if total_outcomes else 0.0

    helped = [o for o in outcomes if o.helped is not None]
    help_rate = round(sum(1 for o in helped if o.helped) / len(helped), 3) if helped else 0.0

    # Stage breakdown
    recs = db.exec(select(Recommendation)).all()
    stage_counts: dict[int, int] = {}
    for r in recs:
        stage_counts[r.stage] = stage_counts.get(r.stage, 0) + 1

    # Helped per stage: join outcomes to recs
    stage_helped: dict[int, int] = {}
    for o in outcomes:
        if o.helped:
            rec = db.get(Recommendation, o.recommendation_id)
            if rec:
                stage_helped[rec.stage] = stage_helped.get(rec.stage, 0) + 1

    stage_breakdown = []
    for stage in range(1, 5):
        count = stage_counts.get(stage, 0)
        helped_count = stage_helped.get(stage, 0)
        stage_breakdown.append(StageSummary(
            stage=stage,
            label=STAGE_LABELS[stage],
            count=count,
            helped_count=helped_count,
            help_rate=round(helped_count / count, 3) if count else 0.0,
        ))

    return AnalyticsSummary(
        total_checkins=total_checkins,
        total_recommendations=total_recs,
        total_outcomes=total_outcomes,
        completion_rate=completion_rate,
        intervention_help_rate=help_rate,
        stage_breakdown=stage_breakdown,
    )
