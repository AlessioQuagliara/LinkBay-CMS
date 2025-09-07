const path = require('path');
const dotenv = require('dotenv');
dotenv.config({ path: path.resolve(__dirname, '../.env') });
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const expressLayouts = require('express-ejs-layouts');
const session = require('express-session');
const cookieParser = require('cookie-parser');

// Middleware per supportare PUT/DELETE nei form HTML
const methodOverride = require('method-override');

// Inizializza l'app Express
const app = express();

// Import routes e middleware
const { initDatabase } = require('./utils/dbInit');
const landingRoutes = require('./routes/landing');
//const userAuthRoutes = require('./routes/userAuth');
//const userDashboardRoutes = require('./routes/userDashboard');
//const adminAuthRoutes = require('./routes/adminAuth');
//const adminDashboardRoutes = require('./routes/adminDashboard');
//const emailRoutes = require('./routes/email');
//const visitRoutes = require('./routes/visit');
//const { authenticateToken } = require('./middleware/userAuth');
//const { authenticateAdmin } = require('./middleware/adminAuth');
//const companyRoutes = require('./routes/company');
//const eventRoutes = require('./routes/events');

// Import models for dashboard data
//const User = require('./models/User');
//const Admin = require('./models/Admin');
//const Message = require('./models/Message');
//const Visit = require('./models/Visit');

dotenv.config();

// Configurazione EJS per le views
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views'));
app.use(expressLayouts);
app.set('layout', 'layouts/main'); // Layout di default

// Configurazione middleware
app.use(cors());
app.use(express.static(path.join(__dirname, '../public')));
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cookieParser());

// Abilita l'override del metodo tramite query _method (necessario per i form che fanno PUT/DELETE)
app.use(methodOverride('_method'));

// Middleware per debug
app.use((req, res, next) => {
  console.log(`📩 Richiesta ricevuta: ${req.method} ${req.url}`);
  next();
});

// Configurazione sessione
app.use(session({
  secret: process.env.SESSION_SECRET || 'default-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false, // FORZA false in assenza di HTTPS
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000,
    sameSite: 'lax' // Aggiungi questa linea
  }
}));

// Simple flash middleware using session
app.use((req, res, next) => {
  res.locals.flash = req.session.flash || {};
  // clear flash after exposing
  delete req.session.flash;
  next();
});

// ==================== ROUTES PER PAGINE EJS ====================

// Redirect alle route di autenticazione esistenti
//app.get('/login', (req, res) => res.redirect('/auth/login'));
//app.get('/register', (req, res) => res.redirect('/auth/register'));
//app.get('/forgot-password', (req, res) => res.redirect('/auth/forgot-password'));
//app.get('/admin/login', (req, res) => res.redirect('/admin/auth/login'));
//app.get('/admin/register', (req, res) => res.redirect('/admin/auth/register'));

// Monta le route di autenticazione per il rendering EJS
//app.use('/auth', userAuthRoutes);
//app.use('/admin/auth', adminAuthRoutes);

// ==================== API ROUTES ====================


// API routes
//app.use('/api/auth', userAuthRoutes);
//app.use('/api/admin/auth', adminAuthRoutes);
//app.use('/api', emailRoutes);

// Visit tracker API
//app.use('/api', visitRoutes);
//app.use('/api/company', authenticateToken, companyRoutes);
//app.use('/api/events', eventRoutes);

// Route dashboard admin EJS
//app.use('/admin', authenticateAdmin, adminDashboardRoutes);
// Route pagine utente (dashboard, messages, events, settings)
//app.use('/', authenticateToken, userDashboardRoutes);

// ==================== GESTIONE ERRORI ====================

  // Gestione errori 404
  app.use((req, res) => {
    res.status(404).render('404', { 
      title: 'Pagina Non Trovata',
      layout: 'layouts/main'
    });
  });

// Gestione errori generici
app.use((err, req, res, next) => {
  console.error('❌ Errore:', err);
  res.status(500).render('error', {
    title: 'Errore del Server',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Si è verificato un errore',
    layout: 'layouts/main'
  });
});


// === SOCKET.IO SETUP ===
const { startSocketServer } = require('./socket');

startSocketServer(app, initDatabase);

module.exports = app;