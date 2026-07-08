# Contributing to LinkBay-CMS

Internal guide for working on this repo day-to-day. For the full guided demo
(tenant → store → product → checkout → customer login) see
[docs/demo-runbook.md](docs/demo-runbook.md). For deploying to a shared
staging box see [docs/staging-deploy.md](docs/staging-deploy.md).

## Repo layout

- `backend/` — Laravel 13 + Filament 5 (central DB + one DB per tenant via
  stancl/tenancy). Three panels: `linkbay-admin` (super admin), `/dashboard`
  (agency, subdomain-scoped), `/admin` (tenant store, subdomain-scoped).
- `frontend/` — Next.js marketing site + the primary storefront implementation
  under `frontend/app/storefront/` (shop, PDP, checkout, account).
- `frontend/storefront/` — shared component/lib library imported by the above.
- `storefront/` — a separate, newer storefront rewrite at the repo root.
  **It is not the one in production use and lacks catalog/PDP/tenant
  resolution.** No product decision has been made yet on which storefront to
  keep — don't build new storefront features in more than one of these three
  without checking first.
- `docker/`, `compose.yaml`, `compose.override.local.yml` — container topology
  (Traefik, Postgres, Redis, PHP-FPM+supervisor, Nginx, Next.js).
- `docs/` — setup guides, runbooks, design docs.

## Local setup

Two supported ways to run the backend locally. Pick one — don't mix.

### Option A — Docker Compose (matches staging/production topology)

```bash
docker compose -f compose.yaml -f compose.override.local.yml up -d
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan migrate --force
docker compose -f compose.yaml -f compose.override.local.yml exec php php artisan db:seed --class=PlanSeeder
```

Full walkthrough, `/etc/hosts` entries, and Stripe CLI wiring:
[docs/local-full-flow-testing.md](docs/local-full-flow-testing.md).

### Option B — Native (`composer run dev`), no Docker

```bash
cd backend
cp .env.example .env
composer install
php artisan key:generate
php artisan migrate --force
composer run dev   # runs php artisan serve + queue:listen + pail (logs) + vite, concurrently
```

Faster iteration, but single-tenant (no wildcard subdomain routing) — use it
for backend logic you can exercise via `php artisan test` rather than through
the panels.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # fill NEXT_PUBLIC_API_BASE_URL etc.
npm run dev
```

## Before opening a PR

```bash
# Backend
cd backend
vendor/bin/pint --dirty --format agent   # auto-fixes style, run before committing
php artisan test --compact               # or --filter=SomeTest for a fast loop

# Frontend
cd frontend
npm run lint
npx tsc --noEmit
npm run build
```

CI (`.github/workflows/ci.yml`) runs the same three checks per area (backend
tests, backend Vite build, frontend lint/typecheck/build), gated by
`dorny/paths-filter` so an unrelated area doesn't block you. If you're
touching CI itself, know that historically `backend-tests` failed on the
migration step and `backend-assets` failed on a missing `composer install` —
both are one-line fixes already applied in the current workflow file; don't
reintroduce them (see git history / [docs/pre-demo-checklist.md](docs/pre-demo-checklist.md)
for the current CI status).

## Conventions

- PHP: follow `backend/CLAUDE.md` (Laravel Boost guidelines) — constructor
  promotion, explicit return types, curly braces always, PHPDoc over inline
  comments. Central-DB models set `protected $connection = 'central'`
  explicitly; tenant models rely on stancl/tenancy's connection swap.
- New Eloquent models: create a factory alongside them (`php artisan make:model --help`
  for options) unless the model is a read-only wrapper over an existing table.
- Migrations for shared/central tables go in `backend/database/migrations/central/`
  and call `Schema::connection('central')` explicitly (see any file in that
  folder for the pattern) — omitting it is exactly the bug that broke CI's
  migration step previously.
- Filament resources: register them explicitly in the relevant
  `app/Providers/Filament/*PanelProvider.php` — this project does not use
  directory auto-discovery.
- Commit messages: imperative, present tense, explain *why* over *what* where
  it isn't obvious from the diff.
- Don't commit `.env` files or real Stripe/SMTP/Slack secrets. Copy from the
  relevant `.env.example` instead.

## Observability additions (read before debugging "nothing happened")

- `GET /up` is a real healthcheck (DB central connection + Redis), not just
  "the framework booted" — see `App\Listeners\CheckApplicationHealth`.
- Failed queue jobs (webhook processing, tenant provisioning) are visible in
  the Admin panel under **Operations → Failed Jobs**, with a one-click retry.
- Stuck/errored Stripe webhooks are visible under **Operations → Stripe
  Webhooks** (unprocessed `BillingEvent` rows).
- Any `Log::critical(...)` (including automatic queue-failure logging) is
  forwarded to Slack in any environment where `LOG_STACK` includes `slack`
  and `LOG_SLACK_WEBHOOK_URL` is set.
- The Laravel scheduler (`routes/console.php`) only runs because
  `docker/php/supervisord.conf` runs `schedule:work` — if you add a
  `Schedule::` entry and it never seems to fire outside Docker, that's why;
  under `composer run dev` you'd need `php artisan schedule:work` running
  separately.
