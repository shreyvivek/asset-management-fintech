from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.alerts.service import AlertsService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(portfolio_profile_id: int | None = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    svc = AlertsService(db)
    alerts = await svc.list_for_profile(portfolio_profile_id=portfolio_profile_id, limit=limit)
    return [{"id": a.id, "title": a.title, "body": a.body, "alert_type": a.alert_type, "created_at": a.created_at} for a in alerts]


@router.post("/{alert_id}/ack")
async def ack_alert(alert_id: int, user_id: int | None = None, db: AsyncSession = Depends(get_db)):
    svc = AlertsService(db)
    ok = await svc.ack(alert_id, user_id=user_id)
    if not ok:
        raise HTTPException(404, "Alert not found")
    await db.flush()
    return {"ok": True}
