import { Router } from 'express';
import { knex } from '../db';
import { jwtAuth } from '../middleware/jwtAuth';

const router = Router();

// GET status
router.get('/onboarding-status', jwtAuth, async (req, res) => {
  const user = (req as any).user;
  if (!user) return res.status(401).json({ error: 'unauthenticated' });
  const row = await knex('users').where({ id: user.id }).first();
  res.json({ onboarding_completed: row?.onboarding_completed || false });
});

// POST mark completed
router.post('/onboarding-status', jwtAuth, async (req, res) => {
  const user = (req as any).user;
  if (!user) return res.status(401).json({ error: 'unauthenticated' });
  await knex('users').where({ id: user.id }).update({ onboarding_completed: true });
  res.json({ onboarding_completed: true });
});

export default router;
