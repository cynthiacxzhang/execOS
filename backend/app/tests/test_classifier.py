import pytest
from app.services.classifier import classify

def _checkin(mood=3, focus=3, energy=3, overwhelm=3, anxiety=3):
    return {"mood": mood, "focus": focus, "energy": energy, "overwhelm": overwhelm, "anxiety": anxiety}

def test_returns_required_keys():
    result = classify(_checkin())
    assert "stage" in result
    assert "confidence" in result
    assert "reasons" in result
    assert "stage_scores" in result

def test_stage_is_1_to_4():
    result = classify(_checkin())
    assert result["stage"] in (1, 2, 3, 4)

def test_confidence_is_between_0_and_1():
    result = classify(_checkin())
    assert 0.0 <= result["confidence"] <= 1.0

def test_stage_scores_has_all_4():
    result = classify(_checkin())
    assert set(result["stage_scores"].keys()) == {"1", "2", "3", "4"}

def test_overwhelm_freeze_pattern():
    # High overwhelm + high anxiety + low energy → stage 3
    result = classify(_checkin(mood=1, focus=2, energy=1, overwhelm=5, anxiety=5))
    assert result["stage"] == 3

def test_urgency_dependency_pattern():
    # Good mood/energy, low anxiety, low focus → stage 4
    result = classify(_checkin(mood=4, focus=2, energy=4, overwhelm=2, anxiety=1))
    assert result["stage"] == 4

def test_decision_paralysis_pattern():
    # Low focus, moderate anxiety and overwhelm → stage 2
    result = classify(_checkin(mood=3, focus=1, energy=3, overwhelm=3, anxiety=3))
    assert result["stage"] == 2

def test_reasons_is_list_of_strings():
    result = classify(_checkin())
    assert isinstance(result["reasons"], list)
    assert all(isinstance(r, str) for r in result["reasons"])
