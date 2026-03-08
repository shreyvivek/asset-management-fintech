# MIVE Repository Structure

```
mive/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── portfolio_profiles.py
│   │   │   │   ├── events.py
│   │   │   │   ├── themes.py
│   │   │   │   ├── simulations.py
│   │   │   │   ├── valuations.py
│   │   │   │   ├── watchlist.py
│   │   │   │   ├── alerts.py
│   │   │   │   └── analytics.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── providers.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── preprocessing/
│   │   │   ├── embeddings/
│   │   │   ├── clustering/
│   │   │   ├── memory/
│   │   │   ├── agents/
│   │   │   ├── orchestration/
│   │   │   ├── valuation/
│   │   │   ├── portfolios/
│   │   │   ├── alerts/
│   │   │   └── analytics/
│   │   ├── workers/
│   │   ├── prompts/
│   │   ├── utils/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── lib/
│       ├── hooks/
│       └── types/
├── data/
│   └── seed/
├── docs/
├── docker-compose.yml
├── .env.example
├── README.md
└── Makefile
```

Implementation uses `fintech/` as repo root; `mive` is the product name. Backend lives at `backend/` (Python), frontend at `frontend/` (React).
