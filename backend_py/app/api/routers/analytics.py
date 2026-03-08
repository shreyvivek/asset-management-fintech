from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/agents")
async def get_agent_analytics(db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    return await svc.get_agent_track_summary()


@router.get("/debater")
async def get_debater_stats(db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    return await svc.get_debater_stats()
