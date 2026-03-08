import { Router } from 'express';
import { getEvents } from '../services/eventStore.js';

export const feedRouter = Router();

feedRouter.get('/', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit, 10) || 30, 100);
  const since = req.query.since || undefined;
  const events = getEvents(limit, since);
  res.json({ feed: events });
});
