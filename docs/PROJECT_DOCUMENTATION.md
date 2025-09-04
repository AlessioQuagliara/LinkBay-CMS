Documentazione Tecnica Completa — LinkBay CMS

Sommario
Panoramica e Architettura

Requisiti di Sistema

Setup e Installazione
3.1. Struttura del Repository
3.2. Configurazione dell'Ambiente
3.3. Inizializzazione del Database

Sviluppo Locale
4.1. Build e Avvio
4.2. Domini di Sviluppo (lvh.me)

Architettura Multitenant
5.1. Risoluzione del Tenant
5.2. Isolamento dei Dati

Flussi di Autenticazione
6.1. Panoramica dei Flussi
6.2. Landing Pubblica e Login Cross-Domain
6.3. OAuth2 (Google, GitHub)
6.4. SAML 2.0
6.5. Autenticazione JWT

Debugging e Troubleshooting
7.1. Problemi Comuni
7.2. Comandi di Debug Rapidi

File Chiave e Punti di Estensione

Monitoraggio e Observability (Sentry)

Workflow di Sviluppo

Deployment e Produzione

1. Panoramica e Architettura ///////////////////////////////////////////////////////////////////////////

LinkBay CMS è una piattaforma SaaS multitenant completa costruita con Node.js e TypeScript. L'architettura segue il pattern "schema-per-tenant" su PostgreSQL, garantendo un forte isolamento dei dati.

Componenti Principali:

Backend: Express.js con TypeScript

Database: PostgreSQL con schemi multipli

Frontend: EJS per SSR, Tailwind CSS, Alpine.js, HTMX

Autenticazione: JWT, OAuth2, SAML 2.0

Pagamenti: Stripe Connect, PayPal Multiparty

Editor: GrapesJS + CodeMirror

Pattern di Deployment:

Landing Pubblica (linkbay-cms.com): Sito marketing, login, registrazione.

Backoffice Tenant ([tenant].yoursite-linkbay-cms.com): Applicazione CMS isolata per ogni cliente.

2. Requisiti di Sistema ///////////////////////////////////////////////////////////////////////////
Node.js: 18.x o superiore

PostgreSQL: 12.x o superiore

npm: 8.x o superiore

Redis: 6.x (per caching e sessioni)

Memoria: Minimo 2GB RAM consigliati

Spazio Disco: Minimo 5GB liberi

3. Setup e Installazione ///////////////////////////////////////////////////////////////////////////
3.1. Struttura del Repository ---------------------------------------------------------------
/LINKBAY-CMS
.
├── backups
│   └── saml_changes_20250902.txt
├── certs
│   ├── test-idp-cert.pem
│   └── test-idp-key.pem
├── dist
│   ├── app.js
│   ├── cache
│   │   └── index.js
│   ├── controllers
│   │   └── pageController.js
│   ├── db.js
│   ├── dbMultiTenant.js
│   ├── graphql
│   │   ├── index.js
│   │   ├── resolvers.js
│   │   └── schema.js
│   ├── i18n.js
│   ├── lib
│   │   ├── abTest.js
│   │   ├── analyticsConsumer.js
│   │   ├── eventBus.js
│   │   ├── hookRegistry.js
│   │   ├── simpleCache.js
│   │   ├── tenantResourceLimits.js
│   │   ├── webhookConsumer.js
│   │   └── workerTask.js
│   ├── middleware
│   │   ├── abTests.js
│   │   ├── audit.js
│   │   ├── authorize.js
│   │   ├── contentLang.js
│   │   ├── cookieConsent.js
│   │   ├── dynamicCors.js
│   │   ├── enforceStorageQuota.js
│   │   ├── jwtAuth.js
│   │   ├── partialCache.js
│   │   ├── permissions.js
│   │   ├── rateLimiters.js
│   │   ├── requireApiKey.js
│   │   ├── resolveTenant.js
│   │   ├── tenantApiTimeout.js
│   │   ├── tenantRateLimiter.js
│   │   ├── tenantResolver.js
│   │   └── trackBandwidth.js
│   ├── models
│   │   ├── refreshToken.js
│   │   ├── tenant.js
│   │   └── user.js
│   ├── plugins
│   │   ├── loader.js
│   │   ├── pluginWorker.js
│   │   ├── router.js
│   │   ├── sandbox.js
│   │   └── types.js
│   ├── routes
│   │   ├── admin.js
│   │   ├── adminAnonymize.js
│   │   ├── adminDataExport.js
│   │   ├── analytics.js
│   │   ├── api
│   │   │   └── v1
│   │   │       └── tenantProducts.js
│   │   ├── auth.js
│   │   ├── blockTemplates.js
│   │   ├── cart.js
│   │   ├── contentAudit.js
│   │   ├── conversations.js
│   │   ├── dashboard.js
│   │   ├── editor.js
│   │   ├── editorApi.js
│   │   ├── health.js
│   │   ├── integrations.js
│   │   ├── marketplace.js
│   │   ├── menus.js
│   │   ├── oauth.js
│   │   ├── onboarding.js
│   │   ├── pages.js
│   │   ├── pluginActivity.js
│   │   ├── products.js
│   │   ├── publicAuth.js
│   │   ├── publicIntegrations.js
│   │   ├── publicLanding.js
│   │   ├── roles.js
│   │   ├── saml.js
│   │   ├── scheduledReports.js
│   │   ├── settings.js
│   │   ├── ssr.js
│   │   ├── status.js
│   │   ├── stripe.js
│   │   ├── subprocessors.js
│   │   ├── tenantCookieConsent.js
│   │   ├── tenantDpia.js
│   │   ├── tenantHealth.js
│   │   ├── tenantSettings.js
│   │   ├── tenantUsage.js
│   │   ├── userPreferences.js
│   │   ├── userRoles.js
│   │   └── zapier.js
│   ├── server.js
│   ├── services
│   │   ├── auth.js
│   │   ├── mailer.js
│   │   └── tenant.js
│   ├── socket
│   │   └── index.js
│   └── types
│       └── events.js
├── docker-compose.yml
├── Dockerfile
├── docs
│   ├── backup_restore.md
│   ├── graphql.md
│   ├── PROJECT_DOCUMENTATION.md
│   ├── retention.md
│   └── saml_local_setup.md
├── knexfile.ts
├── LICENSE
├── locales
│   ├── en
│   │   └── common.json
│   ├── es
│   │   └── common.json
│   └── it
│       └── common.json
├── migrations
│   ├── 20250902_add_indexes.ts
│   ├── 20250902_add_onboarding_to_users.ts
│   ├── 20250902_add_page_language.ts
│   ├── 20250902_add_sso_login_url_to_tenant_saml_providers.ts
│   ├── 20250902_add_subscriptions_and_invoices.ts
│   ├── 20250902_add_tracking_scripts_to_tenant_settings.ts
│   ├── 20250902_create_ab_assignments.ts
│   ├── 20250902_create_ab_tests.ts
│   ├── 20250902_create_analytics_schema.ts
│   ├── 20250902_create_audit_logs.ts
│   ├── 20250902_create_base_tables.ts
│   ├── 20250902_create_block_templates.ts
│   ├── 20250902_create_menus.ts
│   ├── 20250902_create_pages_table.ts
│   ├── 20250902_create_plugins_and_tenant_plugins.ts
│   ├── 20250902_create_product_variants_and_attributes.ts
│   ├── 20250902_create_rbac_tables.ts
│   ├── 20250902_create_scheduled_reports.ts
│   ├── 20250902_create_tenant_conversations_function.ts
│   ├── 20250902_create_tenant_ecommerce_function.ts
│   ├── 20250902_create_tenant_schema_function.ts
│   ├── 20250902_create_tenant_settings.ts
│   ├── 20250902_create_user_preferences.ts
│   ├── 20250903_create_api_keys.ts
│   ├── 20250903_create_public_integrations.ts
│   ├── 20250903_create_tenant_integrations_and_sync_logs.ts
│   ├── 20250903_create_tenant_oauth_providers.ts
│   ├── 20250903_create_tenant_saml_providers.ts
│   ├── 20250903_create_tenant_webhooks_and_logs.ts
│   ├── 20250903_create_zapier_oauth_tables.ts
│   ├── 20250904_create_plugins_tables.ts
│   ├── 20250905_update_available_plugins_add_version_constraints.ts
│   ├── 20250906_create_media_and_tenant_quota.ts
│   ├── 20250907_create_plugin_logs.ts
│   ├── 20250908_add_soft_delete_anonymize.ts
│   ├── 20250909_create_tenant_cookie_consent.ts
│   ├── 20250910_create_content_audit.ts
│   ├── 20250911_add_data_residency_to_tenants.ts
│   ├── 20250911_create_retention_policies.ts
│   ├── 20250911_create_subprocessors.ts
│   └── 20250912_create_api_keys_and_webhooks.ts
├── nginx
│   └── default.conf
├── package-lock.json
├── package.json
├── packages
│   └── plugin-sdk
│       ├── lib
│       │   ├── index.d.ts
│       │   └── index.js
│       ├── package.json
│       ├── README.md
│       ├── src
│       │   └── index.ts
│       └── tsconfig.json
├── plugins
├── postcss.config.js
├── public
│   ├── css
│   │   └── main.css
│   └── media
│       ├── android-chrome-192x192.png
│       ├── android-chrome-512x512.png
│       ├── apple-touch-icon.png
│       ├── favicon-16x16.png
│       ├── favicon-32x32.png
│       ├── favicon.ico
│       ├── google.png
│       ├── klaviyo.png
│       ├── lb-logo-w.svg
│       ├── linkbay_logo.svg
│       ├── mailchimp.png
│       ├── meta.png
│       ├── og-image.svg
│       ├── stripe.png
│       ├── twilio.png
│       ├── zapier.png
│       └── zendesk.png
├── README.md
├── scripts
│   ├── backup.sh
│   ├── fake-idp.js
│   ├── generate_api_key.ts
│   ├── hard_delete_expired.ts
│   ├── restore.sh
│   ├── retention_cleanup.ts
│   ├── run_scheduled_reports.ts
│   ├── setup_tenant_domain.js
│   └── setup_tenant_domain.sh
├── seeds
│   └── 01_tenant_and_admin.ts
├── src
│   ├── app.ts
│   ├── cache
│   │   └── index.ts
│   ├── controllers
│   │   └── pageController.ts
│   ├── css
│   │   └── input.css
│   ├── db.ts
│   ├── dbMultiTenant.ts
│   ├── graphql
│   │   ├── index.ts
│   │   ├── resolvers.ts
│   │   └── schema.ts
│   ├── i18n.ts
│   ├── lib
│   │   ├── abTest.ts
│   │   ├── analyticsConsumer.ts
│   │   ├── eventBus.ts
│   │   ├── hookRegistry.ts
│   │   ├── simpleCache.ts
│   │   ├── tenantResourceLimits.ts
│   │   ├── webhookConsumer.ts
│   │   └── workerTask.ts
│   ├── middleware
│   │   ├── abTests.ts
│   │   ├── audit.ts
│   │   ├── authorize.ts
│   │   ├── contentLang.ts
│   │   ├── cookieConsent.ts
│   │   ├── dynamicCors.ts
│   │   ├── enforceStorageQuota.ts
│   │   ├── jwtAuth.ts
│   │   ├── partialCache.ts
│   │   ├── permissions.ts
│   │   ├── rateLimiters.ts
│   │   ├── requireApiKey.ts
│   │   ├── resolveTenant.ts
│   │   ├── tenantApiTimeout.ts
│   │   ├── tenantRateLimiter.ts
│   │   ├── tenantResolver.ts
│   │   └── trackBandwidth.ts
│   ├── models
│   │   ├── refreshToken.ts
│   │   ├── tenant.ts
│   │   └── user.ts
│   ├── plugins
│   │   ├── loader.ts
│   │   ├── pluginWorker.ts
│   │   ├── router.ts
│   │   ├── sandbox.ts
│   │   └── types.ts
│   ├── routes
│   │   ├── admin.ts
│   │   ├── adminAnonymize.ts
│   │   ├── adminDataExport.ts
│   │   ├── analytics.ts
│   │   ├── api
│   │   │   └── v1
│   │   │       └── tenantProducts.ts
│   │   ├── auth.ts
│   │   ├── blockTemplates.ts
│   │   ├── cart.ts
│   │   ├── contentAudit.ts
│   │   ├── conversations.ts
│   │   ├── dashboard.ts
│   │   ├── editor.ts
│   │   ├── editorApi.ts
│   │   ├── health.ts
│   │   ├── integrations.ts
│   │   ├── marketplace.ts
│   │   ├── menus.ts
│   │   ├── oauth.ts
│   │   ├── onboarding.ts
│   │   ├── pages.ts
│   │   ├── pluginActivity.ts
│   │   ├── products.ts
│   │   ├── publicAuth.ts
│   │   ├── publicIntegrations.ts
│   │   ├── publicLanding.ts
│   │   ├── roles.ts
│   │   ├── saml.ts
│   │   ├── scheduledReports.ts
│   │   ├── settings.ts
│   │   ├── ssr.ts
│   │   ├── status.ts
│   │   ├── stripe.ts
│   │   ├── subprocessors.ts
│   │   ├── tenantCookieConsent.ts
│   │   ├── tenantDpia.ts
│   │   ├── tenantHealth.ts
│   │   ├── tenantSettings.ts
│   │   ├── tenantUsage.ts
│   │   ├── userPreferences.ts
│   │   ├── userRoles.ts
│   │   └── zapier.ts
│   ├── server.ts
│   ├── services
│   │   ├── auth.ts
│   │   ├── mailer.ts
│   │   └── tenant.ts
│   ├── socket
│   │   └── index.ts
│   └── types
│       ├── events.ts
│       ├── express-ejs-layouts.d.ts
│       └── global.d.ts
├── tailwind.config.js
├── tests
│   ├── jest.setup.ts
│   ├── unit
│   │   └── auth-utils.test.ts
│   └── utils
│       └── testDb.ts
├── tsconfig.json
├── views
│   ├── admin_analytics.ejs
│   ├── admin_menus.ejs
│   ├── admin.ejs
│   ├── auth
│   │   ├── login.ejs
│   │   └── register.ejs
│   ├── dashboard
│   │   └── index.ejs
│   ├── editor
│   │   └── [pageId].ejs
│   ├── editor.ejs
│   ├── email
│   │   └── report_summary.ejs
│   ├── error
│   │   └── tenant-not-found.ejs
│   ├── index.ejs
│   ├── integration_configure.ejs
│   ├── landing
│   │   ├── _layout.ejs
│   │   ├── features.ejs
│   │   ├── home.ejs
│   │   ├── login.ejs
│   │   ├── pricing.ejs
│   │   └── signup.ejs
│   ├── layouts
│   │   └── boilerplate.ejs
│   ├── legal
│   │   └── subprocessors.ejs
│   ├── partials
│   │   ├── components
│   │   │   ├── button.ejs
│   │   │   ├── card.ejs
│   │   │   ├── cart.ejs
│   │   │   ├── dark-toggle.ejs
│   │   │   ├── delete-button.ejs
│   │   │   ├── dropdown.ejs
│   │   │   ├── input.ejs
│   │   │   ├── modal.ejs
│   │   │   ├── multi-step-form.ejs
│   │   │   ├── product-filters.ejs
│   │   │   └── tabs.ejs
│   │   ├── cookie-banner.ejs
│   │   ├── dashboard-card.ejs
│   │   ├── flash-messages.ejs
│   │   ├── footer.ejs
│   │   ├── form-errors.ejs
│   │   ├── header.ejs
│   │   ├── menu.ejs
│   │   ├── navbar.ejs
│   │   └── product-form.ejs
│   ├── products
│   │   ├── index.ejs
│   │   └── partials
│   │       ├── row.ejs
│   │       ├── rows.ejs
│   │       └── table.ejs
│   ├── settings
│   │   ├── api-keys.ejs
│   │   ├── partials
│   │   │   └── webhook-row.ejs
│   │   ├── sso.ejs
│   │   └── webhooks.ejs
│   ├── status.ejs
│   └── tenant
│       ├── dashboard.ejs
│       ├── layout.ejs
│       └── pages.ejs
└── workflows
    └── ci-cd.yml

3.2. Configurazione dell'Ambiente ---------------------------------------------------------------
Crea un file .env nella root del progetto:
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/linkbay_dev
REDIS_URL=redis://localhost:6379

# Server
NODE_ENV=development
PORT=3001
APP_URL=http://lvh.me:3001
SESSION_SECRET=your-super-secret-session-key

# JWT
JWT_SECRET=your-jwt-secret-key
JWT_REFRESH_SECRET=your-jwt-refresh-secret-key

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (per notifiche)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

3.3. Inizializzazione del Database ---------------------------------------------------------------

# Creazione database
createdb linkbay_dev

# Esecuzione migrazioni
npx knex migrate:latest --knexfile knexfile.ts

# Esecuzione seed iniziali
npx knex seed:run --knexfile knexfile.ts

# 4. Sviluppo Locale ////////////////////////////////////////////////////////////////////////////////
# 4.1. Build e Avvio ---------------------------------------------------------------

## Quick start (sviluppo locale)

1. Copia il file degli esempi di env e modifica i valori sensibili (NON cancellare i segreti già presenti in `.env`):

  cp .env.example .env

  (Modifica `.env` con DATABASE_URL, GOOGLE_CLIENT_ID/SECRET, GITHUB_CLIENT_ID/SECRET, ecc.)

2. Installa dipendenze:

  npm install

3. Crea il database, esegui migrazioni e seed:

  createdb linkbay_dev
  npx knex migrate:latest --knexfile knexfile.ts
  npx knex seed:run --knexfile knexfile.ts

4. Imposta l'URL di sviluppo (es. usando lvh.me per wildcard subdomains):

  export APP_URL=http://lvh.me:3001

5. Avvia in sviluppo (watch):

  npm run dev

6. Build per produzione e avvio:

  npm run build
  npm start

Se vuoi avviare l'applicazione direttamente dal build compilato (utile dopo `npm run build`):

  node dist/server.js

Nota: non eliminare il file `.env` né i segreti in esso contenuti; se stai lavorando in team, usa un secrets manager o condividi valori in modo sicuro.

4.2. Domini di Sviluppo ---------------------------------------------------------------
Per testing dei subdomini in locale, utilizzare lvh.me (che risolve a 127.0.0.1):

export APP_URL=http://lvh.me:3001
npm run dev

Accedi poi a:

Landing: http://lvh.me:3001

Tenant "default": http://default.lvh.me:3001

5. Architettura Multitenant ///////////////////////////////////////////////////////////////////////
5.1. Risoluzione del Tenant ---------------------------------------------------------------
Il middleware src/middleware/tenantResolver.ts estrae il subdominio dalla richiesta e cerca il tenant corrispondente nel database:

// Esempio semplificato del middleware
const resolveTenant = async (req: Request, res: Response, next: NextFunction) => {
  const subdomain = req.subdomains[0] || 'default';
  
  try {
    const tenant = await TenantService.findBySubdomain(subdomain);
    if (!tenant) {
      return res.status(404).render('error/tenant-not-found');
    }
    
    req.tenant = tenant;
    next();
  } catch (error) {
    next(error);
  }
};

5.2. Isolamento dei Dati ---------------------------------------------------------------
  "start": "node dist/server.js",

6. Flussi di Autenticazione ///////////////////////////////////////////////////////////////////////
6.1. Panoramica dei Flussi ---------------------------------------------------------------

sequenceDiagram
    participant User
    participant Landing as Landing (linkbay-cms.com)
    participant Tenant as Tenant Backoffice (tenant.lvh.me)
    participant Provider as OAuth Provider (Google/GitHub)

    User->>Landing: Clicca "Login"
    Landing->>Landing: POST /api/auth/provider-redirect
    Landing-->>User: {redirect: "tenant.lvh.me/auth/google"}
    User->>Tenant: GET /auth/google
    Tenant->>Provider: Redirect to OAuth
    Provider->>Tenant: GET /auth/google/callback?code=
    Tenant->>Tenant: Scambia code→token, crea/login utente
    Tenant-->>User: JWT cookie, redirect to dashboard

6.2. Landing Pubblica e Login Cross-Domain -------------------------------------------------------
La landing page gestisce il reindirimento iniziale:

// POST /api/auth/provider-redirect
app.post('/api/auth/provider-redirect', async (req, res) => {
  const { provider, email } = req.body;
  
  // Trova il tenant basato sull'email o su altri criteri
  const tenant = await findTenantForUser(email);
  
  if (!tenant) {
    return res.json({ 
      ok: false, 
      error: 'No tenant found for this email' 
    });
  }
  
  // Costruisci URL tenant-specifico
  const tenantUrl = `http://${tenant.subdomain}.lvh.me:3001/auth/${provider}`;
  res.json({ ok: true, redirect: tenantUrl });
});

6.3. OAuth2 (Google, GitHub) --------------------------------------------------------------------
Configurazione Provider:

// Google OAuth strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: `${getTenantBaseUrl()}/auth/google/callback`,
  scope: ['openid', 'email', 'profile']
}, async (accessToken, refreshToken, profile, done) => {
  // Trova o crea utente nel tenant corrente
  const user = await UserService.findOrCreateFromOAuth(profile, req.tenant.id);
  return done(null, user);
}));

Callback URL per sviluppo:

Google: http://default.lvh.me:3001/auth/google/callback

GitHub: http://default.lvh.me:3001/auth/github/callback

Nota sui redirect tenant-scoped:

Il valore di `redirect_uri` usato nella richiesta di autorizzazione verso il provider deve corrispondere esattamente a quello inviato durante lo scambio code→token. In ambiente multitenant locale costruiamo il `redirect_uri` dinamicamente a partire dall'host della richiesta (es. `http://default.lvh.me:3001/auth/google/callback`). Assicurati che i callback registrati nella console del provider includano gli URL tenant-specific (es. `http://*.lvh.me:3001/auth/google/callback`) o i singoli callback per ogni subdomain usato in sviluppo.

6.4. SAML 2.0 -----------------------------------------------------------------------------------
Configurazione:

// Setup SAML
const samlStrategy = new SamlStrategy({
  entryPoint: tenantSamlConfig.entryPoint,
  issuer: tenantSamlConfig.issuer,
  callbackUrl: `${getTenantBaseUrl()}/auth/saml/callback`,
  cert: tenantSamlConfig.cert,
  // ... altre configurazioni
}, async (profile, done) => {
  // Gestisci utente SAML
  const user = await UserService.findOrCreateFromSAML(profile, req.tenant.id);
  done(null, user);
});

6.5. Autenticazione JWT -------------------------------------------------------------------------
Middleware di Verifica:

export const authenticateJWT = async (
  req: Request, 
  res: Response, 
  next: NextFunction
) => {
  const token = req.cookies?.access_token || 
                req.header('Authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
    const user = await UserService.findById(decoded.userId);
    
    if (!user || user.tenant_id !== req.tenant.id) {
      return res.status(403).json({ error: 'Invalid tenant scope' });
    }
    
    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

7. Debugging e Troubleshooting ///////////////////////////////////////////////////////////////////
7.1. Problemi Comuni ----------------------------------------------------------------------------
TS6059 durante build:

# Aggiorna tsconfig.json
{
  "include": ["src/**/*", "types/**/*"],
  "compilerOptions": {
    "rootDir": "./src"
  }
}

Tenant non trovato:

Verifica che il subdominio sia corretto nel browser

Controlla che il tenant esista nel database

Verifica la configurazione di lvh.me o hosts file

Errori OAuth "no_email":

Verifica gli scope configurati (email, profile)

Controlla le configurazioni nella console dello sviluppatore

7.2. Comandi di Debug Rapidi ---------------------------------------------------------------------

# Log dell'applicazione
tail -f /tmp/linkbay_server.log

# Test provider redirect
# Test provider redirect (esempio usando lvh.me)
curl -X POST http://lvh.me:3001/api/auth/provider-redirect \
  -H 'Content-Type: application/json' \
  -d '{"provider":"google","email":"admin@linkbay.local"}' | jq

# Simula richiesta tenant-specifica (Host header è utile quando non si usa lvh.me)
curl -i -v -H 'Host: default.localhost:3001' \
  'http://localhost:3001/auth/google' --max-redirs 0

# Verifica connessione database
npx knex --knexfile knexfile.ts migrate:status

8. File Chiave e Punti di Estensione /////////////////////////////////////////////////////////////
Routing:

src/routes/publicLanding.ts - Landing page pubblica

src/routes/publicAuth.ts - API auth pubblica

src/routes/tenantAuth.ts - Auth tenant-specifica

src/routes/tenantApi.ts - API tenant-specifiche

Middleware:

src/middleware/tenantResolver.ts - Risoluzione tenant

src/middleware/auth.ts - Autenticazione JWT

src/middleware/errorHandler.ts - Gestione errori

Services:

src/services/TenantService.ts - Gestione tenant

src/services/UserService.ts - Gestione utenti

src/services/AuthService.ts - Logica autenticazione

9. Monitoraggio e Observability //////////////////////////////////////////////////////////////////
Integrazione Sentry:

import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Express({ app }),
  ],
  tracesSampleRate: 1.0,
});

// Aggiungi middleware tracing
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());

// Error handler
app.use(Sentry.Handlers.errorHandler());

Logging Strutturato:

import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'SYS:standard',
    }
  }
});

// Utilizzo
logger.info({ tenant: req.tenant?.id }, 'User logged in');


Security checklist (consigli rapidi):

- Non cancellare i segreti in `.env` durante lo sviluppo. Se i segreti sono già presenti e funzionanti, mantenerli localmente; per condivisione usare un secrets manager (AWS Secrets Manager, Vault, 1Password/Bitwarden) o file locali cifrati.
- In produzione usare sempre HTTPS e registrare i callback OAuth/SAML con gli URL esatti di produzione.
- Limitare gli OAuth scopes ai minimi necessari (es. `email profile`), abilitare la verifica delle email lato provider se disponibile.
- Per i redirect in ambiente multitenant assicurarsi che i `redirect_uri` siano esatti e consistenti tra richiesta di autorizzazione e token-exchange; quando possibile registra wildcard o singoli callback per ogni tenant in console provider.
- Rotazione regolare dei segreti e uso di refresh tokens con revoca server-side (gestire la tabella `refresh_tokens`).
- Loggare eventi sensibili (login, refresh token revoke) in modo strutturato e filtrare PII nei log.
- Evitare di commitare `.env` nel repository. Aggiungere `.env` a `.gitignore` (se non già presente) e usare meccanismi sicuri per CI/CD.


10. Workflow di Sviluppo ////////////////////////////////////////////////////////////////////////
Script Utili:

{
  "scripts": {
    "dev": "nodemon --exec ts-node src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "migrate": "knex migrate:latest --knexfile knexfile.ts",
    "rollback": "knex migrate:rollback --knexfile knexfile.ts",
    "seed": "knex seed:run --knexfile knexfile.ts",
    "lint": "eslint src/**/*.ts",
    "test": "jest"
  }
}

Creazione Tenant di Test:

# Script per creare tenant di test
npx ts-node scripts/create-test-tenant.ts \
  --name "Test Tenant" \
  --subdomain "test" \
  --email "admin@test.com"


11. Deployment e Produzione /////////////////////////////////////////////////////////////////////
Variabili d'Ambiente Production:

NODE_ENV=production
APP_URL=https://your-production-domain.com
DATABASE_URL=postgresql://user:password@production-db:5432/linkbay_prod
REDIS_URL=redis://production-redis:6379
# ... altre variabili

Dockerfile Example:

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]

Health Check Endpoints:

# Health check basic
curl -f http://localhost:3001/health || exit 1

# Health check completo
curl http://localhost:3001/health/advanced