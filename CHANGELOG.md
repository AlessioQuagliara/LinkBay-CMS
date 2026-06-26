# Changelog

All notable changes to LinkBay-CMS are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

---

## [0.6.0] — 2026-06-26

### Added — Phase 6A: Early Warnings
- `AgencyHealthAlert` model and `agency_health_alerts` table
- `AgencyAlertService` with 4 alert rules (churn risk, low engagement, revenue drop, inactive stores)
- Artisan command `agency:health-alerts` for scheduled evaluation
- Filament resource for alert management in Admin panel
- Configurable thresholds via `config/agency_health.php`
- 12 feature tests

---

## [0.5.0] — 2026-06-25

### Added — Phase 5C: Agency Insights
- `AgencyInsightsService` + `AgencyInsightsDTO`
- Agency panel page (owner/admin only) with KPIs: store count, layout usage, block adoption, theme distribution
- 19 feature tests

### Added — Phase 5B: Agency Health
- `AgencyHealthService` with 4 health enums and `AgencyHealthDTO`
- Filament Insights page in Agency panel
- Configurable health score thresholds
- 19 feature tests

### Added — Phase 5A: Usage Analytics Foundation
- `UsageEvent` model and `usage_events` table
- `UsageEventService` with 10 event types
- 7 instrumentation points across Builder, Billing, and Auth flows
- Admin dashboard widget for platform-wide usage stats
- Performance indices migration
- 17 feature tests

---

## [0.4.0] — 2026-06-24

### Added — Phase 4D: Fork-with-Lock
- System theme variants with `override_config` and locked field enforcement
- `ThemeForkResolver` service
- "Crea variante" UI action in Theme panel
- `is_system` flag on `plugin_catalog_items`; fork columns on `theme_presets`
- 17 feature tests

### Added — Phase 4C: SKU Separation
- `theme_pack_editorial` feature code (Midnight + Noir)
- `theme_pack_business` feature code (Atelier + Meridian)
- Legacy entitlement expansion in `FeatureAccessService` for backward compatibility
- 14 feature tests

### Added — Phase 4B: Premium Theme Preview Mode
- `isPremiumPreview()` gate on unentitled themes
- Preview modal with palette display and origin badge
- Duplicate-while-previewing blocked
- 11 feature tests

### Added — Phase 4A: Upgrade Nudges
- `PremiumPackConfig` value object for pack metadata
- `ThemePremiumNudgeWidget` in Agency panel
- Nudge sections in MyEntitlements and Billing pages
- 13 feature tests

---

## [0.3.0] — 2026-06-22

### Added — Phase 3: Marketplace & Licensing Foundation
- `PluginCatalogItem` + `AgencyEntitlement` models and tables
- `FeatureAccessService` for feature gate resolution
- Midnight theme gated behind `theme_midnight` feature code
- `MarketingBlockPack` plugin (5 premium blocks: Hero, Testimonials, Pricing, FAQ, CTA)
- `blocksForAgency()` and `premiumViolation()` enforcement in Builder + backend
- Premium Theme Pack v1: Noir, Atelier, Meridian (feature code `theme_premium`)
- `MyEntitlementsPage` in Agency panel: plan features, active/expired entitlements
- Theme badge in panel and 14 tests per module

---

## [0.2.0] — 2026-06-12

### Added — Phase 2: Agency OS Operational Layer
- `AgencyClient` + `AgencyClientContact` models, tables, Filament resources
- `ClientInviteService` + `ClientInviteController` + `ClientInviteMail`
- `AgencyMember` model with roles (owner/admin/member), invite token, status
- `AgencyMemberService` + `AgencyMemberResource` + `AgencyMemberInviteController`
- `PayoutRecord` model, `payout_records` table, `PayoutsPage` in Agency panel
- `payout.created/paid/failed/canceled` webhook handlers with Connect account resolution
- `DashboardAlertService` with 7 alert types (Stripe not configured, plan expired, low credits, T&C pending, etc.)
- `DashboardAlertsWidget` in Agency dashboard
- `AuditEvent` model + `AuditEventService` with 13 event types + `AuditLogPage`
- `StoreAdminWelcomeMail` + reset-password token on tenant provisioning
- Per-store AI Credits usage breakdown (`storeBreakdown()`) in `AiCreditsPage`
- `agency_client_id` FK on `tenants` table

---

## [0.1.0] — 2026-05-29

### Added — Phase 1: Monetisation Foundation
- `platform_fee_rules` table + seed for 4 plan tiers; `PlatformFeeService::resolveRule()`
- `commission_records` table; `StripeConnectService::createPaymentWithFee()` saves record before creating PaymentIntent
- `billing_events` table with idempotent `insertOrIgnore` on `stripe_event_id`
- `agency_subscriptions` table + `AgencySubscriptionService` (sync, handleDeleted, handleInvoicePaid/Failed)
- `terms_acceptances` table + `TermsAcceptancePage` in Agency panel
- `StripeWebhookController` with signature validation + `ProcessStripeWebhookJob` (5 retries, exponential backoff)
- Webhook handlers: `payment_intent.succeeded/payment_failed`, `customer.subscription.created/updated/deleted`, `invoice.paid/payment_failed`, `checkout.session.completed`, `account.updated`, `charge.refunded`, `charge.dispute.created`, `payout.*`
- `CommissionsPage` with CSV export in Agency panel
- `PayoutsPage` in Agency panel
- Automatic agency suspension on `customer.subscription.deleted`
- Stripe Customer Portal link in `AgencyBillingPage`
- Infrastructure fixes: route slugs on BillingPage/AiCreditsPage, `Plan.$fillable`, `AgencyStatsWidget`, `PlanUpsellWidget`
