import Parser from 'rss-parser';
import { addEvent } from './eventStore.js';

const parser = new Parser();

const THEME_KEYWORDS = {
  'fed-pivot': ['fed', 'powell', 'rate', 'fomc', 'taper', 'hike', 'cut', 'easing'],
  'us-inflation': ['cpi', 'inflation', 'pce', 'ppi', 'bls'],
  'em-currency': ['em', 'emerging', 'dxy', 'fx', 'currency', 'turkey', 'brazil', 'zar'],
  'china-growth': ['china', 'pboc', 'evergrande', 'property', 'growth'],
  'europe-rates': ['ecb', 'lagarde', 'euro', 'europe', 'boe'],
};

function classify(text) {
  const t = (text || '').toLowerCase();
  for (const [themeId, keywords] of Object.entries(THEME_KEYWORDS)) {
    if (keywords.some((k) => t.includes(k))) return themeId;
  }
  return 'global';
}

export async function ingestAlphaVantage() {
  const key = process.env.ALPHA_VANTAGE_API_KEY;
  if (!key) return [];
  const added = [];
  try {
    const url = `https://www.alphavantage.co/query?function=REAL_GDP&interval=annual&apikey=${key}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.data && data.data[0]) {
      const gdp = data.data[0];
      const ev = addEvent({
        type: 'macro_data',
        source: 'Alpha Vantage',
        title: `US Real GDP: ${gdp.value}% (${gdp.date})`,
        body: `Annual real GDP growth ${gdp.value}%.`,
        region: 'Americas',
        themeId: 'us-inflation',
      });
      added.push(ev);
    }
  } catch (e) {
    console.warn('Alpha Vantage ingest:', e.message);
  }
  return added;
}

export async function ingestFedRss() {
  const added = [];
  try {
    const feed = await parser.parseURL('https://www.federalreserve.gov/feeds/press_all.xml');
    const items = (feed.items || []).slice(0, 5);
    for (const item of items) {
      const title = item.title || '';
      const themeId = classify(title + (item.contentSnippet || ''));
      addEvent({
        type: 'central_bank',
        source: 'Federal Reserve',
        title,
        body: (item.contentSnippet || item.content || '').slice(0, 500),
        region: 'Americas',
        themeId,
        verified: true,
      });
      added.push({ title, themeId });
    }
  } catch (e) {
    console.warn('Fed RSS ingest:', e.message);
    seedMockEvents().forEach((m) => added.push(m));
  }
  return added;
}

function seedMockEvents() {
  const mock = [
    { title: 'Fed signals data-dependent path on rates', themeId: 'fed-pivot' },
    { title: 'CPI comes in above consensus for January', themeId: 'us-inflation' },
    { title: 'EM currencies under pressure as DXY strengthens', themeId: 'em-currency' },
  ];
  const added = [];
  mock.forEach((m) => {
    addEvent({
      type: 'macro',
      source: 'MIVE Seed',
      title: m.title,
      body: '',
      region: 'Global',
      themeId: m.themeId,
    });
    added.push(m);
  });
  return added;
}

export async function runIngestion() {
  const results = { alphaVantage: [], fed: [] };
  results.alphaVantage = await ingestAlphaVantage();
  results.fed = await ingestFedRss();
  if (results.fed.length === 0 && results.alphaVantage.length === 0) {
    results.fed = seedMockEvents();
  }
  return results;
}
