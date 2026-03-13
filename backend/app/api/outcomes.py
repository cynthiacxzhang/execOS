from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db
from app.models.outcome import Outcome
from app.schemas.outcome import OutcomeCreate, OutcomeRead

router = APIRouter(prefix="/outcomes", tags=["outcomes"])

@router.post("", response_model=OutcomeRead, status_code=201)
def log_outcome(payload: OutcomeCreate, db: Session = Depends(get_db)):
    outcome = Outcome(**payload.model_dump())
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome
