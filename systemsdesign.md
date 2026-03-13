# Systems Design — execOS Backend

## Overview

The backend is a rules-based decision engine for ADHD task paralysis. It takes a user check-in, classifies their current paralysis state, ranks available tasks by initiation likelihood, and returns a targeted intervention. Every recommendation loop is logged so outcomes can inform future improvements.

---

## Folder Layout

```
backend/
  app/
    api/              Route handlers — thin, delegate to services
      tasks.py
      checkins.py
      recommendations.py
      outcomes.py
      analytics.py
    core/
      config.py       SCORING_WEIGHTS and STAGE_THRESHOLDS (single source of truth)
    models/           SQLModel table definitions (DB schema)
      task.py
      checkin.py
      recommendation.py
      outcome.py
    schemas/          Pydantic request/response shapes (API contract)
      task.py
      checkin.py
      recommendation.py
      outcome.py
      analytics.py
    services/         Business logic
      classifier.py      Pure fn: checkin dict → stage prediction
      ranking.py         Pure fn: task + checkin → initiation score
      interventions.py   Pure fn: stage int → intervention card
      recommendations.py Orchestrator: calls all 3, writes to DB
    db/
      session.py      SQLite engine + get_db dependency
    tests/
      test_classifier.py
      test_ranking.py
      test_recommendations.py
  main.py             FastAPI app, CORS, router registration, startup hook
  seed.py             Sample data for local dev
  pyproject.toml
```

---

## Data Flow

```
POST /checkins
  → stores CheckIn row

POST /recommendations/generate  { checkin_id }
  → loads CheckIn from DB
  → loads incomplete Tasks from DB
  → classifier.classify(checkin_dict)        → stage, confidence, reasons
  → ranking.rank_tasks(task_dicts, checkin)  → sorted scored tasks
  → interventions.get_intervention(stage)    → intervention card
  → writes Recommendation row to DB
  → returns full recommendation to client

POST /outcomes
  → stores Outcome row (started, completed, helped)

GET /analytics/summary
  → aggregates stage counts + help rates from Recommendation + Outcome tables
```

---

## Services Design

### classifier.py — Stage Classifier

Pure function. No imports from DB or models. Takes a raw dict, returns a dict.

Each of the 4 stages accumulates evidence from check-in signals. The stage with the highest raw score wins. Confidence is `winner_score / sum(all_scores)`.

**Why rules-based first:** fast to iterate, fully explainable, no training data needed. The input/output contract is designed so `classify(checkin_dict)` can be swapped for an sklearn model later with zero changes to the orchestrator.

| Stage | Key signals |
|-------|------------|
| 1 — Initiation Failure | Some focus, low energy, low overwhelm, low mood |
| 2 — Decision Paralysis | Low focus, moderate anxiety + overwhelm, has energy |
| 3 — Overwhelm Freeze | High overwhelm, high anxiety, low energy |
| 4 — Urgency Dependency | OK mood + energy, low anxiety, low focus |

### ranking.py — Task Ranker

Pure function. Scores each task against the current check-in using weighted sub-scores. Optimizes for **initiation likelihood**, not urgency.

| Weight | Sub-score | Why |
|--------|-----------|-----|
| 0.30 | energy_match | Mismatched energy is the #1 reason tasks don't get started |
| 0.25 | importance | Long-term value matters |
| 0.20 | duration_match | Tasks that fit available time are actually startable |
| 0.15 | urgency | Real but deliberately de-emphasized |
| 0.10 | context_match | Environment fit (desk vs. phone vs. outside) |

Weights live in `core/config.py` — easy to tune without touching logic.

### interventions.py — Intervention Cards

Pure function. Static lookup by stage. Each card has a `title`, `body` (why this works), and `action` (one concrete thing to do right now).

### recommendations.py — Orchestrator

The only service that touches the database. Loads data, converts to plain dicts, calls the three pure services, writes one `Recommendation` row. All other services are testable with just dicts.

---

## Database Schema

```
Task
  id, title, description
  urgency (1-5), importance (1-5), energy_required (1-5)
  estimated_minutes, context, completed, created_at

CheckIn
  id, mood, focus, energy, overwhelm, anxiety (all 1-5)
  available_minutes, current_context, notes, created_at

Recommendation
  id, checkin_id → CheckIn
  stage (1-4), confidence, reasons (JSON), stage_scores (JSON)
  primary_task_id → Task, backup_task_id → Task
  intervention_title, intervention_body, intervention_action
  created_at

Outcome
  id, recommendation_id → Recommendation, task_id → Task
  started, completed, helped (bool|null), notes, created_at
```

---

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List all tasks |
| PATCH | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| POST | `/checkins` | Submit a check-in |
| GET | `/checkins` | List check-ins |
| POST | `/recommendations/generate` | Run the full pipeline |
| POST | `/outcomes` | Log outcome for a recommendation |
| GET | `/analytics/summary` | Stage breakdown + help rates |
| GET | `/health` | Health check |

---

## Key Design Decisions

**Services are pure functions.** Only `recommendations.py` touches the DB. Everything else takes dicts and returns dicts. This makes unit testing trivial and keeps business logic portable.

**Rules-based classifier, ML-ready interface.** The `classify(dict) → dict` contract is stable. A future sklearn or LLM-based classifier just needs to match that shape.

**Energy match is the top ranking weight.** Most ADHD task selection advice focuses on urgency/importance (Eisenhower matrix). This system de-emphasizes urgency and prioritizes whether the task fits the user's *current* state — because a theoretically important task you can't start is worse than a smaller task you actually do.

**JSON columns for reasons/scores.** `Recommendation.reasons` and `stage_scores` are stored as JSON strings in SQLite. Simple for an MVP; easy to migrate to a proper JSON column or separate table later.
