from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers import get_embedding_provider
from app.core.config import get_settings
from app.models.events import NormalizedEvent
from app.models.memory import EventEmbedding, HistoricalEvent


class EmbeddingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_embedding_provider()
        self.settings = get_settings()

    def _text_for_event(self, ev: NormalizedEvent) -> str:
        return f"{ev.title}\n{ev.summary or ''}\n{ev.body or ''}"[:8000]

    def _text_for_historical(self, ev: HistoricalEvent) -> str:
        return f"{ev.title}\n{ev.description or ''}"[:8000]

    async def embed_normalized_events(self, event_ids: list[int] | None = None, limit: int = 50) -> int:
        q = select(NormalizedEvent).where(
            ~NormalizedEvent.id.in_(
                select(EventEmbedding.normalized_event_id).where(EventEmbedding.normalized_event_id.isnot(None))
            )
        )
        if event_ids:
            q = q.where(NormalizedEvent.id.in_(event_ids))
        q = q.limit(limit)
        r = await self.db.execute(q)
        events = r.scalars().all()
        if not events:
            return 0
        texts = [self._text_for_event(e) for e in events]
        vectors = await self.provider.embed(texts)
        for ev, vec in zip(events, vectors):
            self.db.add(EventEmbedding(
                normalized_event_id=ev.id,
                model=self.settings.embedding_model,
                embedding=vec,
            ))
        await self.db.commit()
        return len(events)

    async def embed_historical_events(self, event_ids: list[int] | None = None) -> int:
        q = select(HistoricalEvent).where(
            ~HistoricalEvent.id.in_(
                select(EventEmbedding.historical_event_id).where(EventEmbedding.historical_event_id.isnot(None))
            )
        )
        if event_ids:
            q = q.where(HistoricalEvent.id.in_(event_ids))
        r = await self.db.execute(q)
        events = r.scalars().all()
        if not events:
            return 0
        texts = [self._text_for_historical(e) for e in events]
        vectors = await self.provider.embed(texts)
        for ev, vec in zip(events, vectors):
            self.db.add(EventEmbedding(
                historical_event_id=ev.id,
                model=self.settings.embedding_model,
                embedding=vec,
            ))
        await self.db.commit()
        return len(events)
