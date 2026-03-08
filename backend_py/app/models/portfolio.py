from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class PortfolioProfile(Base):
    __tablename__ = "portfolio_profiles"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mandate_persona: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # asian_fi, us_tech_growth, em_equity_ls, global_macro
    asset_class_weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    geography_exposure: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    sector_exposures: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    duration_risk_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    fx_risk_characteristics: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    alert_thresholds: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    preferred_agent_weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Holding(Base):
    __tablename__ = "holdings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    portfolio_profile_id: Mapped[int] = mapped_column(ForeignKey("portfolio_profiles.id"), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    weight_pct: Mapped[float] = mapped_column(Float, nullable=True)
    notional: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    portfolio_profile_id: Mapped[int] = mapped_column(ForeignKey("portfolio_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Default")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id"), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
