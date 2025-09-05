import { Router, Request, Response } from 'express';
import authenticateTenant from '../middleware/authenticateTenant';

const router = Router();

router.get('/dashboard', authenticateTenant, (req: Request, res: Response) => {
  const tenant = (req as any).tenant;
  res.render('tenant/dashboard', { tenant, title: 'Dashboard' });
});

export default router;
