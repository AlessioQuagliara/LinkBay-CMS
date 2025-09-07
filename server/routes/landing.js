const express = require('express');

const router = express.Router();

// ================== RENDER PAGINE Landing ==================

// Redirect /index a /
router.get('/index', (req, res) => {
  res.redirect('/');
});

// Home page
router.get('/', (req, res) => {
  res.render('index', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Home Page',
      description: 'Benvenuto nella Home Page',
      keywords: 'home, page, welcome',
      sitoOnline
    }
  });
});

// Documentazione
router.get('/docs', (req, res) => {
  res.render('docs', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Documentazione',
      description: 'Scopri di più sulla nostra documentazione',
      keywords: 'documentazione, guide, API',
      sitoOnline
    }
  });
});

// Feature
router.get('/feature', (req, res) => {
  res.render('feature', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Feature',
      description: 'Scopri di più sulle nostre funzionalità',
      keywords: 'documentazione, guide, API',
      sitoOnline
    }
  });
});

// Prezzi
router.get('/pricing', (req, res) => {
  res.render('pricing', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Prezzi',
      description: 'Scopri di più sui nostri piani e prezzi',
      keywords: 'prezzi, costi, abbonamenti',
      sitoOnline
    }
  });
});

// login
router.get('/login', (req, res) => {
  res.render('login', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Login',
      description: 'Accedi al tuo account',
      keywords: 'login, accesso, autenticazione',
      sitoOnline
    }
  });
});

// signup
router.get('/signup', (req, res) => {
  res.render('signup', {
    layout: 'landing/_layout',
    SEO: {
      title: 'Signup',
      description: 'Crea un nuovo account',
      keywords: 'signup, registrazione, account',
      sitoOnline
    }
  });
});

