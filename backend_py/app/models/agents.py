from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class Simulation(Base):
    __tablename__ = "simulations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalized_event_id: Mapped[int] = mapped_column(ForeignKey("normalized_events.id"), nullable=False)
    portfolio_profile_id: Mapped[int | None] = mapped_column(ForeignKey("portfolio_profiles.id"), nullable=True)
    trigger_reason: Mapped[str] = mapped_column(String(64), nullable=False)  # manual, auto_surprise, auto_heat, etc.
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SimulationInput(Base):
    __tablename__ = "simulation_inputs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    input_type: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentOutput(Base):
    __tablename__ = "agent_outputs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_run_id: Mapped[int] = mapped_column(ForeignKey("agent_runs.id"), nullable=False)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    directional_calls: Mapped[list | None] = mapped_column(JSON, nullable=True)
    asset_impacts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    implications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    risks_caveats: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_unanchored: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class EvidenceAnchor(Base):
    __tablename__ = "evidence_anchors"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_output_id: Mapped[int] = mapped_column(ForeignKey("agent_outputs.id"), nullable=False)
    anchor_text: Mapped[str] = mapped_column(String(512), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)


class DebateSummary(Base):
    __tablename__ = "debate_summaries"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    debater_thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    vulnerable_assumptions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    counter_narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    historical_counterexample: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ConsensusOutput(Base):
    __tablename__ = "consensus_outputs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    risk_chain: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    signals_by_asset: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    consensus_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    disagreement_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    debater_divergence: Mapped[float | None] = mapped_column(Float, nullable=True)
    anchored_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
