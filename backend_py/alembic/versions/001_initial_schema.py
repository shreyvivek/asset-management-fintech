"""Initial schema.

Revision ID: 001
Revises:
Create Date: 2026-03-08

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("credibility", sa.String(32), nullable=True),
        sa.Column("config", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sources_slug", "sources", ["slug"], unique=True)
    op.create_table(
        "raw_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("normalized_event_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_documents_content_hash", "raw_documents", ["content_hash"], unique=False)
    op.create_table(
        "normalized_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("raw_document_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_credibility", sa.String(32), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("normalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("country", sa.String(64), nullable=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("asset_classes_affected", sa.JSON(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("surprise_magnitude", sa.Float(), nullable=True),
        sa.Column("tone_shift_score", sa.Float(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["raw_document_id"], ["raw_documents.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_normalized_events_event_type", "normalized_events", ["event_type"], unique=False)
    op.create_index("ix_normalized_events_region", "normalized_events", ["region"], unique=False)
    op.create_table(
        "portfolio_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("mandate_persona", sa.String(64), nullable=False),
        sa.Column("asset_class_weights", sa.JSON(), nullable=True),
        sa.Column("geography_exposure", sa.JSON(), nullable=True),
        sa.Column("sector_exposures", sa.JSON(), nullable=True),
        sa.Column("duration_risk_years", sa.Float(), nullable=True),
        sa.Column("fx_risk_characteristics", sa.JSON(), nullable=True),
        sa.Column("alert_thresholds", sa.JSON(), nullable=True),
        sa.Column("preferred_agent_weights", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_portfolio_profiles_mandate_persona", "portfolio_profiles", ["mandate_persona"], unique=False)
    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("portfolio_profile_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(32), nullable=False),
        sa.Column("weight_pct", sa.Float(), nullable=True),
        sa.Column("notional", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["portfolio_profile_id"], ["portfolio_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_holdings_ticker", "holdings", ["ticker"], unique=False)
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("portfolio_profile_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["portfolio_profile_id"], ["portfolio_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("watchlist_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(32), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["watchlist_id"], ["watchlists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_watchlist_items_ticker", "watchlist_items", ["ticker"], unique=False)
    op.create_table(
        "event_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_value", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "event_market_features",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=False),
        sa.Column("rate_regime", sa.String(32), nullable=True),
        sa.Column("vix_regime", sa.String(32), nullable=True),
        sa.Column("inflation_env", sa.String(32), nullable=True),
        sa.Column("features_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "themes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("asset_class_tag", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_themes_slug", "themes", ["slug"], unique=True)
    op.create_table(
        "theme_event_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "theme_heat_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("heat_score", sa.Float(), nullable=False),
        sa.Column("trajectory", sa.String(16), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "theme_relationships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("theme_id_from", sa.Integer(), nullable=False),
        sa.Column("theme_id_to", sa.Integer(), nullable=False),
        sa.Column("correlation", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["theme_id_from"], ["themes.id"]),
        sa.ForeignKeyConstraint(["theme_id_to"], ["themes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "historical_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("region", sa.String(64), nullable=True),
        sa.Column("surprise_magnitude", sa.Float(), nullable=True),
        sa.Column("macro_regime_tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_historical_events_event_type", "historical_events", ["event_type"], unique=False)
    op.create_table(
        "historical_event_outcomes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("historical_event_id", sa.Integer(), nullable=False),
        sa.Column("horizon", sa.String(16), nullable=False),
        sa.Column("outcome_description", sa.Text(), nullable=False),
        sa.Column("asset_reactions", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["historical_event_id"], ["historical_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "event_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=True),
        sa.Column("historical_event_id", sa.Integer(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["historical_event_id"], ["historical_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "analogue_matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=False),
        sa.Column("historical_event_id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=True),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("quantitative_score", sa.Float(), nullable=True),
        sa.Column("combined_score", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["historical_event_id"], ["historical_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_companies_ticker", "companies", ["ticker"], unique=True)
    op.create_table(
        "simulations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("normalized_event_id", sa.Integer(), nullable=False),
        sa.Column("portfolio_profile_id", sa.Integer(), nullable=True),
        sa.Column("trigger_reason", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.ForeignKeyConstraint(["portfolio_profile_id"], ["portfolio_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "simulation_inputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("input_type", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_runs_agent_id", "agent_runs", ["agent_id"], unique=False)
    op.create_table(
        "agent_outputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_run_id", sa.Integer(), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("directional_calls", sa.JSON(), nullable=True),
        sa.Column("asset_impacts", sa.JSON(), nullable=True),
        sa.Column("implications", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("risks_caveats", sa.Text(), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("is_unanchored", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "evidence_anchors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_output_id", sa.Integer(), nullable=False),
        sa.Column("anchor_text", sa.String(512), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["agent_output_id"], ["agent_outputs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "debate_summaries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("debater_thesis", sa.Text(), nullable=True),
        sa.Column("vulnerable_assumptions", sa.JSON(), nullable=True),
        sa.Column("counter_narrative", sa.Text(), nullable=True),
        sa.Column("historical_counterexample", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "consensus_outputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("risk_chain", sa.JSON(), nullable=True),
        sa.Column("signals_by_asset", sa.JSON(), nullable=True),
        sa.Column("consensus_strength", sa.Float(), nullable=True),
        sa.Column("disagreement_score", sa.Float(), nullable=True),
        sa.Column("debater_divergence", sa.Float(), nullable=True),
        sa.Column("anchored_ratio", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "baseline_valuations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("fair_value", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(8), nullable=True),
        sa.Column("as_of_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inputs_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sensitivity_matrices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("rates_100bps_pct", sa.Float(), nullable=True),
        sa.Column("usd_5pct_pct", sa.Float(), nullable=True),
        sa.Column("oil_20pct_pct", sa.Float(), nullable=True),
        sa.Column("gdp_1pp_pct", sa.Float(), nullable=True),
        sa.Column("inflation_beta", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "valuation_adjustments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=True),
        sa.Column("baseline_fv", sa.Float(), nullable=False),
        sa.Column("adjusted_fv", sa.Float(), nullable=False),
        sa.Column("delta_pct", sa.Float(), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("macro_drivers", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ticker_exposure_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("theme_id", sa.Integer(), nullable=False),
        sa.Column("exposure_score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("portfolio_profile_id", sa.Integer(), nullable=True),
        sa.Column("simulation_id", sa.Integer(), nullable=True),
        sa.Column("normalized_event_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.String(64), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.ForeignKeyConstraint(["portfolio_profile_id"], ["portfolio_profiles.id"]),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_alert_interactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "agent_track_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("directional_correct", sa.Boolean(), nullable=True),
        sa.Column("magnitude_error", sa.Float(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_track_records_agent_id", "agent_track_records", ["agent_id"], unique=False)
    op.create_index("ix_agent_track_records_event_type", "agent_track_records", ["event_type"], unique=False)
    op.create_table(
        "model_provider_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("call_type", sa.String(32), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for t in [
        "model_provider_logs", "agent_track_records", "user_alert_interactions", "alerts",
        "ticker_exposure_links", "valuation_adjustments", "sensitivity_matrices", "baseline_valuations",
        "consensus_outputs", "debate_summaries", "evidence_anchors", "agent_outputs", "agent_runs",
        "simulation_inputs", "simulations", "companies", "analogue_matches", "event_embeddings",
        "historical_event_outcomes", "historical_events", "theme_relationships", "theme_heat_snapshots",
        "theme_event_links", "themes", "event_market_features", "event_entities", "watchlist_items",
        "watchlists", "holdings", "portfolio_profiles", "raw_documents", "normalized_events",
        "sources", "users", "organizations",
    ]:
        op.drop_table(t)
