#!/usr/bin/env python3
"""Run ingestion -> preprocessing -> embeddings -> clustering once."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import async_session_factory
from app.services.ingestion.service import IngestionService
from app.services.preprocessing.service import PreprocessingService
from app.services.embeddings.service import EmbeddingService
from app.services.clustering.service import ClusteringService


async def main():
    async with async_session_factory() as session:
        ing = IngestionService(session)
        await ing.ensure_sources()
        for slug in ["fed_rss", "alpha_vantage"]:
            n = await ing.run_for_source(slug)
            print(f"Ingestion {slug}: {n} new docs")
        pre = PreprocessingService(session)
        await pre.normalize_pending_raw_documents()
        await session.commit()
    async with async_session_factory() as session:
        emb = EmbeddingService(session)
        n_emb = await emb.embed_normalized_events(limit=50)
        print(f"Embedded events: {n_emb}")
        n_hist = await emb.embed_historical_events()
        print(f"Embedded historical: {n_hist}")
    async with async_session_factory() as session:
        cl = ClusteringService(session)
        n_themes = await cl.run_clustering()
        print(f"Clustering: {n_themes} themes updated")


if __name__ == "__main__":
    asyncio.run(main())
