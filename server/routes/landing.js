const express = require('express');
const router = express.Router();
const ejs = require('ejs');

async function renderWithLayout(name, req, res) {
  try {
    const routePath = name === 'home' ? '/' : `/${name}`;
    const title = name === 'home' ? 'LinkBay CMS' : (name.charAt(0).toUpperCase() + name.slice(1));

    // render the page template to a string
    const templatePath = path.join(__dirname, '..', '..', 'views', 'landing', `${name}.ejs`);
    const content = await ejs.renderFile(templatePath, { title, path: routePath }, { async: true });

    // render the layout and inject the content as `body`
    return res.render('landing/_layout', { layout: false, body: content, title, path: routePath });
  } catch (err) {
    console.error('Error rendering landing template', name, err);
    res.status(500).send('Server error');
  }
}

router.get('/', (req, res) => renderWithLayout('home', req, res));
router.get('/accept_invite', (req, res) => renderWithLayout('accept_invite', req, res));
router.get('/docs', (req, res) => renderWithLayout('docs', req, res));
router.get('/features', (req, res) => renderWithLayout('features', req, res));
router.get('/login', (req, res) => renderWithLayout('login', req, res));
router.get('/pricing', (req, res) => renderWithLayout('pricing', req, res));
router.get('/signup', (req, res) => renderWithLayout('signup', req, res));
router.get('/verify_mfa', (req, res) => renderWithLayout('verify_mfa', req, res));

module.exports = router;
