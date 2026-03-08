from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class NormalizedEvent(Base):
    __tablename__ = "normalized_events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raw_document_id: Mapped[int | None] = mapped_column(ForeignKey("raw_documents.id"), nullable=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_credibility: Mapped[str] = mapped_column(String(32), nullable=False, default="secondary")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    normalized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # central_bank, data_release, geopolitical, earnings
    asset_classes_affected: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    surprise_magnitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    tone_shift_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class EventEntity(Base):
    __tablename__ = "event_entities"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalized_event_id: Mapped[int] = mapped_column(ForeignKey("normalized_events.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_value: Mapped[str] = mapped_column(String(255), nullable=False)


class EventMarketFeature(Base):
    __tablename__ = "event_market_features"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalized_event_id: Mapped[int] = mapped_column(ForeignKey("normalized_events.id"), nullable=False)
    rate_regime: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vix_regime: Mapped[str | None] = mapped_column(String(32), nullable=True)
    inflation_env: Mapped[str | None] = mapped_column(String(32), nullable=True)
    features_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
