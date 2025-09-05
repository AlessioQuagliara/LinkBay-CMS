import { Router, Request, Response } from 'express';
import crypto from 'crypto';
import authenticateTenant from '../middleware/authenticateTenant';
import requireRole from '../middleware/requireRole';
import { initDb } from '../../src/db';
import { sendMailTemplate } from '../utils/mailer';
import { emailValidator, roleValidator, validate } from '../middleware/validators';

const router = Router();

// invite: owner or admin
router.post('/invite', authenticateTenant, requireRole(['owner', 'admin']), emailValidator, roleValidator, validate, async (req: Request, res: Response) => {
  const { email, role = 'member' } = req.body as { email?: string; role?: string };
  const tenant = (req as any).tenant;
  if (!email) return res.status(400).json({ ok: false, error: 'email required' });
  if (!['owner', 'admin', 'member'].includes(role)) return res.status(400).json({ ok: false, error: 'invalid role' });

  try {
    const db = await initDb();
    // ensure unique per tenant
    const existing = await db('users').where({ tenant_id: tenant.id, email }).first();
    if (existing) return res.status(409).json({ ok: false, error: 'User already exists' });

    const token = crypto.randomBytes(24).toString('hex');
    const invitedAt = new Date();

    const [user] = await db('users')
      .insert({ tenant_id: tenant.id, email, role, invite_token: token, invited_at: invitedAt })
      .returning('*');

    const acceptLink = `${process.env.APP_URL || 'http://localhost:3001'}/accept-invite?token=${encodeURIComponent(token)}`;
    await sendMailTemplate(email, `Invito per ${tenant.name}`, 'invite', { tenantName: tenant.name, acceptLink });

    return res.json({ ok: true, user });
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('invite error', err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

// remove: only owner
router.post('/remove', authenticateTenant, requireRole('owner'), async (req: Request, res: Response) => {
  const { userId } = req.body as { userId?: string };
  const tenant = (req as any).tenant;
  if (!userId) return res.status(400).json({ ok: false, error: 'userId required' });

  try {
    const db = await initDb();
    const target = await db('users').where({ id: userId, tenant_id: tenant.id }).first();
    if (!target) return res.status(404).json({ ok: false, error: 'User not found' });

    await db('users').where({ id: userId }).del();
    return res.json({ ok: true });
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('remove error', err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

export default router;
