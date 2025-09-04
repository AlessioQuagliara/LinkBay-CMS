# Project documentation index

Questo file è un indice ai documenti più dettagliati del progetto. Apri i file sotto `docs/` per i dettagli.

Documenti disponibili:

- [00_OVERVIEW.md](00_OVERVIEW.md) — Panoramica del progetto
- [01_ARCHITECTURE.md](01_ARCHITECTURE.md) — Architettura e struttura
- [02_TECHNOLOGIES.md](02_TECHNOLOGIES.md) — Tecnologie usate
- [03_SETUP_ENV.md](03_SETUP_ENV.md) — Setup e ambiente
- [04_DATABASE.md](04_DATABASE.md) — Info sul database
- [05_NEXT_STEPS.md](05_NEXT_STEPS.md) — Prossimi passi e TODO

Se desideri che un argomento sia ampliato con esempi (es. script di deploy, CI, o esempi di test), indicamelo e lo aggiungo.

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