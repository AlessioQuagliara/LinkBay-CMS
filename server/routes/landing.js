const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  return res.render('landing/home', { title: 'LinkBay CMS' });
});

module.exports = router;
