"""Run with: uv run python seed.py"""
from sqlmodel import Session
from app.db.session import engine, create_db_and_tables
from app.models.task import Task
from app.models.checkin import CheckIn

SAMPLE_TASKS = [
    Task(title="Write project proposal", description="Draft the Q3 initiative doc", urgency=4, importance=5, energy_required=4, estimated_minutes=90, context="desk"),
    Task(title="Reply to 3 emails", description="Clear inbox backlog", urgency=3, importance=3, energy_required=2, estimated_minutes=20, context="any"),
    Task(title="Review pull request", description="Code review for auth module", urgency=4, importance=4, energy_required=3, estimated_minutes=45, context="desk"),
    Task(title="15-min walk", description="Get outside for a reset", urgency=1, importance=3, energy_required=1, estimated_minutes=15, context="outside"),
    Task(title="Update task statuses", description="Quick status sweep in project tool", urgency=2, importance=2, energy_required=1, estimated_minutes=10, context="any"),
    Task(title="Read one article", description="Stay current — pick anything in Pocket", urgency=1, importance=2, energy_required=1, estimated_minutes=15, context="any"),
]

SAMPLE_CHECKIN = CheckIn(
    mood=2,
    focus=2,
    energy=2,
    overwhelm=4,
    anxiety=4,
    available_minutes=60,
    current_context="desk",
    notes="Feeling frozen, not sure where to start",
)

def seed():
    create_db_and_tables()
    with Session(engine) as db:
        for task in SAMPLE_TASKS:
            db.add(task)
        db.add(SAMPLE_CHECKIN)
        db.commit()
        print(f"Seeded {len(SAMPLE_TASKS)} tasks and 1 check-in.")

if __name__ == "__main__":
    seed()
