# backend — LinkBayCMS

Laravel 13 / Filament 5 multi-tenant backend: piattaforma SaaS B2B per agenzie
digitali che rivendono e gestiscono negozi (store) per i propri clienti.
Multi-tenancy fisica via [stancl/tenancy](https://tenancyforlaravel.com/) —
un database per tenant, non solo scoping a livello di query.

## Stack

- PHP 8.3+, Laravel 13, Filament 5
- Postgres (central + per-tenant), Redis (cache/queue/session)
- Sanctum per l'autenticazione a token (customer storefront, API tenant)
- Stripe (billing agenzia a livello centrale, checkout storefront a livello tenant)
- PHPUnit su SQLite `:memory:` per i test (vedi `phpunit.xml`) — nessuna
  dipendenza da Postgres/Redis per lanciare la suite

## Architettura: central DB vs tenant DB

- **Central**: `App\Models\Central\*` — Agency, AgencyClient, Tenant (= lo
  store), Plan, Subscription, BillingEvent, AuditEvent, ecc. Vive nel
  database Postgres "centrale".
- **Tenant**: `App\Models\Tenant\*` — Product, Order, Customer, CartSession,
  CheckoutSession, ShippingMethod, ecc. Ogni store ha il proprio database
  fisico, inizializzato da `TenantProvisioningService` e risolto a runtime
  dal dominio della richiesta (`Stancl\Tenancy\Middleware\InitializeTenancyByDomain`).
- Un tenant viene registrato su **due domini diversi** (vedi
  `TenantProvisioningService::registerDomain`): il dominio dello store
  (`{tenant_id}.STORE_DOMAIN`, es. `acme.yoursite-linkbay-cms.com`) serve il
  pannello Filament `/admin` del tenant e le API storefront
  (`api/store/*`, `api/v1/*`). Le pagine storefront vere e proprie (Next.js)
  vivono invece su un subdomain di `CENTRAL_DOMAIN` — vedi `frontend/README.md`.

## I tre pannelli Filament

| Panel | Path | Dominio | Provider | Per chi |
|---|---|---|---|---|
| Admin (superadmin) | `/linkbay-admin` | `admin.CENTRAL_DOMAIN` (prod) / `ADMIN_DOMAIN` (locale) | `AdminPanelProvider` | Gestione piattaforma: agenzie, piani, tenant, fatturazione |
| Agency | `/dashboard` | qualsiasi dominio centrale (nessun domain-lock, l'agenzia è risolta dall'utente loggato) | `AgencyPanelProvider` | Agenzie: clienti, store, commissioni, entitlement |
| Tenant | `/admin` | `{tenant_id}.STORE_DOMAIN` (domain-lock via `InitializeTenancyByDomain`) | `TenantPanelProvider` | Store owner: prodotti, ordini, clienti, spedizioni |

## Come si avvia

Con Docker (consigliato — vedi `../compose.yaml` e
`../compose.override.local.yml` per lo sviluppo locale):

```bash
cp ../.env.example ../.env              # valorizza CENTRAL_DOMAIN, STORE_DOMAIN, Stripe keys
cp .env.example .env
docker compose -f ../compose.yaml -f ../compose.override.local.yml up -d
docker compose exec php php artisan migrate --force
docker compose exec php php artisan db:seed --class=PlanSeeder
```

Guida completa passo-passo (agency → tenant → Stripe test mode):
[`docs/local-full-flow-testing.md`](../docs/local-full-flow-testing.md).

Senza Docker (solo backend, `composer run dev` avvia anche queue listener,
log tailing e Vite):

```bash
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate --force
composer run dev
```

## Test

```bash
php artisan test --compact                        # tutta la suite
php artisan test --compact tests/Feature/Tenant    # solo una cartella
php artisan test --compact --filter=nomeTest       # un test specifico
vendor/bin/pint --dirty --format agent             # style fix sui file modificati
```

Note sull'ambiente di test:
- `tests/TenantIsolationTestCase.php` prova l'isolamento fisico dei dati fra
  tenant con due connessioni SQLite in-memory indipendenti, non solo scoping
  a livello di query — vedi `tests/Feature/Tenant/TenantIsolationTest.php`.
- `tests/Concerns/InteractsWithTenantRoutes.php` bypassa solo il middleware
  di risoluzione del tenant da dominio nei test HTTP (che girano su una
  singola connessione SQLite in-memory senza un vero Host header) — il resto
  dello stack (route, form request, controller, service, DB) gira per davvero.
- Se lanci `vendor/bin/phpunit`/`php artisan test` direttamente da CLI locale
  (fuori da Docker/CI) e ottieni un `Fatal error: Allowed memory size
  exhausted`, il tuo `php.ini` locale ha probabilmente `memory_limit=128M` —
  CI non ne risente (i runner GitHub Actions partono con `memory_limit=-1`).

## Documentazione

- [`docs/demo-runbook.md`](../docs/demo-runbook.md) — flusso demo end-to-end
  (shipping method → prodotto → checkout → conferma ordine)
- [`docs/pre-demo-checklist.md`](../docs/pre-demo-checklist.md) — checklist
  pre-demo/pre-beta
- [`docs/staging-deploy.md`](../docs/staging-deploy.md) — proposta di deploy
  su staging (nessun ambiente staging esiste ancora)
- [`docs/local-full-flow-testing.md`](../docs/local-full-flow-testing.md) —
  setup locale dettagliato con routing Traefik
- [`../frontend/README.md`](../frontend/README.md) — storefront Next.js
  (routing tenant, integrazione API)
