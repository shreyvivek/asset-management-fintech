from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    portfolio_profile_id: Mapped[int | None] = mapped_column(ForeignKey("portfolio_profiles.id"), nullable=True)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), nullable=True)
    normalized_event_id: Mapped[int | None] = mapped_column(ForeignKey("normalized_events.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class UserAlertInteraction(Base):
    __tablename__ = "user_alert_interactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # ack, dismiss, click
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
