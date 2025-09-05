const express = require('express');
const router = express.Router();

router.get('/dashboard', (req, res) => {
  const tenant = req.tenant || { name: 'default' };
  return res.render('tenant/dashboard', { tenant, title: 'Dashboard' });
});

module.exports = router;
