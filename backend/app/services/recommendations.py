import json
from sqlmodel import Session, select
from app.models.task import Task
from app.models.checkin import CheckIn
from app.models.recommendation import Recommendation
from app.services.classifier import classify
from app.services.ranking import rank_tasks
from app.services.interventions import get_intervention

def generate_recommendation(checkin_id: int, db: Session) -> Recommendation:
    checkin = db.get(CheckIn, checkin_id)
    if checkin is None:
        raise ValueError(f"CheckIn {checkin_id} not found")

    # Get incomplete tasks
    tasks = db.exec(select(Task).where(Task.completed == False)).all()
    if not tasks:
        raise ValueError("No incomplete tasks available to recommend")

    # Build plain dicts for pure functions
    checkin_dict = {
        "mood": checkin.mood,
        "focus": checkin.focus,
        "energy": checkin.energy,
        "overwhelm": checkin.overwhelm,
        "anxiety": checkin.anxiety,
        "available_minutes": checkin.available_minutes,
        "current_context": checkin.current_context,
    }
    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "urgency": t.urgency,
            "importance": t.importance,
            "energy_required": t.energy_required,
            "estimated_minutes": t.estimated_minutes,
            "context": t.context,
        }
        for t in tasks
    ]

    # Classify stage
    classification = classify(checkin_dict)

    # Rank tasks
    ranked = rank_tasks(task_dicts, checkin_dict)

    primary_task_id = ranked[0]["task_id"] if len(ranked) >= 1 else None
    backup_task_id = ranked[1]["task_id"] if len(ranked) >= 2 else None

    # Get intervention
    intervention = get_intervention(classification["stage"])

    rec = Recommendation(
        checkin_id=checkin_id,
        stage=classification["stage"],
        confidence=classification["confidence"],
        reasons=json.dumps(classification["reasons"]),
        stage_scores=json.dumps(classification["stage_scores"]),
        primary_task_id=primary_task_id,
        backup_task_id=backup_task_id,
        intervention_title=intervention["title"],
        intervention_body=intervention["body"],
        intervention_action=intervention["action"],
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
