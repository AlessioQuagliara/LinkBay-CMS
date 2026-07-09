# Pre-Demo Checklist

Run through this before any live demo, beta tester invite, or staging
deploy. Each item links to where it's implemented/verified. Target: ~15
minutes for someone who already has the stack running.

## Infra / environment

- [ ] `docker compose -f compose.yaml -f compose.override.local.yml ps` — all
      containers `healthy` (db, redis, nginx all report health status; php
      has no built-in healthcheck itself, but nginx's healthcheck depends on
      it responding — see `compose.yaml`)
- [ ] `curl -s -o /dev/null -w "%{http_code}" http://app.linkbay-cms.test/up`
      → `200`. If not: check central DB connectivity and Redis first
      (`App\Listeners\CheckApplicationHealth`).
- [ ] `.env` (root and `backend/.env`) filled from `.env.example` — no
      `REPLACE_ME` placeholders left for anything the demo touches
      (Stripe keys, `CENTRAL_DOMAIN`, `SESSION_DOMAIN`, `STORE_DOMAIN`).
      `STORE_DOMAIN` in particular is easy to miss since it has no
      `REPLACE_ME` marker — it silently falls back to the placeholder
      `yoursite-linkbay-cms.com`, which you don't control, if left unset.
- [ ] `frontend/.env.local` has `NEXT_PUBLIC_MAIN_DOMAIN` set to match
      whatever host family you're actually using (`linkbay-cms.test` locally)
      — if missing, tenant subdomains silently fail to resolve to the
      storefront (see docs/demo-runbook.md § Browse the storefront) and
      `frontend` must be rebuilt after changing it (`NEXT_PUBLIC_*` is
      baked in at build time, not read at runtime).
- [ ] Mail actually delivers (welcome email, password reset). If
      `MAIL_MAILER=log`, switch to a real SMTP sandbox (Mailtrap/Resend) — see
      `backend/.env.example`. A demo where the invite/reset email never
      arrives stalls immediately.

## Background processing

- [ ] Queue workers running: `docker compose exec php supervisorctl status`
      → `laravel-worker` (x2) `RUNNING`.
- [ ] Scheduler running: same command → `laravel-scheduler` `RUNNING`. If
      missing, none of the 7 scheduled tasks in `routes/console.php`
      (entitlement expiry, health alerts, low-stock checks, AI credit bonus,
      Stripe Connect sync, analytics cache warm, stuck-webhook reprocessing)
      will ever fire.
- [ ] Admin panel → **Operations → Failed Jobs** is empty (or every entry is
      explained/retried).
- [ ] Admin panel → **Operations → Stripe Webhooks** is empty (no
      unprocessed `BillingEvent` older than a few minutes).

## Alerting (optional but recommended before a real beta, not just a demo)

- [ ] `LOG_SLACK_WEBHOOK_URL` set and `LOG_STACK=single,slack` in
      whichever `.env` actually runs the demo, so a failed job or
      unhandled exception pages someone instead of sitting in
      `storage/logs/laravel.log` unseen.

## Golden path (see docs/demo-runbook.md for full detail)

- [ ] Agency registration → login works
- [ ] **Tenant/store creation works, panel reachable AND the tenant database
      is actually queryable** — don't just check the Filament wizard says
      "created". Live testing (2026-07-08) found the async
      `CreateDatabase`/`MigrateDatabase`/`SeedDatabase` pipeline can fail
      inconsistently (see docs/demo-runbook.md § 0 for the exact symptom) —
      confirmed unresolved, not a false alarm. Check
      `docker compose logs php | grep -i tenant` and the central Failed Jobs
      admin page after creating a store, before assuming it's ready.
- [ ] Shipping method exists for the demo store (checkout silently looks
      broken without one)
- [ ] At least one active/published product exists and shows on `/shop`
- [ ] Storefront checkout completes with Stripe test card `4242 4242 4242
      4242` and reaches `/checkout/success`
- [ ] Customer register/login on storefront works, order shows in
      `/account/orders`

## Known non-blocking gaps to disclose, not hide

Say these out loud before a beta tester hits them, rather than let them
discover it as a "bug":

- [ ] `storefront/` (repo root) has been archived to
      `_archive/storefront-standalone-legacy/` — the supported storefront is
      `frontend/app/storefront/`.
- [ ] No automated frontend/storefront test suite exists yet — the manual
      runbook is the regression check.
- [ ] The "active plan required to create a store" billing gate is not
      wired up yet — `tests/Feature/StoreFullProvisioningTest.php` documents
      this as a TODO, it's not a commented-out-but-otherwise-ready test.
      Any agency can create a store regardless of plan today.
- [x] ~~Checkout isn't safe against concurrent double-submit~~ — fixed:
      `convertToOrder()` locks the checkout row inside a transaction;
      `createPaymentIntent()` reuses an existing intent plus a Stripe
      idempotency key. See docs/demo-runbook.md for detail.

Cross-tenant data isolation now **does** have a dedicated automated test
(`tests/Feature/Tenant/TenantIsolationTest.php`) — no longer a gap to disclose,
but still worth a visual sanity-check if demoing two tenants side by side.

## CI status

- [ ] `gh run list --limit 1` on `main` is green. As of 2026-07-08 the
      workflow file already contains fixes for the two historical failures
      (migration `--database=central` flag, missing `composer install`
      before the Vite build in `backend-assets`) — confirm they're
      **committed and pushed**, not just sitting in the working tree.
