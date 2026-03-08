from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agents import AgentRun, AgentOutput, DebateSummary


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_agent_track_summary(self) -> list[dict]:
        r = await self.db.execute(
            select(AgentRun.agent_id, func.count(AgentRun.id).label("total"))
            .group_by(AgentRun.agent_id)
        )
        rows = r.all()
        out = []
        for agent_id, total in rows:
            r2 = await self.db.execute(
                select(func.count(AgentOutput.id))
                .select_from(AgentOutput)
                .join(AgentRun, AgentRun.id == AgentOutput.agent_run_id)
                .where(AgentRun.agent_id == agent_id, AgentOutput.is_unanchored == False)
            )
            anchored = (r2.scalar() or 0)
            out.append({
                "agent_id": agent_id,
                "total_runs": total,
                "anchored_count": anchored,
                "anchored_rate": round(anchored / total, 2) if total else 0,
            })
        return out

    async def get_debater_stats(self) -> dict:
        r = await self.db.execute(select(func.count(DebateSummary.id)).select_from(DebateSummary))
        total = r.scalar() or 0
        return {"total_debates": total, "debater_hit_rate": None}
