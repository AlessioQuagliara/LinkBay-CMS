"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const router = (0, express_1.Router)();
// Use explicit layout for landing routes
const layout = 'landing/_layout';
router.get('/', (req, res) => {
    res.render('landing/home', { title: 'Home', layout });
});
router.get('/login', (req, res) => {
    res.render('landing/login', { title: 'Login', layout });
});
router.get('/signup', (req, res) => {
    res.render('landing/signup', { title: 'Sign up', layout });
});
router.get('/pricing', (req, res) => {
    res.render('landing/pricing', { title: 'Pricing', layout });
});
router.get('/features', (req, res) => {
    res.render('landing/features', { title: 'Features', layout });
});
router.get('/docs', (req, res) => {
    res.render('landing/docs', { title: 'Documentation', layout });
});
exports.default = router;
