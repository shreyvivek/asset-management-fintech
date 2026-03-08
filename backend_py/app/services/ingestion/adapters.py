from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import hashlib
import feedparser
import httpx
from app.core.config import get_settings


@dataclass
class RawDocumentPayload:
    external_id: str | None
    content_hash: str
    raw_content: str
    fetched_at: datetime
    meta: dict[str, Any]


class SourceAdapter(ABC):
    @abstractmethod
    async def fetch(self) -> list[RawDocumentPayload]:
        pass

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()


class FedRssAdapter(SourceAdapter):
    def __init__(self):
        self.settings = get_settings()

    async def fetch(self) -> list[RawDocumentPayload]:
        out: list[RawDocumentPayload] = []
        try:
            feed = feedparser.parse(self.settings.fed_rss_url)
            for i, entry in enumerate((feed.entries or [])[:20]):
                title = entry.get("title") or ""
                summary = entry.get("summary") or entry.get("description") or ""
                link = entry.get("link") or ""
                raw = f"{title}\n{summary}\n{link}"
                content_hash = self.hash_content(raw)
                published = None
                if entry.get("published_parsed"):
                    try:
                        from time import mktime
                        published = datetime.utcfromtimestamp(mktime(entry.published_parsed))
                    except Exception:
                        pass
                out.append(RawDocumentPayload(
                    external_id=link or f"fed_{i}",
                    content_hash=content_hash,
                    raw_content=raw,
                    fetched_at=datetime.utcnow(),
                    meta={"title": title, "summary": summary, "published": published},
                ))
        except Exception as e:
            from app.core.logging import get_logger
            get_logger(__name__).warning("fed_rss_fetch_failed", error=str(e))
        return out


class AlphaVantageAdapter(SourceAdapter):
    def __init__(self):
        self.settings = get_settings()

    async def fetch(self) -> list[RawDocumentPayload]:
        out: list[RawDocumentPayload] = []
        if not self.settings.alpha_vantage_api_key:
            return out
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = (
                    "https://www.alphavantage.co/query"
                    f"?function=REAL_GDP&interval=annual&apikey={self.settings.alpha_vantage_api_key}"
                )
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            gdps = data.get("data") or []
            if gdps:
                item = gdps[0]
                raw = f"US Real GDP: {item.get('value')}% ({item.get('date')})"
                content_hash = self.hash_content(raw)
                out.append(RawDocumentPayload(
                    external_id=item.get("date"),
                    content_hash=content_hash,
                    raw_content=raw,
                    fetched_at=datetime.utcnow(),
                    meta={"title": raw, "event_type": "macro_data", "region": "Americas"},
                ))
        except Exception as e:
            from app.core.logging import get_logger
            get_logger(__name__).warning("alpha_vantage_fetch_failed", error=str(e))
        return out
