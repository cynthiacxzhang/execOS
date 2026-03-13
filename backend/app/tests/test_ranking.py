import pytest
from app.services.ranking import score_task, rank_tasks

def _task(id=1, title="Test Task", urgency=3, importance=3, energy_required=3, estimated_minutes=30, context="any"):
    return {"id": id, "title": title, "urgency": urgency, "importance": importance,
            "energy_required": energy_required, "estimated_minutes": estimated_minutes, "context": context}

def _checkin(energy=3, available_minutes=60, current_context="any", **kwargs):
    base = {"mood": 3, "focus": 3, "energy": energy, "overwhelm": 3, "anxiety": 3,
            "available_minutes": available_minutes, "current_context": current_context}
    base.update(kwargs)
    return base

def test_score_task_returns_required_keys():
    result = score_task(_task(), _checkin())
    assert "task_id" in result
    assert "total_score" in result
    assert "sub_scores" in result

def test_total_score_between_0_and_1():
    result = score_task(_task(), _checkin())
    assert 0.0 <= result["total_score"] <= 1.0

def test_energy_match_boosts_score():
    # Task energy_required=1 matches user energy=1 → should score higher than energy=5 task
    low_energy_task = _task(energy_required=1)
    high_energy_task = _task(energy_required=5)
    checkin = _checkin(energy=1)
    low_score = score_task(low_energy_task, checkin)["total_score"]
    high_score = score_task(high_energy_task, checkin)["total_score"]
    assert low_score > high_score

def test_task_that_fits_in_time_scores_higher():
    short_task = _task(estimated_minutes=20)
    long_task = _task(estimated_minutes=120)
    checkin = _checkin(available_minutes=30)
    assert score_task(short_task, checkin)["total_score"] > score_task(long_task, checkin)["total_score"]

def test_context_mismatch_penalizes():
    desk_task = _task(context="desk")
    any_task = _task(context="any")
    checkin = _checkin(current_context="outside")
    assert score_task(any_task, checkin)["total_score"] > score_task(desk_task, checkin)["total_score"]

def test_rank_tasks_returns_sorted_descending():
    tasks = [_task(id=1, urgency=1, importance=1), _task(id=2, urgency=5, importance=5)]
    ranked = rank_tasks(tasks, _checkin())
    assert ranked[0]["total_score"] >= ranked[1]["total_score"]
