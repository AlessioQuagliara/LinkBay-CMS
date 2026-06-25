# LinkBay-CMS — Phase 3 Design Stack

LinkBay-CMS is a multi-tenant B2B e-commerce infrastructure platform designed for agencies, software houses, and established brands that need to manage multiple storefronts, marketplaces, or white-label brands from a single control point. The product already includes a structured multi-tenant backend, authentication and security foundations, subscription logic, a Next.js marketing frontend, and containerized local infrastructure.[web:203]

This document describes the current **Phase 3 Design Stack** of the project in a way that is understandable for technical partners, potential collaborators, and early commercial stakeholders. It focuses on what has been built around themes, layout composition, premium licensing, feature gating, and storefront enforcement.

## What Phase 3 Delivers

Phase 3 turns the design layer of LinkBay-CMS into an operational product capability rather than a purely visual feature. The stack now combines a layout system, a theme engine, a plugin registry, premium licensing, entitlement management, and backend storefront enforcement so that premium design assets can be sold and controlled consistently across admin, agency panel, and runtime storefront rendering.[cite:201][cite:202][web:189]

In practical terms, this means an agency can receive access to premium blocks and premium themes through a controlled entitlement flow, immediately see those assets appear in the panel, and publish storefronts whose final rendered payload respects the same licensing rules at runtime.[cite:202][web:189]

## Core Architecture

The current design stack is built around a few central layers:

- **Layout Manager** for structured page composition.
- **Theme Engine** for reusable storefront presentation logic.
- **Plugin Registry** for centralized registration of blocks and themes.
- **Marketplace / Licensing Foundation** for catalog items and agency entitlements.
- **FeatureAccessService** for unified feature gating decisions.
- **Storefront renderer enforcement** so final output respects premium access rules.[cite:202]

This architecture matters because it avoids the common SaaS anti-pattern of hiding premium UI while leaving backend behavior effectively unrestricted. Secure feature gating requires the underlying API or renderer path to enforce access rules, not just the panel interface.[web:189]

## Premium Themes

Phase 3 now includes a premium theme pack built on top of the existing theme engine. Four premium themes are currently available behind the shared `theme_premium` entitlement: `midnight`, `noir`, `atelier`, and `meridian`.[cite:202]

These themes were introduced as system themes with distinct brand positioning:

| Theme | Positioning | Typical fit |
|------|-------------|-------------|
| Midnight | Dark premium | Modern tech, premium digital brands |
| Noir | Editorial luxury | Fashion, high-end branding, visual-first projects |
| Atelier | Warm artisanal | Creative agencies, consultancy, boutique services |
| Meridian | Corporate B2B | SaaS, fintech, enterprise storefronts |

A single agency entitlement unlocks the full premium pack, which simplifies packaging in v1 and reduces operational friction during onboarding and sales conversations. More granular SKUs can be introduced later if the commercial model requires separate theme bundles.[cite:202]

## Premium Blocks

The design stack also includes a first premium marketing block pack, gated by `block_pack_marketing`. The pack introduces premium layout components such as pricing tables, logo clouds, stats strips, testimonial carousels, and CTA split sections, all registered through the plugin system instead of being hardcoded into the core builder flow.[cite:202]

Access control works on two independent layers. In the agency panel, premium blocks are filtered out of the builder experience when the current agency cannot use the required feature. On the backend, create and edit flows validate submitted blocks again, preventing unauthorized usage through direct request manipulation or DOM tampering.[web:189][cite:202]

## Licensing and Entitlements

The Marketplace / Licensing Foundation is the layer that transforms design assets into controlled commercial capabilities. It is based on catalog items and agency entitlements, making it possible to grant, revoke, expire, and inspect premium access at the agency level without coupling every decision to the subscription plan alone.[cite:201]

This model is aligned with broader SaaS entitlement patterns, where access control is driven by explicit capabilities rather than scattered conditionals or front-end flags. Centralizing feature checks in a dedicated service improves consistency and makes later monetization models easier to extend.[web:178][web:199]

Entitlements can originate from multiple sources such as plan, manual assignment, promotion, or license logic. This gives LinkBay-CMS the flexibility to support both standard pricing tiers and negotiated commercial setups for agencies or strategic partners.[cite:201]

## Storefront Enforcement

A key milestone of Phase 3 is that premium enforcement does not stop at the admin or agency panel. The storefront renderer now applies feature checks before returning the final payload used by the public-facing frontend.[cite:202]

The current fallback strategy is intentionally conservative:

- Premium blocks without access are excluded from the payload.
- Premium system themes without access fall back to default theme configuration.
- Agency custom themes remain renderable because they are treated as agency-owned configuration rather than premium system assets.
- If the tenant-to-agency resolution fails, the renderer falls back safely by excluding premium blocks and using default theme settings.[cite:202]

This approach keeps the storefront payload valid at all times and prevents broken public pages when access changes. It also matches the principle that runtime rendering should be decided by the backend, while frontend feature endpoints are mainly useful for UX hints, upgrade nudges, or conditional messaging.[web:189][cite:202]

## Storefront Features API

LinkBay-CMS also exposes a storefront features endpoint that maps registered feature codes to booleans for a specific tenant context. This allows a Next.js frontend to know which capabilities are active without duplicating business rules in the UI layer.[cite:202]

Because the renderer already filters unauthorized premium content, the frontend does not need to act as the final gatekeeper. The API is useful for presentation logic such as upgrade prompts or optional interface states, but the authoritative enforcement still remains on the backend.[cite:202][web:172]

## Operational Tooling

Phase 3 also improves operational reliability. System catalog items are now seeded automatically from the plugin registry using idempotent seeding logic, with `is_system` used to distinguish framework-provided catalog entries from manually created items. Re-running the seed process updates or creates system records without interfering with manual marketplace items.[cite:201][web:191][web:207]

Automatic entitlement expiration is also handled through a scheduled command, which marks expired entitlements and keeps feature state synchronized over time. Laravel’s scheduler is designed for this kind of recurring operational task and supports protections against overlapping runs.[web:125]

## What This Means for Partners

For a partner, agency, or early customer, this phase demonstrates that LinkBay-CMS is not just a CMS with theme switching. It is becoming a controlled product infrastructure where design assets, tenant branding, premium access, and storefront behavior are all connected through a coherent entitlement model.[cite:202][web:178]

That matters commercially for three reasons:

- Premium features can be packaged and sold without custom code per client.
- White-label agencies can manage multiple brands with stronger design differentiation and central governance.
- Runtime behavior stays aligned with licensing decisions, which reduces operational risk and keeps the commercial model trustworthy.[web:195][web:199][web:189]

## Current Scope and v2 Opportunities

Phase 3 is intentionally pragmatic. It focuses on reliable gating, reusable design assets, and backend consistency rather than polished upsell mechanics or a public marketplace experience.[cite:202]

The most obvious v2 opportunities are:

- Theme previews and richer visual selection in the agency panel.
- Trial or preview mode for premium themes without full entitlement.
- More granular theme pack SKUs instead of one shared `theme_premium` code.
- Agency-friendly theme forking workflows with controlled inheritance from system themes.
- Additional premium block packs built on the same registry and entitlement pattern.[cite:202]

## Positioning Summary

The Phase 3 Design Stack gives LinkBay-CMS a meaningful product advantage: agencies can compose storefronts faster, brand them more credibly, and control premium access centrally without fragmenting the delivery workflow. The implementation is structured enough to scale commercially, while still staying pragmatic in architecture and maintainability.[cite:201][cite:202]
