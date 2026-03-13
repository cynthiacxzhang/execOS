"""
Ranker: score_task(task_dict, checkin_dict) → scored task dict

Optimizes for initiation likelihood, not just urgency.
"""
from app.core.config import SCORING_WEIGHTS

def _normalize(value: int, low: int = 1, high: int = 5) -> float:
    return (value - low) / (high - low)

def score_task(task: dict, checkin: dict) -> dict:
    energy = _normalize(checkin["energy"])
    available_minutes = checkin.get("available_minutes", 60)
    current_context = checkin.get("current_context", "any")

    urgency_score = _normalize(task["urgency"])
    importance_score = _normalize(task["importance"])

    # Energy match: prefer tasks whose energy_required matches user's current energy
    task_energy = _normalize(task["energy_required"])
    energy_diff = abs(energy - task_energy)
    energy_match = 1.0 - energy_diff  # 1 = perfect match

    # Duration match: prefer tasks that fit in available time
    task_mins = task.get("estimated_minutes", 30)
    if task_mins <= available_minutes:
        duration_match = 1.0
    elif task_mins <= available_minutes * 1.5:
        duration_match = 0.5
    else:
        duration_match = 0.0

    # Context match
    task_context = task.get("context", "any")
    if task_context == "any" or current_context == "any" or task_context == current_context:
        context_match = 1.0
    else:
        context_match = 0.0

    sub_scores = {
        "urgency": round(urgency_score, 3),
        "importance": round(importance_score, 3),
        "energy_match": round(energy_match, 3),
        "duration_match": round(duration_match, 3),
        "context_match": round(context_match, 3),
    }

    total = sum(
        sub_scores[k] * SCORING_WEIGHTS[k]
        for k in SCORING_WEIGHTS
    )

    return {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "sub_scores": sub_scores,
        "total_score": round(total, 4),
    }

def rank_tasks(tasks: list[dict], checkin: dict) -> list[dict]:
    scored = [score_task(t, checkin) for t in tasks]
    return sorted(scored, key=lambda x: x["total_score"], reverse=True)
