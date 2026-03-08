from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alerts import Alert, UserAlertInteraction


class AlertsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_from_simulation(
        self,
        simulation_id: int,
        normalized_event_id: int,
        portfolio_profile_id: int | None,
        title: str,
        body: str | None = None,
        relevance_score: float | None = None,
    ) -> Alert:
        a = Alert(
            portfolio_profile_id=portfolio_profile_id,
            simulation_id=simulation_id,
            normalized_event_id=normalized_event_id,
            alert_type="simulation_complete",
            title=title,
            body=body,
            relevance_score=int(relevance_score * 100) if relevance_score is not None else None,
        )
        self.db.add(a)
        await self.db.flush()
        return a

    async def list_for_profile(self, portfolio_profile_id: int | None, limit: int = 50) -> list[Alert]:
        q = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        if portfolio_profile_id is not None:
            q = q.where(Alert.portfolio_profile_id == portfolio_profile_id)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def ack(self, alert_id: int, user_id: int | None = None) -> bool:
        r = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        if r.scalars().first() is None:
            return False
        self.db.add(UserAlertInteraction(alert_id=alert_id, user_id=user_id, action="ack"))
        await self.db.flush()
        return True
