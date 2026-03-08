from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.valuation import Company, BaselineValuation, SensitivityMatrix, ValuationAdjustment
from app.models.agents import ConsensusOutput, Simulation


class ValuationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_baseline(self, ticker: str) -> tuple[float, int | None] | None:
        r = await self.db.execute(select(Company).where(Company.ticker == ticker))
        company = r.scalars().first()
        if not company:
            return None
        r2 = await self.db.execute(
            select(BaselineValuation).where(BaselineValuation.company_id == company.id).order_by(BaselineValuation.as_of_date.desc()).limit(1)
        )
        bv = r2.scalars().first()
        if not bv:
            return None
        return bv.fair_value, company.id

    async def get_sensitivity(self, company_id: int) -> dict | None:
        r = await self.db.execute(select(SensitivityMatrix).where(SensitivityMatrix.company_id == company_id).limit(1))
        s = r.scalars().first()
        if not s:
            return None
        return {
            "rates_100bps_pct": s.rates_100bps_pct,
            "usd_5pct_pct": s.usd_5pct_pct,
            "oil_20pct_pct": s.oil_20pct_pct,
            "gdp_1pp_pct": s.gdp_1pp_pct,
            "inflation_beta": s.inflation_beta,
        }

    async def apply_macro_adjustment(
        self,
        company_id: int,
        baseline_fv: float,
        simulation_id: int | None,
        rates_delta_bps: float = 0,
        usd_delta_pct: float = 0,
        oil_delta_pct: float = 0,
        gdp_delta_pp: float = 0,
    ) -> ValuationAdjustment:
        sens = await self.get_sensitivity(company_id)
        if not sens:
            delta_pct = 0.0
        else:
            delta_pct = (
                (rates_delta_bps / 100) * sens.get("rates_100bps_pct", -5.0)
                + (usd_delta_pct / 5) * sens.get("usd_5pct_pct", -2.0)
                + (oil_delta_pct / 20) * sens.get("oil_20pct_pct", 0.0)
                + (gdp_delta_pp / 1) * sens.get("gdp_1pp_pct", 6.0)
            )
        adjusted_fv = baseline_fv * (1 + delta_pct / 100)
        narrative = f"Macro adjustment: rates {rates_delta_bps:+.0f}bps, USD {usd_delta_pct:+.1f}%, oil {oil_delta_pct:+.1f}%, GDP {gdp_delta_pp:+.1f}pp → FV {delta_pct:+.2f}%."
        adj = ValuationAdjustment(
            company_id=company_id,
            simulation_id=simulation_id,
            baseline_fv=baseline_fv,
            adjusted_fv=adjusted_fv,
            delta_pct=delta_pct,
            narrative=narrative,
            macro_drivers={"rates_bps": rates_delta_bps, "usd_pct": usd_delta_pct, "oil_pct": oil_delta_pct, "gdp_pp": gdp_delta_pp},
        )
        self.db.add(adj)
        await self.db.flush()
        return adj

    async def get_adjustments_for_ticker(self, ticker: str, limit: int = 10) -> list[ValuationAdjustment]:
        r = await self.db.execute(select(Company).where(Company.ticker == ticker))
        company = r.scalars().first()
        if not company:
            return []
        r2 = await self.db.execute(
            select(ValuationAdjustment).where(ValuationAdjustment.company_id == company.id).order_by(ValuationAdjustment.created_at.desc()).limit(limit)
        )
        return list(r2.scalars().all())

    async def get_watchlist_valuations(self, watchlist_id: int) -> list[dict]:
        from app.models.portfolio import WatchlistItem
        r = await self.db.execute(select(WatchlistItem.ticker).where(WatchlistItem.watchlist_id == watchlist_id))
        tickers = [row[0] for row in r.all()]
        out = []
        for t in tickers:
            base = await self.get_baseline(t)
            if not base:
                out.append({"ticker": t, "baseline_fv": None, "adjusted_fv": None, "delta_pct": None})
                continue
            fv, cid = base
            adjs = await self.get_adjustments_for_ticker(t, limit=1)
            adj_fv = adjs[0].adjusted_fv if adjs else fv
            delta = ((adj_fv - fv) / fv * 100) if fv else None
            out.append({"ticker": t, "baseline_fv": fv, "adjusted_fv": adj_fv, "delta_pct": delta})
        return out
