from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.themes import Theme, ThemeEventLink, ThemeHeatSnapshot
from app.models.events import NormalizedEvent
from app.schemas.common import ThemeBrief, EventBrief

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=List[dict])
async def list_themes(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Theme))
    themes = r.scalars().all()
    out = []
    for t in themes:
        r2 = await db.execute(
            select(ThemeHeatSnapshot).where(ThemeHeatSnapshot.theme_id == t.id).order_by(ThemeHeatSnapshot.snapshot_at.desc()).limit(1)
        )
        snap = r2.scalars().first()
        out.append({
            "id": t.id,
            "slug": t.slug,
            "label": t.label,
            "heat_score": snap.heat_score if snap else None,
            "trajectory": snap.trajectory if snap else None,
        })
    return out


@router.get("/{theme_id}")
async def get_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = r.scalars().first()
    if not theme:
        raise HTTPException(404, "Theme not found")
    r2 = await db.execute(
        select(ThemeHeatSnapshot).where(ThemeHeatSnapshot.theme_id == theme_id).order_by(ThemeHeatSnapshot.snapshot_at.desc()).limit(1)
    )
    snap = r2.scalars().first()
    return {"id": theme.id, "slug": theme.slug, "label": theme.label, "heat_score": snap.heat_score if snap else None, "trajectory": snap.trajectory if snap else None}


@router.get("/{theme_id}/events", response_model=List[EventBrief])
async def get_theme_events(theme_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(NormalizedEvent)
        .join(ThemeEventLink, ThemeEventLink.normalized_event_id == NormalizedEvent.id)
        .where(ThemeEventLink.theme_id == theme_id)
        .order_by(NormalizedEvent.published_at.desc().nullslast())
        .limit(limit)
    )
    events = r.scalars().all()
    return [EventBrief.model_validate(e) for e in events]
