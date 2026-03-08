from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


def _vector_type():
    if HAS_PGVECTOR:
        return Vector(1536)
    return None


class HistoricalEvent(Base):
    __tablename__ = "historical_events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    surprise_magnitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    macro_regime_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class HistoricalEventOutcome(Base):
    __tablename__ = "historical_event_outcomes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    historical_event_id: Mapped[int] = mapped_column(ForeignKey("historical_events.id"), nullable=False)
    horizon: Mapped[str] = mapped_column(String(16), nullable=False)  # 24h, 1w, 1m
    outcome_description: Mapped[str] = mapped_column(Text, nullable=False)
    asset_reactions: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class EventEmbedding(Base):
    __tablename__ = "event_embeddings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalized_event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    historical_event_id: Mapped[int | None] = mapped_column(ForeignKey("historical_events.id"), nullable=True)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)  # store as JSON if pgvector not available
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AnalogueMatch(Base):
    __tablename__ = "analogue_matches"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalized_event_id: Mapped[int] = mapped_column(Integer, nullable=False)
    historical_event_id: Mapped[int] = mapped_column(ForeignKey("historical_events.id"), nullable=False)
    simulation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # FK to simulations.id, avoid circular import
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    quantitative_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    combined_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
