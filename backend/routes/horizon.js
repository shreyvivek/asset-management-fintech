import { Router } from 'express';
import { getWatchlist, addToWatchlist, getHorizonView } from '../services/valuation.js';

export const horizonRouter = Router();

horizonRouter.get('/watchlist', (_, res) => {
  res.json({ watchlist: getWatchlist() });
});

horizonRouter.post('/watchlist', (req, res) => {
  const ticker = req.body?.ticker || req.query?.ticker;
  if (!ticker) return res.status(400).json({ error: 'ticker required' });
  const added = addToWatchlist(ticker);
  res.json({ watchlist: getWatchlist(), added });
});

horizonRouter.get('/view', async (_, res) => {
  try {
    const view = await getHorizonView();
    res.json({ view });
  } catch (e) {
    res.status(500).json({ error: e.message || 'Failed to build horizon view' });
  }
});
