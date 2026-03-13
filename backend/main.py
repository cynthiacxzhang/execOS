from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import create_db_and_tables
from app.api import tasks, checkins, recommendations, outcomes, analytics

app = FastAPI(title="execOS ADHD Decision Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(tasks.router)
app.include_router(checkins.router)
app.include_router(recommendations.router)
app.include_router(outcomes.router)
app.include_router(analytics.router)

@app.get("/health")
def health():
    return {"status": "ok"}
