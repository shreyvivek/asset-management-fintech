from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from app.models.events import NormalizedEvent
from app.models.memory import HistoricalEvent, HistoricalEventOutcome, EventEmbedding, AnalogueMatch


@dataclass
class AnalogueResult:
    historical_event_id: int
    title: str
    event_date: str
    outcome_24h: str | None
    outcome_1w: str | None
    similarity_score: float
    quantitative_score: float
    combined_score: float
    reason: str


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    x, y = np.array(a), np.array(b)
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_event_embedding(self, normalized_event_id: int) -> list[float] | None:
        r = await self.db.execute(
            select(EventEmbedding.embedding).where(
                EventEmbedding.normalized_event_id == normalized_event_id,
            ).limit(1)
        )
        row = r.first()
        return row[0] if row and row[0] else None

    async def retrieve_analogues(
        self,
        normalized_event_id: int,
        top_k: int = 3,
        min_confidence: float = 0.3,
        simulation_id: int | None = None,
    ) -> list[AnalogueResult]:
        ev_emb = await self.get_event_embedding(normalized_event_id)
        r = await self.db.execute(select(NormalizedEvent).where(NormalizedEvent.id == normalized_event_id))
        ev = r.scalars().first()
        if not ev or not ev_emb:
            return []
        hist_embeddings = await self.db.execute(
            select(EventEmbedding.historical_event_id, EventEmbedding.embedding).where(
                EventEmbedding.historical_event_id.isnot(None),
                EventEmbedding.embedding.isnot(None),
            )
        )
        candidates: list[tuple[int, float]] = []
        for hid, emb in hist_embeddings.all():
            if not emb or not ev_emb:
                continue
            sim = cosine_similarity(ev_emb, emb)
            quant = 0.5
            if ev.surprise_magnitude is not None:
                quant = 0.5 + min(0.5, abs(ev.surprise_magnitude) * 0.1)
            combined = 0.6 * sim + 0.4 * quant
            if combined >= min_confidence:
                candidates.append((hid, combined))
        candidates.sort(key=lambda x: -x[1])
        results = []
        for rank, (hid, combined) in enumerate(candidates[:top_k], 1):
            r2 = await self.db.execute(select(HistoricalEvent).where(HistoricalEvent.id == hid))
            he = r2.scalars().first()
            if not he:
                continue
            r3 = await self.db.execute(
                select(HistoricalEventOutcome).where(
                    HistoricalEventOutcome.historical_event_id == hid,
                )
            )
            outcomes = {o.horizon: o.outcome_description for o in r3.scalars().all()}
            self.db.add(AnalogueMatch(
                normalized_event_id=normalized_event_id,
                historical_event_id=hid,
                simulation_id=simulation_id,
                similarity_score=combined,
                quantitative_score=0.5,
                combined_score=combined,
                reason=f"Semantic + regime match (rank {rank})",
                rank=rank,
            ))
            results.append(AnalogueResult(
                historical_event_id=he.id,
                title=he.title,
                event_date=he.event_date.isoformat() if he.event_date else "",
                outcome_24h=outcomes.get("24h"),
                outcome_1w=outcomes.get("1w"),
                similarity_score=combined,
                quantitative_score=0.5,
                combined_score=combined,
                reason=f"Semantic + regime match (rank {rank})",
            ))
        return results
