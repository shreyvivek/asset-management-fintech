# MIVE — Macro-Intelligence & Valuation Engine

End-to-end macro-intelligence platform: **portfolio reallocation**, **LivePulse feed**, **MacroHeat Map**, **Horizon View**, and **multi-agent simulation** with institutional memory.

## Quick start

```bash
# Install root + frontend deps
npm run install:all

# Stop any process already using port 3001, then:
npm run dev
```

Open **http://localhost:5173**. Use the **Reallocation** tab for pie charts and metrics; use **Intelligence** for Heat Map, LivePulse feed (click any event for agent analysis), and Horizon View (add tickers, macro-adjusted fair values).

## What works end-to-end

- **Reallocation**: Current vs 2026 Resilient pie charts, live metrics (Reward, Risk, Sharpe), SAA/TAA table, sparklines.
- **MacroHeat Map**: Theme grid with heat scores and trajectory (Fed pivot, US inflation, EM currency, China growth, etc.).
- **LivePulse Feed**: Events from Fed RSS + Alpha Vantage; click an event to run a 6-agent simulation + Debater; risk chain and agent take shown below.
- **Horizon View**: Watchlist (default AAPL, MSFT, GOOGL); add tickers; macro-adjusted fair value and narrative per ticker (prices from Alpha Vantage when key set).
- **WebSocket**: Live metric/allocation updates every few seconds; optional feed/themes refresh every 5 min.

## Environment variables (.env)

Copy `.env.example` to `.env`. No keys are strictly required: missing keys use mocks (seed events, mock quotes, mock agent text).

| Variable | Purpose |
|----------|--------|
| `PORT` | Backend port (default 3001) |
| `ALPHA_VANTAGE_API_KEY` | Real GDP + GLOBAL_QUOTE; [get key](https://www.alphavantage.co/support/#api-key) |
| `OPENAI_API_KEY` | 6-agent + Debater simulation (otherwise mock responses) |

## Scripts

- `npm run dev` — backend (3001) + frontend (5173)  
- `npm run dev:backend` — backend only  
- `npm run dev:frontend` — frontend only (proxy /api to 3001)  
- `npm run build` — build frontend for production  
