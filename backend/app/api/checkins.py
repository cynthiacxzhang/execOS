from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.checkin import CheckIn
from app.schemas.checkin import CheckInCreate, CheckInRead

router = APIRouter(prefix="/checkins", tags=["checkins"])

@router.post("", response_model=CheckInRead, status_code=201)
def create_checkin(payload: CheckInCreate, db: Session = Depends(get_db)):
    checkin = CheckIn(**payload.model_dump())
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@router.get("", response_model=list[CheckInRead])
def list_checkins(db: Session = Depends(get_db)):
    return db.exec(select(CheckIn)).all()
