import { Router } from 'express';
import { jwtAuth } from '../middleware/jwtAuth';

const router = Router();

// tenant dashboard pages require auth
router.get('/analytics', jwtAuth, async (req:any, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).send('tenant required');
  res.render('admin_analytics', { tenant });
});

export default router;
