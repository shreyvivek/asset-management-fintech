from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.portfolio import Watchlist, WatchlistItem
from app.services.valuation.service import ValuationService

router = APIRouter(prefix="/valuations", tags=["valuations"])


@router.get("/watchlist/{watchlist_id}")
async def get_watchlist_valuations(watchlist_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    if r.scalars().first() is None:
        raise HTTPException(404, "Watchlist not found")
    svc = ValuationService(db)
    return await svc.get_watchlist_valuations(watchlist_id)


@router.get("/{ticker}")
async def get_ticker_valuation(ticker: str, db: AsyncSession = Depends(get_db)):
    svc = ValuationService(db)
    base = await svc.get_baseline(ticker)
    if not base:
        raise HTTPException(404, "Ticker not found")
    fv, company_id = base
    sens = await svc.get_sensitivity(company_id)
    adjs = await svc.get_adjustments_for_ticker(ticker, limit=5)
    return {"ticker": ticker, "baseline_fv": fv, "sensitivity": sens, "recent_adjustments": [{"adjusted_fv": a.adjusted_fv, "delta_pct": a.delta_pct, "narrative": a.narrative} for a in adjs]}


@router.get("/{ticker}/adjustments")
async def get_ticker_adjustments(ticker: str, limit: int = Query(10, le=50), db: AsyncSession = Depends(get_db)):
    svc = ValuationService(db)
    adjs = await svc.get_adjustments_for_ticker(ticker, limit=limit)
    return [{"adjusted_fv": a.adjusted_fv, "delta_pct": a.delta_pct, "narrative": a.narrative, "created_at": a.created_at} for a in adjs]
