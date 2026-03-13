import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db
from app.schemas.recommendation import GenerateRequest, RecommendationRead, InterventionCard
from app.services.recommendations import generate_recommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("/generate", response_model=RecommendationRead, status_code=201)
def generate(payload: GenerateRequest, db: Session = Depends(get_db)):
    try:
        rec = generate_recommendation(payload.checkin_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return RecommendationRead(
        id=rec.id,
        checkin_id=rec.checkin_id,
        stage=rec.stage,
        confidence=rec.confidence,
        reasons=json.loads(rec.reasons),
        stage_scores=json.loads(rec.stage_scores),
        primary_task_id=rec.primary_task_id,
        backup_task_id=rec.backup_task_id,
        intervention=InterventionCard(
            title=rec.intervention_title,
            body=rec.intervention_body,
            action=rec.intervention_action,
        ),
        created_at=rec.created_at,
    )
