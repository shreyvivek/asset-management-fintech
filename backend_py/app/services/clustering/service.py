from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from app.core.config import get_settings
from app.models.events import NormalizedEvent
from app.models.memory import EventEmbedding
from app.models.themes import Theme, ThemeEventLink, ThemeHeatSnapshot


def heat_score(velocity: float, sentiment_delta: float, asset_dispersion: float) -> float:
    """Deterministic heat: 0-100. velocity = events per 24h, sentiment_delta in [-1,1], asset_dispersion in [0,1]."""
    v_component = min(40, velocity * 8)
    s_component = min(35, (sentiment_delta + 1) * 17.5)
    a_component = min(25, asset_dispersion * 25)
    return min(100.0, 20.0 + v_component + s_component + a_component)


def trajectory(prev_heat: float, curr_heat: float) -> str:
    if curr_heat - prev_heat >= 5:
        return "heating"
    if prev_heat - curr_heat >= 5:
        return "cooling"
    return "stable"


class ClusteringService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def get_recent_embeddings(self, window_hours: int | None = None) -> list[tuple[int, list[float]]]:
        window = window_hours or self.settings.clustering_window_hours
        since = datetime.utcnow() - timedelta(hours=window)
        r = await self.db.execute(
            select(EventEmbedding.normalized_event_id, EventEmbedding.embedding).where(
                EventEmbedding.normalized_event_id.isnot(None),
                EventEmbedding.embedding.isnot(None),
            )
        )
        rows = r.all()
        event_ids = []
        embeddings = []
        for eid, emb in rows:
            if emb is None:
                continue
            event_ids.append(eid)
            embeddings.append(emb)
        return list(zip(event_ids, embeddings))

    async def run_clustering(self) -> int:
        try:
            import hdbscan
        except ImportError:
            return 0
        data = await self.get_recent_embeddings()
        if len(data) < 2:
            return 0
        event_ids, vectors = zip(*data)
        X = np.array(vectors, dtype=np.float64)
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=max(1, self.settings.min_cluster_size),
            min_samples=self.settings.min_samples,
            metric="euclidean",
        )
        labels = clusterer.fit_predict(X)
        unique_labels = set(labels) - {-1}
        theme_slugs = {}
        for i, label in enumerate(unique_labels):
            slug = f"theme_{label}"
            theme_slugs[label] = slug
        r = await self.db.execute(select(Theme))
        existing = {t.slug: t for t in r.scalars().all()}
        for label in unique_labels:
            slug = theme_slugs[label]
            if slug not in existing:
                theme = Theme(slug=slug, name=slug.replace("_", " ").title(), region="Global")
                self.db.add(theme)
                await self.db.flush()
                existing[slug] = theme
        for i, label in enumerate(labels):
            if label == -1:
                continue
            slug = theme_slugs[label]
            theme = existing[slug]
            eid = event_ids[i]
            r2 = await self.db.execute(
                select(ThemeEventLink).where(
                    ThemeEventLink.theme_id == theme.id,
                    ThemeEventLink.normalized_event_id == eid,
                )
            )
            if r2.scalars().first() is not None:
                continue
            self.db.add(ThemeEventLink(theme_id=theme.id, normalized_event_id=eid))
        await self.db.commit()
        for theme in existing.values():
            await self._snapshot_heat(theme.id)
        await self.db.commit()
        return len(unique_labels)

    async def _snapshot_heat(self, theme_id: int) -> None:
        r = await self.db.execute(
            select(ThemeEventLink).where(ThemeEventLink.theme_id == theme_id)
        )
        links = r.scalars().all()
        n = len(links)
        velocity = n / max(1, self.settings.clustering_window_hours / 24)
        heat = heat_score(velocity, 0.0, 0.3)
        r2 = await self.db.execute(
            select(ThemeHeatSnapshot).where(ThemeHeatSnapshot.theme_id == theme_id).order_by(ThemeHeatSnapshot.snapshot_at.desc()).limit(1)
        )
        prev = r2.scalars().first()
        prev_heat = prev.heat_score if prev else heat
        traj = trajectory(prev_heat, heat)
        self.db.add(ThemeHeatSnapshot(theme_id=theme_id, heat_score=heat, trajectory=traj))
