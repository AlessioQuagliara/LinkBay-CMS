import { Router, Request, Response } from 'express';
import passport from 'passport';
import { tenantNameValidator, providerValidator, validate } from '../middleware/validators';

const router = Router();

// POST /auth/preflight
router.post('/preflight', tenantNameValidator, providerValidator, validate, (req: Request, res: Response) => {
  const { tenantName, provider } = req.body as { tenantName?: string; provider?: string };

  // save tenantName in session
  (req.session as any).tenantName = tenantName;

  // redirect to provider auth start
  return res.redirect(`/auth/${provider}`);
});

// start oauth for provider
router.get('/:provider', (req: Request, res: Response, next) => {
  const provider = req.params.provider;
  if (provider === 'google') return passport.authenticate('google', { scope: ['profile', 'email'] })(req, res, next);
  if (provider === 'github') return passport.authenticate('github', { scope: ['user:email'] })(req, res, next);
  if (provider === 'microsoft') return passport.authenticate('azuread-openidconnect')(req, res, next);
  return res.status(400).json({ ok: false, error: 'Unknown provider' });
});

// callback
router.get('/:provider/callback', (req: Request, res: Response, next) => {
  const provider = req.params.provider;
  const handler = (err: any, user: any) => {
    // after passport handled, user info is in req.user normally
    // we'll just continue in the next middleware
  };

  if (provider === 'google') return passport.authenticate('google', { failureRedirect: '/login' })(req, res, next);
  if (provider === 'github') return passport.authenticate('github', { failureRedirect: '/login' })(req, res, next);
  if (provider === 'microsoft') return passport.authenticate('azuread-openidconnect', { failureRedirect: '/login' })(req, res, next);
  return res.status(400).json({ ok: false, error: 'Unknown provider' });
});

export default router;
