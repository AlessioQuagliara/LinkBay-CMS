import { Router, Request, Response } from 'express';
import speakeasy from 'speakeasy';
import { initDb } from '../../src/db';
import { sendMailTemplate } from '../utils/mailer';

const router = Router();

// Render accept invite page (simple form)
router.get('/accept-invite', async (req: Request, res: Response) => {
  const { token } = req.query as { token?: string };
  return res.render('landing/accept_invite', { token, title: 'Accetta Invito' });
});

// POST accept-invite: verify token, generate MFA secret, send verification email
router.post('/accept-invite', async (req: Request, res: Response) => {
  const { token } = req.body as { token?: string };
  if (!token) return res.status(400).json({ ok: false, error: 'token required' });

  try {
    const db = await initDb();
    const user = await db('users').where({ invite_token: token }).first();
    if (!user) return res.status(404).json({ ok: false, error: 'Invalid or expired token' });

    // generate MFA secret and save
    const secret = speakeasy.generateSecret({ length: 20 });
    await db('users').where({ id: user.id }).update({ mfa_secret: secret.base32, invite_token: null, invited_at: null });

    // load tenant
    const tenant = await db('tenants').where({ id: user.tenant_id }).first();

    // send MFA verification email using mailer
    const verifyLink = `${process.env.APP_URL || 'http://localhost:3001'}/verify-mfa?secret=${encodeURIComponent(secret.base32)}&tenant=${encodeURIComponent(tenant.name)}`;
    await sendMailTemplate(user.email, `Verifica MFA per ${tenant.name}`, 'mfa_verify', { tenantName: tenant.name, verifyLink });

    return res.json({ ok: true, message: 'MFA setup started, check your email' });
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('accept-invite error', err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

export default router;
