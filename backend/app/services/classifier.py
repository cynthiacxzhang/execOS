"""
Classifier: checkin dict → stage prediction

Stage signals:
  1 - Initiation Failure: high focus but low mood/energy, not overwhelmed
  2 - Decision Paralysis: scattered focus, moderate everything, anxiety
  3 - Overwhelm Freeze: high overwhelm + high anxiety, low energy
  4 - Urgency Dependency: low urgency feelings, procrastination pattern

Input shape (all keys required):
  mood: 1-5, focus: 1-5, energy: 1-5, overwhelm: 1-5, anxiety: 1-5

Output shape:
  {
    "stage": int (1-4),
    "confidence": float (0-1),
    "reasons": list[str],
    "stage_scores": {"1": float, "2": float, "3": float, "4": float}
  }
"""

def _normalize(value: int, low: int = 1, high: int = 5) -> float:
    """Map 1-5 scale to 0-1."""
    return (value - low) / (high - low)

def classify(checkin: dict) -> dict:
    mood = _normalize(checkin["mood"])
    focus = _normalize(checkin["focus"])
    energy = _normalize(checkin["energy"])
    overwhelm = _normalize(checkin["overwhelm"])
    anxiety = _normalize(checkin["anxiety"])

    scores = {}
    reasons = {}

    # Stage 1: Initiation Failure
    # Knows what to do, can't start. Moderate focus, low-mid energy, low overwhelm, low-mid anxiety
    s1 = 0.0
    s1_reasons = []
    if focus > 0.4:
        s1 += 0.3
        s1_reasons.append("has some focus but still stuck")
    if energy < 0.5:
        s1 += 0.3
        s1_reasons.append("low energy making activation hard")
    if overwhelm < 0.5:
        s1 += 0.2
        s1_reasons.append("not overwhelmed — task is clear")
    if mood < 0.4:
        s1 += 0.2
        s1_reasons.append("low mood reducing motivation to start")
    scores["1"] = round(s1, 3)
    reasons["1"] = s1_reasons

    # Stage 2: Decision Paralysis
    # Too many options, spinning. Low focus, moderate anxiety, moderate overwhelm
    s2 = 0.0
    s2_reasons = []
    if focus < 0.4:
        s2 += 0.35
        s2_reasons.append("scattered focus — can't pick a direction")
    if anxiety > 0.4 and anxiety < 0.8:
        s2 += 0.25
        s2_reasons.append("moderate anxiety from too many choices")
    if overwhelm > 0.3 and overwhelm < 0.7:
        s2 += 0.25
        s2_reasons.append("moderate overwhelm — tasks feel numerous")
    if energy > 0.3:
        s2 += 0.15
        s2_reasons.append("has energy but no direction")
    scores["2"] = round(s2, 3)
    reasons["2"] = s2_reasons

    # Stage 3: Overwhelm Freeze
    # Task feels too big. High overwhelm + high anxiety, low energy, low mood
    s3 = 0.0
    s3_reasons = []
    if overwhelm > 0.6:
        s3 += 0.35
        s3_reasons.append("high overwhelm — task feels crushing")
    if anxiety > 0.6:
        s3 += 0.30
        s3_reasons.append("high anxiety creating dread")
    if energy < 0.4:
        s3 += 0.20
        s3_reasons.append("depleted energy compounds freeze")
    if mood < 0.4:
        s3 += 0.15
        s3_reasons.append("low mood deepens the freeze")
    scores["3"] = round(s3, 3)
    reasons["3"] = s3_reasons

    # Stage 4: Urgency Dependency
    # Waits for deadline pressure. Decent mood/energy, low anxiety, but low focus (drifting)
    s4 = 0.0
    s4_reasons = []
    if mood > 0.4:
        s4 += 0.25
        s4_reasons.append("mood is okay — not suffering, just drifting")
    if energy > 0.4:
        s4 += 0.25
        s4_reasons.append("has energy but not deploying it")
    if anxiety < 0.4:
        s4 += 0.25
        s4_reasons.append("low anxiety — no urgency signal firing")
    if focus < 0.5:
        s4 += 0.25
        s4_reasons.append("unfocused without deadline pressure")
    scores["4"] = round(s4, 3)
    reasons["4"] = s4_reasons

    # Pick winner
    best_stage = max(scores, key=lambda k: scores[k])
    best_score = scores[best_stage]
    total = sum(scores.values()) or 1.0
    confidence = round(best_score / total, 3)

    return {
        "stage": int(best_stage),
        "confidence": confidence,
        "reasons": reasons[best_stage],
        "stage_scores": scores,
    }
