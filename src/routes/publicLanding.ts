import { Router } from 'express';

const router = Router();

router.get('/', (req, res) => {
  res.render('landing/home', { layout: 'landing/_layout', title: 'LinkBay CMS — Welcome' });
});

router.get('/features', (req, res) => {
  res.render('landing/features', { layout: 'landing/_layout', title: 'Features — LinkBay CMS' });
});

router.get('/pricing', (req, res) => {
  res.render('landing/pricing', { layout: 'landing/_layout', title: 'Pricing — LinkBay CMS' });
});

router.get('/login', (req, res) => {
  res.render('landing/login', { layout: 'landing/_layout', title: 'Login — LinkBay CMS' });
});

router.get('/signup', (req, res) => {
  res.render('landing/signup', { layout: 'landing/_layout', title: 'Sign up — LinkBay CMS' });
});

// simple redirector to tenant subdomain for login (GET form target)
router.get('/login-redirect', (req, res) => {
  const tenant = (req.query.tenant || '').toString().trim();
  if (!tenant) return res.redirect('/login');
  // redirect to tenant subdomain (assume same base domain)
  const target = `http://${tenant}.yoursite-linkbay-cms.com`;
  res.redirect(target);
});

// simple signup handler (creates tenant) - lightweight placeholder
router.post('/signup', async (req, res) => {
  const { subdomain, email, password } = req.body as any;
  if (!subdomain || !email || !password) return res.status(400).send('missing');
  // NOTE: real implementation should validate, create tenant record, hashed password, send confirmation, etc.
  // For now redirect to a success page or to the tenant subdomain
  return res.redirect(`http://${subdomain}.yoursite-linkbay-cms.com`);
});

export default router;
