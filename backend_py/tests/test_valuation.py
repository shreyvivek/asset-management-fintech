"""Valuation adjustment logic: delta_pct from sensitivity and macro deltas."""
# Pure function style: no DB, just the formula used in ValuationService
def apply_macro_delta_pct(
    rates_delta_bps: float,
    usd_delta_pct: float,
    oil_delta_pct: float,
    gdp_delta_pp: float,
    rates_100bps_pct: float = -5.0,
    usd_5pct_pct: float = -2.0,
    oil_20pct_pct: float = 0.0,
    gdp_1pp_pct: float = 6.0,
) -> float:
    return (
        (rates_delta_bps / 100) * rates_100bps_pct
        + (usd_delta_pct / 5) * usd_5pct_pct
        + (oil_delta_pct / 20) * oil_20pct_pct
        + (gdp_delta_pp / 1) * gdp_1pp_pct
    )


def test_rates_up_negative_fv():
    delta = apply_macro_delta_pct(rates_delta_bps=100, usd_delta_pct=0, oil_delta_pct=0, gdp_delta_pp=0)
    assert delta == -5.0


def test_gdp_up_positive_fv():
    delta = apply_macro_delta_pct(rates_delta_bps=0, usd_delta_pct=0, oil_delta_pct=0, gdp_delta_pp=1)
    assert delta == 6.0


def test_usd_up_negative_fv():
    delta = apply_macro_delta_pct(rates_delta_bps=0, usd_delta_pct=5, oil_delta_pct=0, gdp_delta_pp=0)
    assert delta == -2.0
