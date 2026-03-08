from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.events import NormalizedEvent
from app.schemas.common import EventBrief
from app.services.memory.service import MemoryService
from app.services.orchestration.service import OrchestrationService
from app.services.preprocessing.service import PreprocessingService

router = APIRouter(prefix="/events", tags=["events"])


class ManualIngestBody(BaseModel):
    title: str
    summary: str | None = None
    event_type: str = "data_release"
    region: str | None = None


@router.post("/ingest/manual")
async def manual_ingest(body: ManualIngestBody, db: AsyncSession = Depends(get_db)):
    ev = NormalizedEvent(
        title=body.title,
        summary=body.summary,
        source_credibility="manual",
        event_type=body.event_type,
        region=body.region,
    )
    db.add(ev)
    await db.flush()
    return {"id": ev.id, "title": ev.title}


@router.get("", response_model=List[EventBrief])
async def list_events(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    event_type: str | None = None,
    region: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(NormalizedEvent).order_by(NormalizedEvent.published_at.desc().nullslast()).offset(offset).limit(limit)
    if event_type:
        q = q.where(NormalizedEvent.event_type == event_type)
    if region:
        q = q.where(NormalizedEvent.region == region)
    r = await db.execute(q)
    events = r.scalars().all()
    return [EventBrief.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=EventBrief)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(NormalizedEvent).where(NormalizedEvent.id == event_id))
    event = r.scalars().first()
    if not event:
        raise HTTPException(404, "Event not found")
    return EventBrief.model_validate(event)


@router.post("/{event_id}/simulate")
async def trigger_simulation(
    event_id: int,
    portfolio_profile_id: int | None = None,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
):
    orch = OrchestrationService(db)
    sim_id = await orch.run_simulation(event_id, portfolio_profile_id=portfolio_profile_id, force=force)
    if sim_id is None:
        raise HTTPException(429, "Cooldown active or event not found")
    return {"simulation_id": sim_id}


@router.get("/{event_id}/analogues")
async def get_analogues(event_id: int, top_k: int = Query(3, le=10), db: AsyncSession = Depends(get_db)):
    mem = MemoryService(db)
    results = await mem.retrieve_analogues(event_id, top_k=top_k)
    return [{"historical_event_id": a.historical_event_id, "title": a.title, "event_date": a.event_date, "outcome_24h": a.outcome_24h, "outcome_1w": a.outcome_1w, "combined_score": a.combined_score, "reason": a.reason} for a in results]
