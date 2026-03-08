/**
 * Macro-driven portfolio reallocation logic.
 * Uses theme heat and external data (when APIs configured) to suggest TAA vs SAA.
 */

const ASSET_COLORS = {
  US: '#B91C1C',
  Bonds: '#EA580C',
  Europe: '#C2410C',
  'Private Markets': '#7C2D12',
  Singapore: '#E11D48',
  'Hong Kong': '#9F1239',
  Cash: '#FDA4AF',
};

const BASE_CURRENT = {
  US: 70,
  Cash: 20,
  Bonds: 5,
  Singapore: 3,
  'Hong Kong': 2,
};

const BASE_RECOMMENDED = {
  US: 35,
  Bonds: 20,
  Europe: 20,
  'Private Markets': 12,
  Singapore: 10,
  Cash: 3,
};

const REALLOCATION_TABLE = [
  {
    assetClass: 'Fixed Income (Bonds)',
    saa: 30,
    taa: 20,
    reasoning: 'Investing in 5% yields before the Fed easing cycle compresses rates further.',
  },
  {
    assetClass: 'Alternatives (Private Mkt)',
    saa: 5,
    taa: 12,
    reasoning: 'Replaces low-yield cash with 8.5% senior secured income.',
  },
  {
    assetClass: 'Cash & Equivalents',
    saa: 5,
    taa: 3,
    reasoning: 'Minimum liquidity to reduce the cash drag on $80M.',
  },
];

function normalizeAlloc(alloc) {
  const total = Object.values(alloc).reduce((s, v) => s + v, 0);
  if (total === 0) return alloc;
  const f = 100 / total;
  const out = {};
  for (const [k, v] of Object.entries(alloc)) out[k] = Math.round(v * f * 10) / 10;
  return out;
}

/** Small live wiggle around base recommended allocation (economics-friendly simulation) */
export function getLiveAllocation(tick) {
  const wiggle = 0.15 * Math.sin(tick * 0.5) + 0.1 * Math.sin(tick * 0.3);
  const alloc = { ...BASE_RECOMMENDED };
  alloc.US = Math.max(30, Math.min(40, BASE_RECOMMENDED.US + wiggle * 5));
  alloc.Bonds = Math.max(18, Math.min(24, BASE_RECOMMENDED.Bonds - wiggle * 2));
  alloc.Cash = Math.max(2, Math.min(5, BASE_RECOMMENDED.Cash + wiggle));
  return normalizeAlloc(alloc);
}

/** Live metrics with small changes (reward, risk, sharpe) */
export function getLiveMetrics(tick) {
  const drift = 0.02 * Math.sin(tick * 0.4);
  return {
    reward: 7.45 + drift * 0.2,
    rewardDelta: -0.25 + drift * 0.05,
    risk: 10.5 - Math.abs(drift) * 0.3,
    riskDelta: -2.07 + drift * 0.1,
    sharpe: 0.31 + drift * 0.01,
    sharpeDelta: 0.02 + drift * 0.005,
  };
}

export function getCurrentPortfolio() {
  return { ...BASE_CURRENT };
}

export function getRecommendedPortfolio() {
  return { ...BASE_RECOMMENDED };
}

export function getReallocationTable() {
  return REALLOCATION_TABLE.map((r) => ({ ...r }));
}

export function getAssetColors() {
  return { ...ASSET_COLORS };
}
