RISK_CHAIN_PROMPT = """Generate a risk chain for this macro event.

Event: {title}
Summary: {summary}

Output JSON only, with this exact structure:
{{
  "first_order": [{{ "implication": "string", "asset_class": "string" }}],
  "second_order": [{{ "implication": "string", "asset_class": "string" }}],
  "third_order": [{{ "implication": "string", "asset_class": "string" }}]
}}

Provide 1-2 items per order. Be specific and evidence-based."""

AGENT_SYSTEM_TEMPLATE = """You are {agent_name}. Your focus: {focus}.

You must output valid JSON only, no markdown or extra text, with this structure:
{{
  "thesis": "1-2 sentence thesis",
  "directional_calls": [{{ "asset_class": "string", "direction": "up|down|neutral", "magnitude": "string" }}],
  "asset_impacts": [{{ "asset": "string", "impact": "string" }}],
  "implications": ["first-order", "second-order", "third-order"],
  "confidence": 0.0 to 1.0,
  "evidence_anchors": ["source: claim", "source: claim"],
  "risks_caveats": "1 sentence"
}}

Rules: Cite at least one evidence anchor (e.g. CME FedWatch, BLS, historical date). Do not use generic hedging. Do not pretend false certainty."""

DEBATER_PROMPT = """You are the Debater. You must challenge the consensus.

Event: {title}

Other agents' theses (summary): {theses_summary}

Output JSON only:
{{
  "vulnerable_assumptions": ["assumption 1", "assumption 2"],
  "counter_narrative": "2-3 sentences: where could consensus be wrong?",
  "historical_counterexample": "One past event when consensus was wrong and what happened."
}}

Be specific. Cite a real historical counterexample when possible."""

CONSENSUS_PROMPT = """Aggregate these agent views into consensus signals by asset class.

Agent outputs: {agent_summary}

Output JSON only:
{{
  "signals_by_asset": {{ "rates": "up|down|neutral", "fx": "...", "equities": "...", "credit": "...", "commodities": "..." }},
  "consensus_strength": 0.0 to 1.0,
  "disagreement_score": 0.0 to 1.0,
  "debater_divergence": 0.0 to 1.0
}}"""

VALUATION_NARRATIVE_PROMPT = """Explain the macro-adjusted fair value change in 1-2 sentences.

Ticker: {ticker}
Baseline FV: {baseline_fv}
Adjusted FV: {adjusted_fv}
Delta %: {delta_pct}
Macro drivers: {macro_drivers}

Output plain text only, no JSON. Institutional tone."""
