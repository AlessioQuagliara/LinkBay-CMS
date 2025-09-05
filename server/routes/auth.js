const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// POST /api/register
router.post('/register', authController.register);

// deprecated: auth endpoints will be reimplemented later
router.all('*', (req, res) => res.status(410).json({ ok: false, error: 'Auth endpoints not implemented' }));

module.exports = router;
