import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(__dirname, '../data/watchlist.json');
const defaultTickers = ['AAPL', 'MSFT', 'GOOGL'];

let watchlist = defaultTickers.slice();

function loadWatchlist() {
  try {
    const s = process.env.WATCHLIST || '';
    if (s) {
      watchlist = s.split(',').map((t) => t.trim()).filter(Boolean);
      return;
    }
    if (existsSync(DATA_PATH)) {
      watchlist = JSON.parse(readFileSync(DATA_PATH, 'utf8'));
    }
  } catch (_) {}
}
function saveWatchlist() {
  try {
    writeFileSync(DATA_PATH, JSON.stringify(watchlist));
  } catch (_) {}
}
loadWatchlist();

export function getWatchlist() {
  return [...watchlist];
}

export function addToWatchlist(ticker) {
  const t = (ticker || '').toUpperCase().trim();
  if (t && !watchlist.includes(t)) {
    watchlist.push(t);
    saveWatchlist();
    return true;
  }
  return false;
}

const SENSITIVITY = {
  AAPL: { rates: -0.05, usd: -0.02, growth: 0.08 },
  MSFT: { rates: -0.06, usd: -0.01, growth: 0.07 },
  GOOGL: { rates: -0.05, usd: -0.02, growth: 0.09 },
  TSLA: { rates: -0.09, usd: -0.03, growth: 0.12 },
  NVDA: { rates: -0.08, usd: -0.02, growth: 0.10 },
};

function getSensitivity(ticker) {
  return SENSITIVITY[ticker] || { rates: -0.05, usd: -0.02, growth: 0.06 };
}

export async function fetchQuote(ticker) {
  const key = process.env.ALPHA_VANTAGE_API_KEY;
  if (key) {
    try {
      const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${ticker}&apikey=${key}`;
      const res = await fetch(url);
      const data = await res.json();
      const q = data['Global Quote'];
      if (q && q['05. price']) {
        const price = parseFloat(q['05. price']);
        const change = parseFloat(q['09. change'] || 0);
        return { price, change, source: 'Alpha Vantage' };
      }
    } catch (_) {}
  }
  const mock = { AAPL: 225, MSFT: 420, GOOGL: 175, TSLA: 248, NVDA: 138 };
  const price = mock[ticker] || 100 + Math.random() * 50;
  return { price, change: 0, source: 'Mock' };
}

export async function getHorizonView() {
  const items = [];
  for (const ticker of watchlist) {
    const quote = await fetchQuote(ticker);
    const sens = getSensitivity(ticker);
    const macroAdj = 1 + sens.rates * 0.5 + sens.usd * 0.2;
    const baseFv = quote.price * 1.05;
    const macroFv = baseFv * macroAdj;
    const delta = ((macroFv - quote.price) / quote.price) * 100;
    items.push({
      ticker,
      currentPrice: quote.price,
      baseFairValue: baseFv,
      macroAdjustedFairValue: macroFv,
      deltaPct: delta,
      narrative: `Rates and USD moves imply ${delta >= 0 ? '+' : ''}${delta.toFixed(1)}% fair value adjustment vs. current price.`,
    });
  }
  return items;
}
