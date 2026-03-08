import { Router } from 'express';
import { getThemes } from '../services/themes.js';

export const macroRouter = Router();

macroRouter.get('/themes', (req, res) => {
  const profile = req.query.profile || 'global_macro';
  const themes = getThemes(profile);
  res.json({ themes });
});
