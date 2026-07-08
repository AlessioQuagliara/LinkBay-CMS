# Demo Runbook — LinkBayCMS

End-to-end script for running a live demo or smoke-testing a beta build:
**Agency → Store (tenant) → Product → Shipping method → Storefront checkout → Customer login/order history.**

This picks up where [docs/local-full-flow-testing.md](local-full-flow-testing.md)
leaves off (that doc covers agency registration, super admin, and tenant
creation in detail — read it first if you haven't set up the stack yet). This
doc assumes the stack is already up and a tenant already exists.

Run this in full before any demo or before inviting a beta tester — see
[docs/pre-demo-checklist.md](pre-demo-checklist.md) for the condensed
go/no-go list.

---

## 0. Prerequisites

```bash
docker compose -f compose.yaml -f compose.override.local.yml up -d
docker compose -f compose.yaml -f compose.override.local.yml ps   # all healthy?
```

- Agency created and tenant/store provisioned (see local-full-flow-testing.md
  steps 1–4). This runbook uses `clientalpha` as the example store slug, which
  resolves to **two different hosts** — don't mix them up, they're not
  interchangeable (see `TenantProvisioningService::registerDomain` and
  `frontend/README.md` → "Routing tenant"):
  - `clientalpha.linkbay-cms.test` — the **storefront pages** (Next.js:
    shop/cart/checkout/account), same parent domain as `app.`/`admin.test`
    but any other subdomain, routed to the `frontend` container by Traefik.
  - `clientalpha.yoursite-linkbay-cms.test` — the **tenant backend**
    (Filament `/admin` panel + the `api/store/*`/`api/v1/*` JSON API the
    storefront calls behind the scenes). This is `STORE_DOMAIN`, a separate
    domain from `CENTRAL_DOMAIN` on purpose.
- A second terminal running `stripe listen --forward-to
  http://app.linkbay-cms.test/api/stripe/webhook` if you need platform-level
  billing events. Storefront checkout has its **own** tenant-level webhook
  endpoint, `http://clientalpha.yoursite-linkbay-cms.test/webhooks/stripe` —
  but as of this writing it shares the same `STRIPE_WEBHOOK_SECRET` as the
  platform one (`services.stripe.tenant_webhook_secret`, mentioned in an
  earlier draft of this doc, is not an actual config key in the current code;
  there is no separate per-tenant secret yet). Order **creation** does not
  depend on this webhook at all — see step 6.

## 1. Add a shipping method (required before checkout will work)

Storefront checkout calls `GET /api/store/shipping-methods` and blocks on an
empty list. Create at least one before trying to check out.

- **http://clientalpha.yoursite-linkbay-cms.test/admin** → **Shipping Methods → New**
- Name: `Standard`, Price: `5.00`, Active: yes

Without this step, checkout will look broken (empty shipping step) — it
isn't a bug, it's missing seed data.

## 2. Create a product

- Same tenant panel → **Products → New**
- Fill name, price, stock, at least one image if you want the storefront PDP
  gallery to render; mark it **Active** / **Published** (field naming may
  differ slightly by version — anything not active won't show in
  `/shop`).
- Optional: assign to a collection/category if you want to demo
  `/collections/{slug}` or `/shop/{category}`.

## 3. Browse the storefront

Requires `NEXT_PUBLIC_MAIN_DOMAIN=linkbay-cms.test` set in `frontend/.env.local`
(see `frontend/.env.local.example`) and the `frontend` container rebuilt after
setting it — `NEXT_PUBLIC_*` vars are baked in at build time. Without this,
every `.test` subdomain is treated as the marketing site instead of being
rewritten to `/storefront`, and `/shop` etc. 404 even though the backend and
Next.js code are both correct — this was the single biggest "demo looks
broken but isn't" trap found in this repo, now fixed at the config level.

- **http://clientalpha.linkbay-cms.test/** → homepage (CMS blocks or featured
  products depending on what's configured)
- **/shop** → catalog, infinite scroll
- Click into the product → PDP with gallery, related products
- Add to cart (top-right cart drawer)

If `/shop` is empty, check the product's active/published flag from step 2 —
this is the most common "demo looks broken" cause.

## 4. Checkout (Stripe test mode)

- Cart drawer → **Checkout** (rewrites to `/storefront/checkout`)
- Step 1 — Address: fill any test address
- Step 2 — Shipping: pick the method created in step 1
- Step 3 — Payment: Stripe test card `4242 4242 4242 4242`, any future
  expiry, any CVC
- Confirm → redirected to `/checkout/success?checkout=X&order=Y`

Behind the scenes: `POST /checkout` → `POST /checkout/{id}/payment-intent` →
Stripe Elements `confirmPayment()` → `POST /checkout/{id}/confirm`. If the
payment intent step fails immediately, check `NEXT_PUBLIC_STRIPE_KEY` in the
frontend container matches the tenant's Stripe **test** publishable key, not
the platform's.

## 5. Customer account — register, login, order history

- **/account/login** → Register tab: create a customer (name/email/password)
- On success the storefront stores a Sanctum bearer token (`authStore` in
  `frontend/storefront/lib/store`) and calls authenticated routes with
  `Authorization: Bearer <token>`
- **/account/orders** → the order placed in step 4 should appear
- **/account/orders/{id}** → order detail
- **/account/profile** → edit name, add a saved address

This flow was flagged as broken in an earlier audit (frontend expecting a
token, backend allegedly using session auth). Re-checking the current code
(`CustomerAuthController` → `CustomerAuthService::login/register`) shows it
issues a Sanctum `plainTextToken` and protected routes use `auth:sanctum` —
they now match. **Still run this step manually before a demo** — this hasn't
been exercised against a live stack since that fix, only verified by reading
the code.

## 6. Verify webhook + job processing actually ran

Correction to an earlier draft of this doc: order **creation** in step 4 is
**synchronous**, not queued — `POST /checkout/{id}/confirm` calls
`CheckoutService::convertToOrder()` directly in the request/response cycle
(`CheckoutController::confirm`). There is no job in the path from "customer
clicks pay" to "order row exists". The tenant Stripe webhook
(`TenantStripeWebhookController`) only handles **updates** to an order that
already exists (marks it refunded/failed, from `payment_intent.succeeded` /
`payment_intent.failed` / `charge.refunded`) — it looks the order up by
`stripe_payment_intent_id`, which `convertToOrder()` now stores on the order
it creates, so this reconciliation path works. If the customer's browser
drops the connection between Stripe confirming payment and that final
`/confirm` call completing, no order is created and no webhook will create
one after the fact either — this is a known gap, see the final report.

The platform-level billing pipeline (`ProcessStripeWebhookJob`,
`BillingEvent`) is a **separate, unrelated system** for agency
subscriptions/AI credits — it has nothing to do with storefront orders.
Confirm nothing silently failed in either system:

- **http://app.linkbay-cms.test/linkbay-admin** → **Operations → Failed
  Jobs** — should be empty (or explainable)
- **Operations → Stripe Webhooks** — should be empty (all `BillingEvent`
  rows processed); if something sits here for more than a few minutes, the
  scheduled `billing:reprocess-stuck-events` job should have retried it —
  if it's still stuck, the scheduler isn't running (check `docker compose
  logs php | grep scheduler`)
- **`GET http://app.linkbay-cms.test/up`** → should return 200. A 500 here
  means central DB or Redis is unreachable — nothing downstream will work
  either.

---

## Known non-blocking gaps (updated 2026-07-08)

- `storefront/` (repo root) has been archived to
  `_archive/storefront-standalone-legacy/` — it's reference-only, not a
  choice you can still make by accident. The supported storefront is
  `frontend/app/storefront/`.
- No automated frontend/storefront tests exist (Jest/Vitest/Playwright) —
  this runbook is currently the only regression check for the checkout and
  account flows.
- ~~Multi-tenant DB isolation has no dedicated automated test~~ — no longer
  true: `tests/Feature/Tenant/TenantIsolationTest.php` now proves products,
  orders, cart sessions, and same-email customer registration are genuinely
  isolated per tenant DB. Still sanity-check visually if demoing two tenants
  side by side — the test proves data isolation, not that the UI/routing
  layer can't cross wires.
- Checkout has no protection against true concurrent double-submission (two
  near-simultaneous confirm calls for the same checkout could both create an
  order) — sequential retries are idempotent and safe, races are not. Low
  risk for a supervised demo, worth hardening before a real beta.
- `createPaymentIntent()` isn't idempotent — repeatedly clicking "proceed to
  payment" before the first attempt returns can create orphaned Stripe
  PaymentIntents. Doesn't break the demo, just leaves noise in the Stripe
  dashboard.
