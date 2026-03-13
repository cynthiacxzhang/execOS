# execOS — ADHD Decision Agent

A closed-loop system that helps people with ADHD break out of task paralysis by predicting which paralysis stage they're in and recommending one concrete action.

## What it does

1. User submits a check-in (mood, focus, energy, overwhelm, anxiety)
2. System classifies which of 4 ADHD paralysis stages they're in
3. System ranks their task list by initiation likelihood (not just urgency)
4. System returns one primary task, one backup task, and one targeted intervention
5. User logs whether it helped

## Stack

- **Backend:** FastAPI, SQLModel, SQLite, Pydantic v2, Python 3.11+
- **Package manager:** uv

## Quickstart

```bash
cd backend
uv venv && uv pip install -e ".[dev]"
uv run python seed.py          # load sample tasks + check-in
uv run uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## Run tests

```bash
cd backend
uv run pytest app/tests/ -v
```

## The 4 paralysis stages

| Stage | Name | Pattern | Fix |
|-------|------|---------|-----|
| 1 | Initiation Failure | Knows what to do, can't start | Activation trick |
| 2 | Decision Paralysis | Too many options, spinning | Eliminate choices |
| 3 | Overwhelm Freeze | Task feels crushing, dread | Microscopic first step |
| 4 | Urgency Dependency | Waits for deadline pressure | Artificial urgency |

## Docs

- [`systemsdesign.md`](systemsdesign.md) — architecture and data flow
