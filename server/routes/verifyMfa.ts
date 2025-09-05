import { Router, Request, Response } from 'express';
import speakeasy from 'speakeasy';
import { initDb } from '../../src/db';

const router = Router();

router.get('/verify-mfa', (req: Request, res: Response) => {
  const { secret, tenant } = req.query as { secret?: string; tenant?: string };
  return res.render('landing/verify_mfa', { secret, tenant, title: 'Verifica MFA' });
});

router.post('/verify-mfa', async (req: Request, res: Response) => {
  const { secret, token } = req.body as { secret?: string; token?: string };
  if (!secret || !token) return res.status(400).json({ ok: false, error: 'secret and token required' });

  const verified = speakeasy.totp.verify({ secret, encoding: 'base32', token, window: 1 });
  if (!verified) return res.status(400).json({ ok: false, error: 'Invalid token' });

  try {
    const db = await initDb();
    // find user with this mfa secret
    const user = await db('users').where({ mfa_secret: secret }).first();
    if (!user) return res.status(404).json({ ok: false, error: 'User not found' });

    await db('users').where({ id: user.id }).update({ mfa_verified: true });

    // create session: store user id and tenant in session
    (req.session as any).userId = user.id;
    (req.session as any).tenantName = (await db('tenants').where({ id: user.tenant_id }).first()).name;

    // redirect to tenant dashboard
    return res.redirect('/tenant/dashboard');
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('verify-mfa error', err);
    return res.status(500).json({ ok: false, error: err.message });
  }
});

export default router;
