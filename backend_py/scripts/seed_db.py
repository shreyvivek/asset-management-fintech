#!/usr/bin/env python3
"""Seed MIVE database: historical events, portfolio personas, companies, watchlists."""
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone

# Add parent so app is importable
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.user import Organization, User
from app.models.portfolio import PortfolioProfile, Watchlist, WatchlistItem
from app.models.valuation import Company, BaselineValuation, SensitivityMatrix
from app.models.memory import HistoricalEvent, HistoricalEventOutcome
from app.models.events import NormalizedEvent
from app.models.sources import Source


SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"


async def load_historical_events(session) -> int:
    p = SEED_DIR / "historical_events.json"
    if not p.exists():
        return 0
    data = json.loads(p.read_text())
    r = await session.execute(select(HistoricalEvent).limit(1))
    if r.scalars().first():
        return 0
    for row in data:
        dt = datetime.fromisoformat(row["event_date"] + "T12:00:00").replace(tzinfo=timezone.utc)
        he = HistoricalEvent(
            event_type=row["event_type"],
            event_date=dt,
            title=row["title"],
            description=row.get("description"),
            region=row.get("region"),
            surprise_magnitude=row.get("surprise_magnitude"),
        )
        session.add(he)
        await session.flush()
        outcomes = row.get("outcomes") or {}
        for horizon, desc in outcomes.items():
            session.add(HistoricalEventOutcome(historical_event_id=he.id, horizon=horizon, outcome_description=desc))
    return len(data)


async def seed_org_and_profiles(session) -> None:
    r = await session.execute(select(Organization).limit(1))
    if r.scalars().first():
        return
    org = Organization(name="MIVE Demo Org")
    session.add(org)
    await session.flush()
    personas = [
        ("Asian Fixed Income Fund", "asian_fi", {"rates": 0.5, "credit": 0.3, "fx": 0.2}, {"APAC": 0.6, "US": 0.2}),
        ("US Tech Growth Fund", "us_tech_growth", {"equities": 0.9, "rates": 0.1}, {"US": 0.8}),
        ("EM Equity Long/Short", "em_equity_ls", {"equities": 0.6, "fx": 0.2, "commodities": 0.2}, {"EM": 0.5, "APAC": 0.3}),
        ("Global Macro Hedge Fund", "global_macro", {"rates": 0.25, "fx": 0.25, "equities": 0.2, "commodities": 0.2}, {"US": 0.3, "EU": 0.2, "APAC": 0.2}),
    ]
    for name, mandate, ac_weights, geo in personas:
        p = PortfolioProfile(
            organization_id=org.id,
            name=name,
            mandate_persona=mandate,
            asset_class_weights=ac_weights,
            geography_exposure=geo,
            sector_exposures={},
        )
        session.add(p)
        await session.flush()
        wl = Watchlist(portfolio_profile_id=p.id, name="Default")
        session.add(wl)
        await session.flush()
        for ticker in ["AAPL", "MSFT", "GOOGL"][:2]:
            session.add(WatchlistItem(watchlist_id=wl.id, ticker=ticker))


async def seed_companies_and_valuations(session) -> None:
    r = await session.execute(select(Company).limit(1))
    if r.scalars().first():
        return
    tickers = [
        ("AAPL", "Apple Inc", 220.0),
        ("MSFT", "Microsoft Corp", 450.0),
        ("GOOGL", "Alphabet Inc", 180.0),
        ("NVDA", "NVIDIA Corp", 950.0),
    ]
    as_of = datetime.now(timezone.utc)
    for ticker, name, fv in tickers:
        c = Company(ticker=ticker, name=name)
        session.add(c)
        await session.flush()
        session.add(BaselineValuation(company_id=c.id, fair_value=fv, currency="USD", as_of_date=as_of))
        session.add(SensitivityMatrix(
            company_id=c.id,
            rates_100bps_pct=-5.0,
            usd_5pct_pct=-2.0,
            oil_20pct_pct=0.0,
            gdp_1pp_pct=6.0,
        ))


async def seed_sources(session) -> None:
    r = await session.execute(select(Source).limit(1))
    if r.scalars().first():
        return
    for slug, name in [("fed_rss", "Federal Reserve RSS"), ("alpha_vantage", "Alpha Vantage")]:
        session.add(Source(name=name, slug=slug, source_type="rss" if slug == "fed_rss" else "api", credibility="official" if slug == "fed_rss" else "secondary", enabled=True))


async def seed_sample_events(session) -> int:
    r = await session.execute(select(NormalizedEvent).where(NormalizedEvent.source_credibility == "manual").limit(1))
    if r.scalars().first():
        return 0
    for title, summary, etype in [
        ("US CPI surprise above consensus", "Headline CPI +0.4% MoM vs +0.2% expected.", "data_release"),
        ("Fed signals data-dependent path", "FOMC keeps rates unchanged, dot plot shows fewer cuts.", "central_bank"),
    ]:
        session.add(NormalizedEvent(title=title, summary=summary, source_credibility="manual", event_type=etype))
    return 2


async def main():
    async with async_session_factory() as session:
        try:
            n_hist = await load_historical_events(session)
            print(f"Historical events: {n_hist}")
            await seed_org_and_profiles(session)
            print("Org and portfolio profiles seeded.")
            await seed_companies_and_valuations(session)
            print("Companies and valuations seeded.")
            await seed_sources(session)
            print("Sources seeded.")
            n_ev = await seed_sample_events(session)
            print(f"Sample events: {n_ev}")
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
