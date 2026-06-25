import Link from "next/link";

// ── Data ──────────────────────────────────────────────────────────────────────

type AddOn = {
  id: string;
  name: string;
  badge: string;
  badgeStyle: string;
  tagline: string;
  audience: string;
  unlocks: string[];
  outcome: string;
};

const ADD_ONS: AddOn[] = [
  {
    id: "editorial",
    name: "Editorial Pack",
    badge: "Add-on",
    badgeStyle: "bg-violet-100 text-violet-700 border border-violet-200",
    tagline: "For clients where aesthetics is a differentiator.",
    audience: "Fashion, lifestyle, food premium, brand-driven projects.",
    unlocks: [
      "Midnight and Noir premium themes",
      "Per-client fork of each theme",
      "High-contrast palettes, editorial layouts",
    ],
    outcome:
      "Deliver a storefront that looks like it came from a design studio — not a template engine.",
  },
  {
    id: "business",
    name: "Business Pack",
    badge: "Add-on",
    badgeStyle: "bg-blue-100 text-blue-700 border border-blue-200",
    tagline: "Faster onboarding. More professional result.",
    audience: "SMEs, generalist shops, multi-location brands, local services.",
    unlocks: [
      "Atelier and Meridian premium themes",
      "Conversion-optimised layouts",
      "Per-client fork of each theme",
    ],
    outcome:
      "A professional starting point that doesn't need hours of customisation before it's presentable.",
  },
  {
    id: "marketing",
    name: "Marketing Block Pack",
    badge: "Add-on",
    badgeStyle: "bg-emerald-100 text-emerald-700 border border-emerald-200",
    tagline: "Build campaigns without opening a code editor.",
    audience:
      "Agencies managing storefronts with active promotions, seasonal activity, or frequent launches.",
    unlocks: [
      "Countdown timer block",
      "Promo banner block",
      "Video hero block",
      "Testimonials with star rating",
      "Feature comparison grid",
    ],
    outcome:
      "Publish campaign pages without a custom dev request. No extra hours to justify to the client.",
  },
];

const BUNDLE_INCLUDES = [
  "All 4 premium themes — Midnight, Noir, Atelier, Meridian",
  "Per-client fork of any premium theme",
  "Marketing blocks: countdown, promo banner, video hero, testimonials",
  "Applies across all your managed client stores",
  "Automatic fallback — nothing breaks if access is removed",
];

type PricingModelItem = {
  label: string;
  title: string;
  labelStyle: string;
  body: string;
};

const PRICING_MODEL: PricingModelItem[] = [
  {
    label: "Always included",
    labelStyle: "bg-gray-100 text-gray-600",
    title: "Core Platform",
    body: "Your agency plan covers multi-tenant management, the layout builder, core blocks, and free themes. The platform works as a standalone product — no add-on required.",
  },
  {
    label: "Per agency, flat",
    labelStyle: "bg-blue-100 text-blue-700",
    title: "Individual add-ons",
    body: "Each pack is a flat monthly add-on for your agency — not calculated per client store. One subscription unlocks the pack across all the projects you manage.",
  },
  {
    label: "Recommended",
    labelStyle: "bg-red-100 text-red-700",
    title: "Design Acceleration Bundle",
    body: "All three packs combined at a lower total price than purchasing separately. The sensible choice when you manage four or more active client projects with varied design needs.",
  },
];

// ── Component ─────────────────────────────────────────────────────────────────

export function PremiumPacksSection() {
  return (
    <>
      {/* ── 1. Section intro ────────────────────────────────────────────────── */}
      <section
        id="premium-packs"
        className="scroll-mt-20 bg-white py-20"
        aria-labelledby="premium-packs-heading"
      >
        <div className="mx-auto max-w-4xl px-4 text-center">
          <div className="mb-6">
            <span className="inline-block rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-700">
              <span aria-hidden="true">★ </span>Premium Add-ons
            </span>
          </div>
          <h2
            id="premium-packs-heading"
            className="mb-5 text-3xl font-bold leading-tight text-gray-900 md:text-4xl"
          >
            Add-ons that make the difference
            <br className="hidden md:block" /> on the projects where it matters.
          </h2>
          <p className="mx-auto max-w-2xl text-lg leading-relaxed text-gray-600">
            Premium packs are not &ldquo;extra themes.&rdquo; They are a way to accelerate
            delivery, differentiate per client, and give your agency a broader range without
            building everything custom from scratch. Core platform is always included — add only
            what you actually need.
          </p>
        </div>
      </section>

      {/* ── 2. Add-on cards ─────────────────────────────────────────────────── */}
      <section className="bg-gray-50 pb-6 pt-16" aria-label="Individual add-ons">
        <div className="mx-auto max-w-7xl px-4">
          <div className="grid gap-6 md:grid-cols-3">
            {ADD_ONS.map((pack) => (
              <article
                key={pack.id}
                className="flex flex-col rounded-2xl border border-gray-200 bg-white p-8 shadow-sm"
              >
                <div className="mb-5">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${pack.badgeStyle}`}
                  >
                    {pack.badge}
                  </span>
                </div>

                <h3 className="mb-2 text-xl font-bold text-[#343a4D]">{pack.name}</h3>
                <p className="mb-6 text-sm italic leading-relaxed text-gray-500">{pack.tagline}</p>

                <div className="mb-5">
                  <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400">
                    Best for
                  </div>
                  <p className="text-sm text-gray-700">{pack.audience}</p>
                </div>

                <div className="mb-6 flex-1">
                  <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                    What it unlocks
                  </div>
                  <ul className="space-y-2">
                    {pack.unlocks.map((item) => (
                      <li key={item} className="flex items-start gap-2.5">
                        <span
                          className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-red-100 text-[10px] text-red-600"
                          aria-hidden="true"
                        >
                          ✓
                        </span>
                        <span className="text-sm text-gray-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-xl bg-gray-50 p-4">
                  <p className="text-sm leading-relaxed text-gray-700">{pack.outcome}</p>
                </div>
              </article>
            ))}
          </div>

          {/* ── Bundle card ───────────────────────────────────────────────────── */}
          <div className="mt-6 rounded-2xl border-2 border-[#ff5758] bg-[#343a4D] p-8 text-white shadow-lg md:p-10">
            <div className="grid items-start gap-10 md:grid-cols-2">
              <div>
                <div className="mb-4">
                  <span className="inline-block rounded-full bg-[#ff5758] px-4 py-1.5 text-xs font-bold uppercase tracking-wide text-white">
                    Recommended Bundle
                  </span>
                </div>
                <h3 className="mb-3 text-2xl font-bold">Design Acceleration Bundle</h3>
                <p className="mb-5 leading-relaxed text-gray-300">
                  Editorial Pack + Business Pack + Marketing Block Pack. One subscription that covers
                  your full delivery range — without having to evaluate which add-on applies to each
                  new project.
                </p>
                <p className="text-sm text-gray-400">
                  Combined price lower than purchasing individual packs separately. Available on Pro
                  and Business agency plans.
                </p>
              </div>

              <div>
                <ul className="mb-7 space-y-3">
                  {BUNDLE_INCLUDES.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <span
                        className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/20 text-xs text-white"
                        aria-hidden="true"
                      >
                        ✓
                      </span>
                      <span className="text-sm text-gray-200">{item}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/contact"
                  className="inline-block rounded-xl bg-[#ff5758] px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-[#e04e4f]"
                >
                  Ask about the bundle →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 3. Pricing model explainer ──────────────────────────────────────── */}
      <section className="bg-white py-16" aria-labelledby="pricing-model-heading">
        <div className="mx-auto max-w-4xl px-4">
          <div className="mb-10 text-center">
            <h2 id="pricing-model-heading" className="mb-3 text-2xl font-bold text-gray-900">
              How add-on pricing works
            </h2>
            <p className="mx-auto max-w-xl text-sm leading-relaxed text-gray-600">
              No per-store variables. No usage tiers. You pay once per agency and the access applies
              across all your projects.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {PRICING_MODEL.map((item) => (
              <div
                key={item.title}
                className="rounded-2xl border border-gray-100 bg-gray-50 p-6"
              >
                <div className="mb-4">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${item.labelStyle}`}
                  >
                    {item.label}
                  </span>
                </div>
                <h3 className="mb-2 font-bold text-gray-900">{item.title}</h3>
                <p className="text-sm leading-relaxed text-gray-600">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. Soft CTA ─────────────────────────────────────────────────────── */}
      <section className="bg-gray-50 py-14">
        <div className="mx-auto max-w-2xl px-4 text-center">
          <h2 className="mb-3 text-xl font-bold text-gray-900">
            Not sure which add-ons fit your current projects?
          </h2>
          <p className="mb-7 text-sm leading-relaxed text-gray-600">
            Tell us about your agency and the types of clients you manage. We&rsquo;ll walk you
            through which packs are worth it now and what makes sense to add later.
          </p>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/contact"
              className="rounded-xl bg-[#343a4D] px-7 py-3 text-sm font-bold text-white transition-all duration-200 hover:bg-[#ff5758]"
            >
              Talk to our team
            </Link>
            <Link
              href="/marketplace"
              className="rounded-xl border-2 border-gray-300 px-7 py-3 text-sm font-bold text-gray-700 transition-all duration-200 hover:border-[#343a4D] hover:text-[#343a4D]"
            >
              Explore the marketplace
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
