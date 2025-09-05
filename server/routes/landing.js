const express = require('express');
const router = express.Router();

function renderTemplate(name, req, res) {
  const routePath = name === 'home' ? '/' : `/${name}`;
  const title = name === 'home' ? 'LinkBay CMS' : (name.charAt(0).toUpperCase() + name.slice(1));
  return res.render(`landing/${name}`, { layout: 'landing/_layout', path: routePath, title });
}

router.get('/', (req, res) => renderTemplate('home', req, res));
router.get('/accept_invite', (req, res) => renderTemplate('accept_invite', req, res));
router.get('/docs', (req, res) => renderTemplate('docs', req, res));
router.get('/features', (req, res) => renderTemplate('features', req, res));
router.get('/login', (req, res) => renderTemplate('login', req, res));
router.get('/pricing', (req, res) => renderTemplate('pricing', req, res));
router.get('/signup', (req, res) => renderTemplate('signup', req, res));
router.get('/verify_mfa', (req, res) => renderTemplate('verify_mfa', req, res));

module.exports = router;
