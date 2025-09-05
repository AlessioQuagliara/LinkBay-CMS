const express = require('express');
const fs = require('fs');
const path = require('path');

const router = express.Router();

const viewsDir = path.join(__dirname, '..', '..', 'views', 'landing');

function getTemplates() {
  try {
    const files = fs.readdirSync(viewsDir);
    return files.filter(f => f.endsWith('.ejs') && f !== '_layout.ejs').map(f => f.replace(/\.ejs$/, ''));
  } catch (err) {
    console.error('Error reading landing views', err);
    return [];
  }
}

const templates = getTemplates();

templates.forEach(name => {
  const routePath = name === 'home' ? '/' : `/${name}`;
  router.get(routePath, (req, res) => {
    // render using landing/_layout as layout
    res.render(`landing/${name}`, { layout: 'landing/_layout', path: routePath });
  });
});

module.exports = router;
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  return res.render('landing/home', { title: 'LinkBay CMS' });
});

module.exports = router;
