from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Theme(Base):
    __tablename__ = "themes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    asset_class_tag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ThemeEventLink(Base):
    __tablename__ = "theme_event_links"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    normalized_event_id: Mapped[int] = mapped_column(ForeignKey("normalized_events.id"), nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ThemeHeatSnapshot(Base):
    __tablename__ = "theme_heat_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    heat_score: Mapped[float] = mapped_column(Float, nullable=False)
    trajectory: Mapped[str] = mapped_column(String(16), nullable=False)  # heating, cooling, stable
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ThemeRelationship(Base):
    __tablename__ = "theme_relationships"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    theme_id_from: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    theme_id_to: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    correlation: Mapped[float | None] = mapped_column(Float, nullable=True)
