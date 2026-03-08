import { getAllEvents } from './eventStore.js';

const THEME_NAMES = {
  'fed-pivot': 'Fed Pivot Expectations',
  'us-inflation': 'US Inflation Cycle',
  'em-currency': 'EM Currency Pressure',
  'china-growth': 'China Growth Slowdown',
  'europe-rates': 'Europe Rates',
  global: 'Global Macro',
};

const REGIONS = { 'fed-pivot': 'Americas', 'us-inflation': 'Americas', 'em-currency': 'Global', 'china-growth': 'Asia-Pacific', 'europe-rates': 'Europe', global: 'Global' };

const MS_48H = 48 * 60 * 60 * 1000;

export function getThemes(portfolioProfile = 'global_macro') {
  const events = getAllEvents();
  const now = Date.now();
  const window = events.filter((e) => {
    const t = new Date(e.timestamp).getTime();
    return now - t < MS_48H;
  });

  const byTheme = {};
  window.forEach((e) => {
    const id = e.themeId || 'global';
    if (!byTheme[id]) byTheme[id] = [];
    byTheme[id].push(e);
  });

  const themes = Object.entries(byTheme).map(([id, evs]) => {
    const count = evs.length;
    const velocity = count / (48 / 24);
    const heat = Math.min(100, Math.round(30 + velocity * 12 + (evs.length > 2 ? 20 : 0)));
    const trajectory = heat >= 65 ? 'heating' : heat >= 40 ? 'stable' : 'cooling';
    return {
      id,
      name: THEME_NAMES[id] || id,
      region: REGIONS[id] || 'Global',
      heat: Math.min(100, heat + (id === 'fed-pivot' ? 5 : 0)),
      trajectory,
      eventCount: evs.length,
    };
  });

  const defaultThemes = [
    { id: 'fed-pivot', name: 'Fed Pivot Expectations', heat: 72, trajectory: 'heating', region: 'Americas', eventCount: 0 },
    { id: 'em-currency', name: 'EM Currency Pressure', heat: 58, trajectory: 'stable', region: 'Global', eventCount: 0 },
    { id: 'us-inflation', name: 'US Inflation Cycle', heat: 65, trajectory: 'cooling', region: 'Americas', eventCount: 0 },
    { id: 'china-growth', name: 'China Growth Slowdown', heat: 44, trajectory: 'stable', region: 'Asia-Pacific', eventCount: 0 },
  ];

  const merged = new Map(defaultThemes.map((t) => [t.id, { ...t }]));
  themes.forEach((t) => merged.set(t.id, t));
  return Array.from(merged.values());
}
