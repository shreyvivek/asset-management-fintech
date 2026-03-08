from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.portfolio import PortfolioProfile, Holding, Watchlist, WatchlistItem
from app.models.events import NormalizedEvent


class PortfolioService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, profile_id: int) -> PortfolioProfile | None:
        r = await self.db.execute(select(PortfolioProfile).where(PortfolioProfile.id == profile_id))
        return r.scalars().first()

    async def list_profiles(self, organization_id: int | None = None) -> list[PortfolioProfile]:
        q = select(PortfolioProfile)
        if organization_id is not None:
            q = q.where(PortfolioProfile.organization_id == organization_id)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def create_profile(
        self,
        name: str,
        mandate_persona: str,
        organization_id: int | None = None,
        asset_class_weights: dict | None = None,
        geography_exposure: dict | None = None,
        sector_exposures: dict | None = None,
    ) -> PortfolioProfile:
        p = PortfolioProfile(
            organization_id=organization_id,
            name=name,
            mandate_persona=mandate_persona,
            asset_class_weights=asset_class_weights or {},
            geography_exposure=geography_exposure or {},
            sector_exposures=sector_exposures or {},
        )
        self.db.add(p)
        await self.db.flush()
        return p

    async def relevance_score(
        self,
        normalized_event: NormalizedEvent,
        profile: PortfolioProfile,
    ) -> float:
        score = 0.0
        event_region = (normalized_event.region or "").lower()
        event_types = {normalized_event.event_type}
        ac_weights = profile.asset_class_weights or {}
        geo = profile.geography_exposure or {}
        for region, weight in geo.items():
            if region.lower() in event_region or event_region in region.lower():
                score += float(weight) * 0.4
        for ac, weight in ac_weights.items():
            score += float(weight) * 0.3
        if normalized_event.event_type in ("central_bank", "data_release"):
            score += 0.2
        return min(1.0, score + 0.1)
