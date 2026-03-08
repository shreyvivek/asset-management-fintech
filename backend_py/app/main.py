from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.deps import get_db
from app.api.routers import events, themes, simulations, portfolio, valuations, watchlist, alerts, analytics

app = FastAPI(title="MIVE", description="Macro-Intelligence & Valuation Engine")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(themes.router)
app.include_router(simulations.router)
app.include_router(portfolio.router)
app.include_router(valuations.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)
app.include_router(analytics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/me")
async def me():
    """Stub for auth; returns anonymous user for MVP."""
    return {"id": 1, "organization_id": 1}
