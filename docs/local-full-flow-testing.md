# Local Full-Flow Testing — LinkBayCMS

Guida passo-passo per testare in locale l'intero flusso:
**Registrazione agency → Login → Dashboard → Creazione tenant → Stripe test mode**

---

## Come usare i file Compose

### Locale (Mac con /etc/hosts .test)
```bash
docker compose -f compose.yaml -f compose.override.local.yml up -d
```

Per evitare di digitare sempre i due `-f`, crea un symlink:
```bash
ln -sf compose.override.local.yml docker-compose.override.yml
docker compose up -d    # carica automaticamente l'override
```

### Produzione / Staging
```bash
docker compose -f compose.yaml up -d
```

---

## Cosa è base, cosa è override

| Contenuto | `compose.yaml` | `compose.override.local.yml` |
|---|---|---|
| Servizi (traefik, db, redis, php, nginx, frontend…) | ✅ definiti | — override opzionale |
| Router Traefik `*.linkbay-cms.com` | ✅ | — |
| Router Traefik `*.linkbay-cms.test` | ❌ | ✅ |
| Router Traefik `localhost` | ❌ | ✅ |
| `CENTRAL_DOMAIN=linkbay-cms.com` (default prod) | ✅ | override a `linkbay-cms.test` |
| `APP_ENV=production` (default) | ✅ | override a `local` |
| `APP_URL=https://app.linkbay-cms.com` (produzione) | backend/.env | override a `http://app.linkbay-cms.test` |
| Porte 5432/6379 esposte sull'host | ❌ | ✅ |
| APP_DEBUG, log verbose | ❌ | ✅ |
| Stripe CLI sidecar (commentato) | ❌ | ✅ |

---

## Domini locali vs produzione

| Scopo | Locale (`.test`) | Produzione (`.com`) |
|---|---|---|
| Landing / Frontend | `http://linkbay-cms.test` | `https://linkbay-cms.com` |
| Backend API / Admin | `http://app.linkbay-cms.test` | `https://app.linkbay-cms.com` |
| Super Admin panel | `http://app.linkbay-cms.test/linkbay-admin` | `https://app.linkbay-cms.com/linkbay-admin` |
| Registrazione agency | `http://app.linkbay-cms.test/agency/register` | `https://app.linkbay-cms.com/agency/register` |
| Agency dashboard | `http://testagency.linkbay-cms.test/dashboard` | `https://testagency.linkbay-cms.com/dashboard` |
| Storefront del tenant (Next.js) | `http://clientalpha.linkbay-cms.test/` | `https://clientalpha.linkbay-cms.com/` |
| Tenant store admin | `http://clientalpha.yoursite-linkbay-cms.test/admin` | `https://clientalpha.yoursite-linkbay-cms.com/admin` |

> **Attenzione — due domini diversi per lo stesso store**: il pannello
> Filament del tenant e le sue API (`api/store/*`, `api/v1/*`) vivono su
> `STORE_DOMAIN` (`yoursite-linkbay-cms.test`/`.com`), un dominio **diverso**
> da `CENTRAL_DOMAIN` — vedi `TenantProvisioningService::registerDomain()`.
> Una versione precedente di questa tabella/guida usava
> `clientalpha.linkbay-cms.test/admin` per il pannello tenant: non funziona,
> perché quel dominio non viene mai registrato per nessun tenant dal codice
> reale (solo un tinker manuale che scrive un domain "sbagliato" può farlo
> sembrare funzionante, vedi Step 4 più sotto). `clientalpha.linkbay-cms.test`
> (senza `yoursite-`) è invece corretto per la **storefront** Next.js.

---

## Architettura routing locale

```
Browser
  │
  ▼
Traefik :80  (tutti i domini → 127.0.0.1 via /etc/hosts)
  │
  ├─ linkbay-cms.test                   → frontend-svc (Next.js :3000)
  │    Landing page, marketing, CTA
  │
  ├─ app.linkbay-cms.test/*             → nginx-svc → php-fpm (Laravel)
  │    /agency/register                 → form registrazione Blade
  │    /linkbay-admin                   → Filament Super Admin (host-locked)
  │    /api/stripe/webhook              → Stripe webhook handler
  │
  ├─ testagency.linkbay-cms.test/*      → nginx-svc → php-fpm
  │    /dashboard                       → Filament Agency Panel
  │    (nessun domain-lock: qualunque host centrale funziona, l'agency è
  │     risolta dall'utente loggato, non dal subdomain)
  │
  ├─ clientalpha.linkbay-cms.test/*     → frontend-svc (Next.js :3000)
  │    Storefront del tenant (shop/cart/checkout/account) — QUALSIASI
  │    subdomain di linkbay-cms.test che non sia app./admin./api. finisce
  │    qui (Traefik priority), poi middleware.ts fa il rewrite a /storefront
  │
  └─ clientalpha.yoursite-linkbay-cms.test/*  → nginx-svc → php-fpm
       /admin                           → Filament Tenant Panel
       /api/store/*, /api/v1/*          → API consumate dalla storefront sopra
       (tenant identificato da domain nel DB — dominio STORE_DOMAIN, diverso
        dalla riga precedente anche se lo slug "clientalpha" è lo stesso)
```

---

## Prerequisiti

- Docker Desktop con `docker compose` v2
- `/etc/hosts` configurato (o dnsmasq per wildcard):

```
127.0.0.1   linkbay-cms.test
127.0.0.1   app.linkbay-cms.test
127.0.0.1   admin.linkbay-cms.test
127.0.0.1   testagency.linkbay-cms.test
127.0.0.1   clientalpha.linkbay-cms.test
127.0.0.1   clientalpha.yoursite-linkbay-cms.test
```

dnsmasq (alternativa wildcard):
```bash
brew install dnsmasq
echo "address=/.linkbay-cms.test/127.0.0.1" >> $(brew --prefix)/etc/dnsmasq.conf
sudo brew services start dnsmasq
sudo mkdir -p /etc/resolver && echo "nameserver 127.0.0.1" | sudo tee /etc/resolver/linkbay-cms.test
```

---

## Comandi di avvio (copia-incolla)

```bash
# 1. Avvia lo stack locale
docker compose -f compose.yaml -f compose.override.local.yml up -d

# 2. Verifica che i container siano up
docker compose -f compose.yaml -f compose.override.local.yml ps

# 3. Esegui le migrations (solo prima volta o dopo pull)
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan migrate --force

# 4. Seed piani e pacchetti AI
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan db:seed --class=PlanSeeder

# 5. Crea super admin
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan tinker --execute="
\App\Models\Central\User::firstOrCreate(
    ['email' => 'admin@linkbay-cms.test'],
    ['name' => 'Super Admin', 'password' => bcrypt('password'), 'is_super_admin' => true]
);
echo 'done';
"

# 6. Pulisci cache config
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan config:clear
```

---

## Stripe webhook locale

Apri un **secondo terminale** (resta aperto durante i test):

```bash
stripe login    # una volta sola

stripe listen --forward-to http://app.linkbay-cms.test/api/stripe/webhook
# → copia il whsec_... mostrato in output
```

Aggiorna il segreto nel container (senza rebuild):
```bash
# Opzione A: aggiorna root .env e ricrea il container
# APP_STRIPE_WEBHOOK_SECRET=whsec_...
docker compose -f compose.yaml -f compose.override.local.yml up -d --force-recreate php

# Opzione B: aggiorna compose.override.local.yml (decommentare la riga STRIPE_WEBHOOK_SECRET)
# poi ricrea:
docker compose -f compose.yaml -f compose.override.local.yml up -d --force-recreate php
```

Poi:
```bash
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan config:clear
```

---

## Flusso test completo

### Step 1 — Registrazione agency
- Apri: **http://linkbay-cms.test** → clicca "Inizia ora"
- Oppure vai diretto: **http://app.linkbay-cms.test/agency/register**
- Compila:
  - Nome: `Test Agency`
  - Slug: `testagency`
  - Email: `owner@testagency.test`
  - Password: `password123`
- Submit → redirect a `http://testagency.linkbay-cms.test/dashboard/login`

### Step 2 — Login agency
- URL: **http://testagency.linkbay-cms.test/dashboard/login**
- Email: `owner@testagency.test` / Password: `password123`
- Arriva alla Agency Dashboard Filament

### Step 3 — Super Admin
- URL: **http://app.linkbay-cms.test/linkbay-admin**
- Email: `admin@linkbay-cms.test` / Password: `password`
- Menu **Tenancy → Agenzie** → vedi `Test Agency`

### Step 4 — Crea tenant (negozio)
- Dal Super Admin: **Tenancy → Tenant** → Create
- O da tinker:
```bash
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan tinker --execute="
\$tenant = \App\Models\Central\Tenant::create(['id' => 'clientalpha', 'name' => 'Client Alpha']);
app(\App\Services\TenantProvisioningService::class)->registerDomain(\$tenant);
echo 'done';
"
```
Usa sempre `registerDomain()` invece di scrivere il domain a mano — registra
`{tenant_id}.STORE_DOMAIN` (`clientalpha.yoursite-linkbay-cms.test` in
locale), lo stesso meccanismo usato dal wizard reale in
`CreateStore::afterCreate()`. Scrivere manualmente
`clientalpha.linkbay-cms.test` come domain "funzionerebbe" per stancl/tenancy
ma non corrisponde a come l'app crea davvero i tenant, e quel host è comunque
instradato alla storefront Next.js, non a Laravel (vedi diagramma sopra).

- Poi accedi: **http://clientalpha.yoursite-linkbay-cms.test/admin**

**✅ Fixato e verificato dal vivo il 2026-07-09**: una versione precedente di
questa nota segnalava `Tenant::create()` come intermittentemente rotto
(`TenantDatabaseAlreadyExistsException` con il database in realtà assente).
Root cause: `TenantProvisioningService::initializeDatabase()` chiamava
`tenancy()->initialize()` subito dopo, assumendo che la pipeline asincrona
`TenantCreated → CreateDatabase → MigrateDatabase → SeedDatabase`
(`TenancyServiceProvider`) avesse già creato il database fisico — nessuna
garanzia d'ordine tra i due. `TenantProvisioningService` ora crea e migra il
database del tenant da sé, in modo sincrono
(`ensureDatabaseProvisioned()`); `TenancyServiceProvider` non registra più
quella pipeline per `TenantCreated`. La stessa sessione di test ha anche
scoperto e corretto due bug reali specifici di Postgres (tollerati in
silenzio da SQLite, quindi mai visti nei test automatici): una migration
tenant che referenziava una tabella inesistente `tenant_users` invece di
`users`, e il modello `Setting` privo della sua chiave primaria non
standard (`key`, non `id`).

Verificato dal vivo: creazione tenant sia via wizard agency
(`ProvisionTenantDatabaseJob`, asincrono) sia via API centrale
(`POST /central/api/tenants`, sincrono) — 3/3 di fila per entrambi, zero
job falliti, database del tenant confermato migrato e seedato ogni volta.
Test di regressione: `backend/tests/Feature/TenantProvisioningTest.php`.

---

## 404 attesi vs 404 anomali

| URL | Codice | Motivazione |
|---|---|---|
| `testagency.linkbay-cms.test/dashboard/login` prima della registrazione | 200 | Filament serve la login page anche senza agency in DB |
| `clientalpha.yoursite-linkbay-cms.test/admin` senza tenant nel DB | **500** `TenantCouldNotBeIdentifiedException` | **Atteso** — il tenant non esiste, stancl/tenancy lancia eccezione |
| `clientalpha.yoursite-linkbay-cms.test/admin` dopo creazione tenant | 200/302 | Funziona dopo `db:seed` o creazione manuale (con `registerDomain()`, non un domain scritto a mano) |
| `clientalpha.linkbay-cms.test/` (storefront) prima di impostare `NEXT_PUBLIC_MAIN_DOMAIN` | Sito marketing invece della storefront, o 404 su `/shop` | **Anomalo ma comune** — vedi `frontend/.env.local.example`, non è un bug del codice |
| Qualsiasi `.test` restituisce Traefik `404 page not found` | 404 Traefik | **Anomalo** — significa che il routing in `compose.override.local.yml` non è caricato |

---

## Quando serve rebuild del frontend

Il frontend Next.js baka le variabili `NEXT_PUBLIC_*` al **build time**. Dopo ogni modifica a `frontend/.env.local`:

```bash
docker compose -f compose.yaml -f compose.override.local.yml build frontend
docker compose -f compose.yaml -f compose.override.local.yml up -d frontend
```

Valori correnti baked nel container locale:
```
NEXT_PUBLIC_API_BASE_URL=http://app.linkbay-cms.test
NEXT_PUBLIC_AGENCY_REGISTER_URL=http://app.linkbay-cms.test/agency/register
NEXT_PUBLIC_AGENCY_LOGIN_URL=http://app.linkbay-cms.test/linkbay-admin
```

---

## Come verificare che non sto uscendo dal locale

```bash
# 1. Verifica i router Traefik attivi
curl -s http://localhost:8080/api/http/routers | python3 -m json.tool | grep '"rule"'

# 2. Verifica env nel container PHP
docker compose -f compose.yaml -f compose.override.local.yml exec php env | grep -E "APP_URL|CENTRAL_DOMAIN|SESSION_DOMAIN"
# Deve mostrare: http://app.linkbay-cms.test / linkbay-cms.test / .linkbay-cms.test

# 3. Test routing completo
curl -s -o /dev/null -w "%{http_code}" -H "Host: app.linkbay-cms.test" http://localhost/linkbay-admin/login
# Deve rispondere 200

# 4. Verifica che i link nel frontend puntino a .test
curl -s -H "Host: linkbay-cms.test" http://localhost/ | grep -o "linkbay-cms\.test" | wc -l
# Deve mostrare > 0 (link locali presenti)
```

---

## Protocollo locale scelto

**HTTP puro** — Traefik espone solo la porta 80, nessun TLS locale.

Tutti gli URL locali usano `http://`. Questo è intenzionale:
- `APP_URL=http://app.linkbay-cms.test` → `url()` e `route()` Laravel generano `http://`
- `SESSION_DOMAIN=.linkbay-cms.test` → cookie condivisi cross-subdomain
- `TrustProxies` è attivo (`bootstrap/app.php`) per gestire gli header X-Forwarded-* di Traefik

---

## Playwright golden path

Suite E2E minimale (`frontend/e2e/`) che copre il percorso critico
storefront → checkout → conferma → ordine in account contro lo stack Docker
reale — non dipende solo dal runbook manuale per accorgersi di regressioni
su login/checkout. Due spec, deliberatamente pochi test, non una batteria:

- `checkout-golden-path.spec.ts` — percorso **autenticato**: registrazione →
  carrello → checkout → pagamento Stripe reale (test mode) → conferma →
  ordine visibile in `/account/orders`. Registrazione avviene **prima** del
  checkout, non dopo: un ordine guest ha `customer_id = null` e non esiste
  logica di "reclamo" per email da nessuna parte nell'app (verificato in
  `CustomerAuthService` prima di scrivere il test) — collegare un ordine
  guest a un account dopo la registrazione richiederebbe inventare un
  comportamento nuovo, fuori scope ("non cambiare la logica di
  checkout/ordini").
- `guest-checkout.spec.ts` — percorso **guest**: carrello → checkout →
  pagamento → conferma, senza account, verificando che la pagina di
  conferma mostri i dati reali dell'ordine (non lo stato di errore ambra —
  vedi `checkout/success/page.tsx`). Copre il path pubblico
  `GET /api/store/checkout/{checkout}/order` separatamente da quello
  autenticato.

### Prerequisiti (una tantum)

1. **Stack Docker avviato**:
   ```bash
   docker compose -f compose.yaml -f compose.override.local.yml up -d
   ```
2. **Riga in `/etc/hosts`** per il tenant e2e dedicato — non automatizzabile
   da questa suite (richiede sudo):
   ```
   127.0.0.1 e2e-test.linkbay-cms.test e2e-test.yoursite-linkbay-cms.test
   ```
3. **Chiave Stripe test** in `frontend/.env.local` (deve combaciare con
   `APP_STRIPE_SECRET_KEY` nel root `.env` — stesso account Stripe, modalità
   test):
   ```
   NEXT_PUBLIC_STRIPE_KEY=pk_test_...
   ```
   e `NEXT_PUBLIC_MAIN_DOMAIN=linkbay-cms.test` (vedi
   `frontend/.env.local.example` — senza questa riga il routing dei
   subdomain è silenziosamente rotto, non solo per Playwright). Dopo aver
   modificato `.env.local`: `docker compose build frontend && docker compose
   up -d frontend` (i `NEXT_PUBLIC_*` sono baked al build time).
4. **Migrations + seed piani** già eseguiti sul central DB (vedi sezione
   "Comandi di avvio" più sopra).

### Come lanciarlo

```bash
cd frontend
npm ci
npx playwright install --with-deps chromium   # una tantum
npm run test:e2e            # headless
npm run test:e2e:ui         # UI mode interattiva, utile per debug
```

Il `globalSetup` (`frontend/e2e/setup/provision-tenant.ts`) provisiona in
modo idempotente un tenant fisso `e2e-test` — stessa pipeline verificata dal
vivo in `docs/demo-runbook.md` § 0 (crea solo se assente), più un metodo di
spedizione e un prodotto dedicati (`firstOrCreate`/`updateOrCreate`, sempre
riallineati). Se `/etc/hosts` o lo stack non sono pronti, fallisce subito con
un messaggio che dice esattamente cosa manca, invece di un timeout di
navigazione oscuro.

### Interpretare i risultati

- **Verde**: il golden path funziona end-to-end contro il codice reale — non
  solo build/lint/tsc puliti.
- **Fallisce al passo Stripe** (`payWithStripeTestCard`): quasi sempre
  `NEXT_PUBLIC_STRIPE_KEY` mancante/non ricostruita nel container, o
  `APP_STRIPE_SECRET_KEY` non in modalità test — non un bug del test.
- **Fallisce al passo "ordine in account"**: qui sì che vale la pena
  guardare — significa che la sessione autenticata non produce più un
  ordine collegato al cliente (regressione reale su
  `CartController::store()`/`CheckoutService`).
- Su fallimento: `frontend/playwright-report/index.html` (trace, screenshot,
  video) e `frontend/test-results/`.
- Riesecuzioni ripetute sono sicure: il tenant/prodotto/spedizione sono
  fissi e idempotenti, solo l'email cliente è unica per run
  (`e2e-{timestamp}@example.test`) — nessuna pulizia manuale richiesta tra
  un run e l'altro.

### CI (opzionale)

`.github/workflows/e2e.yml` — solo `workflow_dispatch` (manuale), non su
ogni push/PR: la suite guida iframe Stripe reali sulla rete, più lenta e
potenzialmente più fragile delle suite unit/feature già in `ci.yml`. Richiede
i secret repo `STRIPE_TEST_SECRET_KEY` e `STRIPE_TEST_PUBLISHABLE_KEY`
(chiavi test, mai `sk_live_`/`pk_live_`).

Per HTTPS locale in futuro: usare `mkcert linkbay-cms.test "*.linkbay-cms.test"` e abilitare il blocco `websecure` in compose.yaml.
