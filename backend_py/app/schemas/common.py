from pydantic import BaseModel
from datetime import datetime
from typing import Any


class EventBrief(BaseModel):
    id: int
    title: str
    summary: str | None
    source_credibility: str
    published_at: datetime | None
    region: str | None
    event_type: str
    sentiment_score: float | None
    surprise_magnitude: float | None

    class Config:
        from_attributes = True


class ThemeBrief(BaseModel):
    id: int
    slug: str
    label: str | None
    heat_score: float | None
    trajectory: str | None

    class Config:
        from_attributes = True
