from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.portfolio import Watchlist, WatchlistItem

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class AddItemBody(BaseModel):
    ticker: str


@router.get("")
async def list_watchlists(portfolio_profile_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Watchlist).where(Watchlist.portfolio_profile_id == portfolio_profile_id))
    wls = r.scalars().all()
    return [{"id": w.id, "name": w.name} for w in wls]


@router.post("")
async def create_watchlist(portfolio_profile_id: int, name: str = "Default", db: AsyncSession = Depends(get_db)):
    w = Watchlist(portfolio_profile_id=portfolio_profile_id, name=name)
    db.add(w)
    await db.flush()
    return {"id": w.id, "name": w.name}


@router.get("/{watchlist_id}/items")
async def get_watchlist_items(watchlist_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist_id))
    items = r.scalars().all()
    return [{"ticker": i.ticker} for i in items]


@router.post("/{watchlist_id}/items")
async def add_watchlist_item(watchlist_id: int, body: AddItemBody, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    if r.scalars().first() is None:
        raise HTTPException(404, "Watchlist not found")
    item = WatchlistItem(watchlist_id=watchlist_id, ticker=body.ticker)
    db.add(item)
    await db.flush()
    return {"ticker": body.ticker}
