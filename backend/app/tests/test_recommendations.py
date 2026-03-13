import pytest
from unittest.mock import MagicMock, patch
from app.services.recommendations import generate_recommendation

def _mock_checkin():
    c = MagicMock()
    c.mood = 2; c.focus = 2; c.energy = 2; c.overwhelm = 4; c.anxiety = 4
    c.available_minutes = 60; c.current_context = "desk"
    return c

def _mock_task(id, title="Task", urgency=3, importance=3, energy_required=2, estimated_minutes=30, context="any"):
    t = MagicMock()
    t.id = id; t.title = title; t.urgency = urgency; t.importance = importance
    t.energy_required = energy_required; t.estimated_minutes = estimated_minutes; t.context = context
    t.completed = False
    return t

def test_generate_raises_if_no_checkin():
    db = MagicMock()
    db.get.return_value = None
    with pytest.raises(ValueError, match="not found"):
        generate_recommendation(999, db)

def test_generate_raises_if_no_tasks():
    db = MagicMock()
    db.get.return_value = _mock_checkin()
    db.exec.return_value.all.return_value = []
    with pytest.raises(ValueError, match="No incomplete tasks"):
        generate_recommendation(1, db)

def test_generate_returns_recommendation_with_stage():
    db = MagicMock()
    db.get.return_value = _mock_checkin()
    db.exec.return_value.all.return_value = [_mock_task(1), _mock_task(2)]

    # Capture what gets added to db
    added = []
    db.add.side_effect = lambda obj: added.append(obj)
    db.refresh.side_effect = lambda obj: None

    result = generate_recommendation(1, db)
    assert len(added) == 1
    rec = added[0]
    assert rec.stage in (1, 2, 3, 4)
    assert 0.0 <= rec.confidence <= 1.0
    assert rec.primary_task_id == 1 or rec.primary_task_id == 2
