# MIVE — Technical Architecture

## 1. System Overview

MIVE is a closed-loop macro-financial intelligence platform. Data flows:

```
External Sources → Ingestion → Raw Store → Normalization → Normalized Events
       → Embeddings → Clustering → Themes (heat/trajectory)
       → Memory Retrieval (analogues) → Multi-Agent Debate → Consensus + Debater
       → Risk Chain → Valuation Adjustment → Alerts → Dashboard
```

All paths are portfolio-personalized via the Portfolio Profile engine.

## 2. Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| **ingestion** | Fetch from RSS/APIs, dedupe, persist raw documents, trigger normalization |
| **preprocessing** | Normalize raw → event schema, extract metadata, classify type/region/surprise |
| **embeddings** | Generate vector embeddings for events and historical events (provider abstraction) |
| **clustering** | HDBSCAN on rolling window, theme labels, heat score, trajectory |
| **memory** | Historical event archive, semantic + quantitative retrieval, top-k analogues |
| **agents** | Six personas + Debater, structured JSON output, evidence anchoring, validation |
| **orchestration** | Simulation pipeline: event → risk chain → agents → consensus, auto-trigger rules |
| **valuation** | Baseline FV, sensitivity matrix, macro-adjustment engine, narrative generator |
| **portfolios** | Profile CRUD, holdings, relevance scoring, persona presets |
| **alerts** | Alert creation from simulations/thresholds, ack, delivery |
| **analytics** | Agent track records, theme stats, relevance metrics |
| **api** | REST + WebSocket, auth stubs, rate limiting |
| **db** | SQLAlchemy models, session, migrations |
| **core** | Config, logging, provider factories, schemas |

## 3. Data Flow (Detail)

1. **Ingestion job** (scheduled): For each enabled source, fetch → hash → dedupe → insert `raw_documents`. Emit task: normalize(doc_id).
2. **Normalization**: Parse raw → `normalized_events` + `event_entities`, extract features → `event_market_features`. Emit: embed(event_id), cluster(trigger).
3. **Embedding job**: Compute embedding for event text → store in `event_embeddings` (pgvector).
4. **Clustering job** (periodic): Load recent event embeddings → HDBSCAN → update `themes`, `theme_event_links`, `theme_heat_snapshots`. Heat = f(velocity, sentiment_delta, proxy).
5. **Simulation** (trigger: manual or auto): Load event + profile → memory.retrieve(event) → risk_chain.generate() → agents.run_parallel() → debater.run() → consensus.aggregate() → persist `simulations`, `agent_runs`, `consensus_outputs` → valuation.adjust(watchlist) → alerts.create().
6. **Frontend**: Poll/WebSocket for events, themes, simulations; display Heat Map, LivePulse, Horizon View, Event Detail, Agent Track Record.

## 4. Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2, PostgreSQL 15+, pgvector, Redis, Dramatiq (or RQ), Pydantic, httpx, pandas, scikit-learn, hdbscan.
- **AI**: OpenAI-compatible API (LLM + embeddings), structured outputs, retries, validation.
- **Frontend**: React 18, TypeScript, Tailwind, Recharts, TanStack Query, WebSocket.
- **DevOps**: Docker Compose (app, postgres, redis, worker), Alembic migrations, .env.

## 5. Failure Handling

- Ingestion: retries with backoff, log failures, skip duplicate hash.
- Embeddings: on failure, store null and skip from clustering; optional retry later.
- Agents: validate JSON; on malformed, retry once or use repair prompt; flag unanchored.
- Memory: if no analogues above confidence, return empty with reason.
- Valuation: if missing sensitivity, use default coefficients.

## 6. Security and Compliance

- No buy/sell recommendations; disclaimers in UI and API.
- Secrets via env; no hardcoding.
- Audit log for simulation create and alert ack.
- Org/user scoping for portfolio and alert data (stubbed for MVP).
