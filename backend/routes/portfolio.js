import { Router } from 'express';
import {
  getCurrentPortfolio,
  getRecommendedPortfolio,
  getReallocationTable,
  getLiveMetrics,
  getLiveAllocation,
  getAssetColors,
} from '../services/reallocation.js';

export const portfolioRouter = Router();

portfolioRouter.get('/current', (_, res) => {
  res.json({ allocation: getCurrentPortfolio(), colors: getAssetColors() });
});

portfolioRouter.get('/recommended', (_, res) => {
  res.json({
    allocation: getRecommendedPortfolio(),
    colors: getAssetColors(),
  });
});

portfolioRouter.get('/recommended/live', (_, res) => {
  const tick = Math.floor(Date.now() / 4000);
  res.json({
    allocation: getLiveAllocation(tick),
    colors: getAssetColors(),
  });
});

portfolioRouter.get('/reallocation-table', (_, res) => {
  res.json({ rows: getReallocationTable() });
});

portfolioRouter.get('/metrics', (_, res) => {
  const tick = Math.floor(Date.now() / 4000);
  res.json(getLiveMetrics(tick));
});
