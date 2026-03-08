AGENT_REGISTRY = [
    {"id": "central_bank_watcher", "name": "Central Bank Watcher", "focus": "Policy signals, forward guidance, dot plot, hawk/dove tone."},
    {"id": "bond_trader", "name": "Bond Trader", "focus": "Duration risk, yield curve, credit spreads, real yields."},
    {"id": "equity_strategist", "name": "Equity Strategist", "focus": "Sector rotation, P/E compression, earnings revision risk."},
    {"id": "macro_hedge_fund", "name": "Macro Hedge Fund", "focus": "Non-consensus trades, tail risk, asymmetric opportunities."},
    {"id": "risk_manager", "name": "Risk Manager", "focus": "Portfolio stress, concentration, hedging instruments."},
    {"id": "em_analyst", "name": "Emerging Market Analyst", "focus": "EM spillovers, capital flows, FX pressure, China."},
]


def get_agent_focus(agent_id: str) -> str:
    for a in AGENT_REGISTRY:
        if a["id"] == agent_id:
            return a["focus"]
    return "Macro and cross-asset implications."
