from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class BaselineValuation(Base):
    __tablename__ = "baseline_valuations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    fair_value: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    as_of_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    inputs_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class SensitivityMatrix(Base):
    __tablename__ = "sensitivity_matrices"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    rates_100bps_pct: Mapped[float] = mapped_column(Float, nullable=False, default=-5.0)
    usd_5pct_pct: Mapped[float] = mapped_column(Float, nullable=False, default=-2.0)
    oil_20pct_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gdp_1pp_pct: Mapped[float] = mapped_column(Float, nullable=False, default=6.0)
    inflation_beta: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ValuationAdjustment(Base):
    __tablename__ = "valuation_adjustments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), nullable=True)
    baseline_fv: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_fv: Mapped[float] = mapped_column(Float, nullable=False)
    delta_pct: Mapped[float] = mapped_column(Float, nullable=False)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    macro_drivers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class TickerExposureLink(Base):
    __tablename__ = "ticker_exposure_links"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    exposure_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
