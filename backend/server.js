import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { portfolioRouter } from './routes/portfolio.js';
import { macroRouter } from './routes/macro.js';
import { feedRouter } from './routes/feed.js';
import { simulateRouter } from './routes/simulate.js';
import { horizonRouter } from './routes/horizon.js';
import { runIngestion } from './services/ingestion.js';
import { getThemes } from './services/themes.js';
import { getEvents } from './services/eventStore.js';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors({ origin: true }));
app.use(express.json());

app.use('/api/portfolio', portfolioRouter);
app.use('/api/macro', macroRouter);
app.use('/api/feed', feedRouter);
app.use('/api/simulate', simulateRouter);
app.use('/api/horizon', horizonRouter);

app.get('/api/health', (_, res) => res.json({ status: 'ok', ts: Date.now() }));

const server = createServer(app);
const wss = new WebSocketServer({ server });

// Live-update broadcast: push new metrics/allocation deltas periodically
const BROADCAST_INTERVAL_MS = 4000;
let clientId = 0;
const clients = new Set();

wss.on('connection', (ws) => {
  const id = ++clientId;
  clients.add(ws);
  ws.on('close', () => clients.delete(ws));
});

function broadcast(data) {
  const payload = JSON.stringify(data);
  clients.forEach((client) => {
    if (client.readyState === 1) client.send(payload);
  });
}

// Startup: run ingestion once to seed feed
runIngestion().then((r) => console.log('Ingestion:', Object.keys(r).join(', '))).catch((e) => console.warn('Ingestion:', e.message));

// Periodic ingestion (every 5 min) and broadcast feed/themes
const INGEST_INTERVAL_MS = 5 * 60 * 1000;
setInterval(() => {
  runIngestion().catch(() => {});
  const feed = getEvents(20);
  const themes = getThemes();
  broadcast({ type: 'feed_themes', feed, themes, ts: Date.now() });
}, INGEST_INTERVAL_MS);

// Simulate live macro-driven metric and allocation tweaks
let tick = 0;
import('./services/reallocation.js').then(({ getLiveMetrics, getLiveAllocation }) => {
  setInterval(() => {
    tick++;
    broadcast({
      type: 'live_update',
      metrics: getLiveMetrics(tick),
      recommended: getLiveAllocation(tick),
      ts: Date.now(),
    });
  }, BROADCAST_INTERVAL_MS);
});

server.listen(PORT, () => {
  console.log(`MIVE backend http+ws on http://localhost:${PORT}`);
});
