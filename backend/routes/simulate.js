import { Router } from 'express';
import { runSimulation } from '../services/agents.js';
import { getEventById } from '../services/eventStore.js';
import { addEvent } from '../services/eventStore.js';

export const simulateRouter = Router();

simulateRouter.post('/', async (req, res) => {
  try {
    const { eventId, event: eventPayload, portfolioProfile } = req.body || {};
    let event;
    if (eventId) {
      event = getEventById(eventId);
      if (!event) return res.status(404).json({ error: 'Event not found' });
    } else if (eventPayload && eventPayload.title) {
      event = addEvent({
        type: eventPayload.type || 'macro',
        source: eventPayload.source || 'User',
        title: eventPayload.title,
        body: eventPayload.body || '',
        region: eventPayload.region || 'Global',
        themeId: eventPayload.themeId || 'global',
      });
    } else {
      return res.status(400).json({ error: 'Provide eventId or event: { title, ... }' });
    }
    const result = await runSimulation(event, portfolioProfile || 'global_macro');
    res.json({ event, ...result });
  } catch (e) {
    console.error('Simulate error:', e);
    res.status(500).json({ error: e.message || 'Simulation failed' });
  }
});
