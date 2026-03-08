import { readFileSync, writeFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_PATH = join(__dirname, '../data/events.json');

let events = [];

function load() {
  try {
    if (existsSync(DATA_PATH)) {
      events = JSON.parse(readFileSync(DATA_PATH, 'utf8'));
    }
  } catch (_) {
    events = [];
  }
}

function save() {
  try {
    writeFileSync(DATA_PATH, JSON.stringify(events.slice(-500), null, 0));
  } catch (_) {}
}

load();

/** Ensure feed is never empty on first request (before async ingestion completes) */
function ensureSeed() {
  if (events.length > 0) return;
  const mock = [
    { type: 'macro', source: 'MIVE Seed', title: 'Fed signals data-dependent path on rates', body: '', region: 'Americas', themeId: 'fed-pivot' },
    { type: 'macro', source: 'MIVE Seed', title: 'CPI comes in above consensus for January', body: '', region: 'Americas', themeId: 'us-inflation' },
    { type: 'macro', source: 'MIVE Seed', title: 'EM currencies under pressure as DXY strengthens', body: '', region: 'Global', themeId: 'em-currency' },
  ];
  mock.forEach((m) => {
    const id = `ev_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    events.push({ id, timestamp: new Date().toISOString(), ...m });
  });
  save();
}

export function addEvent(ev) {
  const id = `ev_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const entry = { id, timestamp: new Date().toISOString(), ...ev };
  events.unshift(entry);
  save();
  return entry;
}

export function getEvents(limit = 50, since) {
  if (events.length === 0) ensureSeed();
  let out = events;
  if (since) out = out.filter((e) => e.timestamp > since);
  return out.slice(0, limit);
}

export function getEventById(id) {
  return events.find((e) => e.id === id);
}

export function getAllEvents() {
  return [...events];
}
