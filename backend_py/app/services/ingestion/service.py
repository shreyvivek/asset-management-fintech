from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_factory
from app.models.sources import Source, RawDocument
from app.services.ingestion.adapters import FedRssAdapter, AlphaVantageAdapter
from app.services.preprocessing.service import PreprocessingService


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.adapters = {
            "fed_rss": FedRssAdapter(),
            "alpha_vantage": AlphaVantageAdapter(),
        }

    async def ensure_sources(self) -> None:
        for slug, adapter in self.adapters.items():
            r = await self.db.execute(select(Source).where(Source.slug == slug))
            if r.scalars().first() is None:
                name = "Federal Reserve RSS" if slug == "fed_rss" else "Alpha Vantage"
                cred = "official" if slug == "fed_rss" else "secondary"
                self.db.add(Source(
                    name=name,
                    slug=slug,
                    source_type="rss" if slug == "fed_rss" else "api",
                    credibility=cred,
                    enabled=True,
                ))
        await self.db.commit()

    async def run_for_source(self, slug: str) -> int:
        adapter = self.adapters.get(slug)
        if not adapter:
            return 0
        r = await self.db.execute(select(Source).where(Source.slug == slug))
        source = r.scalars().first()
        if not source or not source.enabled:
            return 0
        payloads = await adapter.fetch()
        added = 0
        for p in payloads:
            r2 = await self.db.execute(select(RawDocument).where(RawDocument.content_hash == p.content_hash))
            if r2.scalars().first() is not None:
                continue
            doc = RawDocument(
                source_id=source.id,
                external_id=p.external_id,
                content_hash=p.content_hash,
                raw_content=p.raw_content,
                fetched_at=p.fetched_at,
            )
            self.db.add(doc)
            added += 1
        source.last_fetched_at = datetime.utcnow()
        await self.db.commit()
        preproc = PreprocessingService(self.db)
        await preproc.normalize_pending_raw_documents()
        return added

    async def run_all(self) -> dict[str, int]:
        await self.ensure_sources()
        result = {}
        for slug in self.adapters:
            result[slug] = await self.run_for_source(slug)
        return result
