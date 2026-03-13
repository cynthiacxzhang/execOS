SCORING_WEIGHTS = {
    "urgency": 0.15,
    "importance": 0.25,
    "energy_match": 0.30,
    "duration_match": 0.20,
    "context_match": 0.10,
}

STAGE_THRESHOLDS = {
    1: 0.35,  # Initiation Failure
    2: 0.35,  # Decision Paralysis
    3: 0.35,  # Overwhelm Freeze
    4: 0.35,  # Urgency Dependency
}
