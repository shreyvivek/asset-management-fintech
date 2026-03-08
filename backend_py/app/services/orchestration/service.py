from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models.events import NormalizedEvent
from app.models.themes import Theme, ThemeHeatSnapshot
from app.models.agents import Simulation
from app.services.agents.runner import AgentRunner


class OrchestrationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def should_auto_trigger_event(self, event: NormalizedEvent) -> tuple[bool, str]:
        """Returns (should_trigger, reason)."""
        if event.surprise_magnitude is not None and event.surprise_magnitude >= self.settings.auto_trigger_surprise_threshold_sd:
            return True, "auto_surprise"
        if event.tone_shift_score is not None and abs(event.tone_shift_score) >= 0.5:
            return True, "auto_tone_shift"
        return False, ""

    async def should_auto_trigger_theme(self, theme_id: int) -> tuple[bool, str]:
        r = await self.db.execute(
            select(ThemeHeatSnapshot).where(
                ThemeHeatSnapshot.theme_id == theme_id,
            ).order_by(ThemeHeatSnapshot.snapshot_at.desc()).limit(2)
        )
        snapshots = r.scalars().all()
        if len(snapshots) < 2:
            return False, ""
        curr, prev = snapshots[0], snapshots[1]
        if curr.heat_score >= self.settings.auto_trigger_heat_threshold:
            return True, "auto_heat"
        return False, ""

    async def cooldown_active(self, normalized_event_id: int) -> bool:
        since = datetime.utcnow() - timedelta(seconds=self.settings.simulation_cooldown_seconds)
        r = await self.db.execute(
            select(Simulation).where(
                and_(
                    Simulation.normalized_event_id == normalized_event_id,
                    Simulation.started_at >= since,
                )
            )
        )
        return r.scalars().first() is not None

    async def run_simulation(
        self,
        normalized_event_id: int,
        portfolio_profile_id: int | None = None,
        force: bool = False,
    ) -> int | None:
        if not force and await self.cooldown_active(normalized_event_id):
            return None
        runner = AgentRunner(self.db)
        return await runner.run_simulation(
            normalized_event_id,
            portfolio_profile_id=portfolio_profile_id,
            trigger_reason="manual" if force else "auto",
        )
