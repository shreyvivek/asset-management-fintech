import re
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sources import Source, RawDocument
from app.models.events import NormalizedEvent, EventEntity, EventMarketFeature


THEME_KEYWORDS = {
    "fed-pivot": ["fed", "powell", "rate", "fomc", "taper", "hike", "cut", "easing"],
    "us-inflation": ["cpi", "inflation", "pce", "ppi", "bls"],
    "em-currency": ["em", "emerging", "dxy", "fx", "currency", "turkey", "brazil", "zar"],
    "china-growth": ["china", "pboc", "evergrande", "property", "growth"],
}


def classify_event_type(title: str, summary: str) -> str:
    t = (title + " " + summary).lower()
    if any(k in t for k in ["fed", "fomc", "powell", "ecb", "central bank"]):
        return "central_bank"
    if any(k in t for k in ["cpi", "gdp", "employment", "nfp", "release"]):
        return "data_release"
    if any(k in t for k in ["war", "sanctions", "election", "geopolitical"]):
        return "geopolitical"
    if any(k in t for k in ["earnings", "guidance", "quarterly"]):
        return "earnings"
    return "macro"


def extract_region(title: str, summary: str) -> str | None:
    t = (title + " " + summary).lower()
    if "us " in t or "u.s." in t or "federal reserve" in t or "bls" in t:
        return "Americas"
    if "ecb" in t or "euro" in t or "europe" in t:
        return "Europe"
    if "china" in t or "asia" in t or "mas" in t or "singapore" in t:
        return "Asia-Pacific"
    return "Global"


def extract_keywords(text: str, max_=10) -> list[str]:
    words = re.findall(r"[a-z]{4,}", text.lower())
    stop = {"that", "this", "with", "from", "have", "were", "been", "their", "would", "could", "about"}
    seen = set()
    out = []
    for w in words:
        if w not in stop and w not in seen and len(out) < max_:
            seen.add(w)
            out.append(w)
    return out


class PreprocessingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def normalize_pending_raw_documents(self) -> int:
        r = await self.db.execute(
            select(RawDocument).where(RawDocument.normalized_event_id.is_(None))
        )
        docs = r.scalars().all()
        count = 0
        for doc in docs:
            ev = await self._normalize_one(doc)
            if ev:
                doc.normalized_event_id = ev.id
                count += 1
        await self.db.commit()
        return count

    async def _normalize_one(self, doc: RawDocument) -> NormalizedEvent | None:
        lines = doc.raw_content.strip().split("\n")
        title = lines[0][:1024] if lines else doc.raw_content[:1024]
        summary = "\n".join(lines[1:])[:2000] if len(lines) > 1 else None
        meta = getattr(doc, "_meta", {}) or {}
        published_at = meta.get("published") or doc.fetched_at
        event_type = meta.get("event_type") or classify_event_type(title, summary or "")
        region = meta.get("region") or extract_region(title, summary or "")
        keywords = extract_keywords(title + " " + (summary or ""))
        r = await self.db.execute(select(Source).where(Source.id == doc.source_id))
        source = r.scalars().first()
        credibility = source.credibility if source else "secondary"
        ev = NormalizedEvent(
            raw_document_id=doc.id,
            source_id=doc.source_id,
            title=title,
            summary=summary,
            source_credibility=credibility,
            published_at=published_at,
            normalized_at=datetime.utcnow(),
            region=region,
            event_type=event_type,
            keywords=keywords,
            body=doc.raw_content[:8000] if len(doc.raw_content) > 8000 else doc.raw_content,
        )
        self.db.add(ev)
        await self.db.flush()
        return ev
