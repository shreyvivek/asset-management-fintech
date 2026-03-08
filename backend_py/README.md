# MIVE Backend (Python)

Macro-Intelligence & Valuation Engine — FastAPI backend: ingestion, clustering, memory, multi-agent debate, consensus, valuation, alerts.

## Stack

- Python 3.11+, FastAPI, SQLAlchemy 2 (async), PostgreSQL, Redis (optional), Pydantic
- Embeddings/LLM: OpenAI-compatible (mock when no key)
- Clustering: HDBSCAN; heat/trajectory formulas in code

## Local run

### 1. Environment

```bash
cp .env.example .env
# Edit .env: set DATABASE_URL, optionally OPENAI_API_KEY
```

### 2. Database

```bash
# Create DB (e.g. createdb mive) and user
psql -c "CREATE USER mive WITH PASSWORD 'mive';"
psql -c "CREATE DATABASE mive OWNER mive;"

# Migrate
cd backend_py && alembic upgrade head
```

### 3. Seed

```bash
python scripts/seed_db.py
```

### 4. Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- Events: `GET http://localhost:8000/events`
- Themes: `GET http://localhost:8000/themes`
- Manual ingest: `POST http://localhost:8000/events/ingest/manual` with `{"title": "...", "summary": "...", "event_type": "data_release"}`
- Trigger simulation: `POST http://localhost:8000/events/{event_id}/simulate` (optional `?portfolio_profile_id=1&force=true`)

### 5. Pipeline (ingestion → embeddings → clustering)

```bash
python scripts/run_pipeline.py
```

Run after seed to embed historical events so analogue retrieval works. Requires DB and (for real embeddings) `OPENAI_API_KEY` or mock will be used.

## Tests

```bash
pytest tests/ -v
```

- `test_clustering.py`: heat_score, trajectory
- `test_consensus.py`: consensus aggregation
- `test_valuation.py`: macro delta_pct formula
- `test_api_smoke.py`: health, me, events/themes (may 500 if DB not set)

## API summary

| Area | Endpoints |
|------|-----------|
| Events | GET /events, GET /events/{id}, POST /events/ingest/manual, POST /events/{id}/simulate, GET /events/{id}/analogues |
| Themes | GET /themes, GET /themes/{id}, GET /themes/{id}/events |
| Simulations | GET /simulations, GET /simulations/{id}, GET /simulations/{id}/agents, GET /simulations/{id}/consensus |
| Portfolio | GET/POST/PATCH /portfolio-profiles, GET /portfolio-profiles/{id} |
| Watchlist | GET/POST /watchlist, GET/POST /watchlist/{id}/items |
| Valuations | GET /valuations/watchlist/{id}, GET /valuations/{ticker}, GET /valuations/{ticker}/adjustments |
| Alerts | GET /alerts, POST /alerts/{id}/ack |
| Analytics | GET /analytics/agents, GET /analytics/debater |

## Limitations (MVP)

- Auth: stub only (`/me` returns fixed user).
- pgvector: embeddings stored as JSON if pgvector not installed.
- Agent track record: structure in place; full evaluation job vs market snapshots can be added later.
