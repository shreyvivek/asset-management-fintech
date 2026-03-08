import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
let memory = [];

function load() {
  try {
    const path = join(__dirname, '../data/memory.json');
    if (existsSync(path)) memory = JSON.parse(readFileSync(path, 'utf8'));
  } catch (_) {
    memory = [];
  }
}
load();

function score(a, b) {
  let s = 0;
  const at = (a.type || '').toLowerCase();
  const bt = (b.type || '').toLowerCase();
  if (at === bt) s += 2;
  const atitle = (a.title || '').toLowerCase();
  const bdesc = (b.description || b.title || '').toLowerCase();
  const words = atitle.split(/\s+/).filter((w) => w.length > 3);
  words.forEach((w) => {
    if (bdesc.includes(w) || (b.title || '').toLowerCase().includes(w)) s += 1;
  });
  return s;
}

export function getPrecedents(event, limit = 3) {
  const precedents = memory.map((p) => ({ ...p, _score: score(p, event) })).filter((p) => p._score > 0);
  precedents.sort((a, b) => b._score - a._score);
  return precedents.slice(0, limit).map(({ _score, ...p }) => p);
}
