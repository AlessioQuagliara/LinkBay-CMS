import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing — LinkBay",
  description:
    "Pricing for agencies and their client portfolios. Starter €29, Pro €79, Business €199. Transparent platform shares, no hidden fees.",
  keywords: "agency pricing, white-label commerce pricing, client subscription plans, platform fee",
};

type Plan = {
  name: string;
  price: string;
  period: string;
  bestFor: string;
  maxStores: string;
  transactionFee: string;
  platformShare: string;
  whiteLabel: boolean;
  customDomain: boolean;
  aiCredits: string;
  layoutManager: boolean;
  marketplaceAccess: boolean;
  prioritySupport: boolean;
  ctaLabel: string;
  ctaHref: string;
  highlight?: boolean;
};

const plans: Plan[] = [
  {
    name: "Starter",
    price: "€29",
    period: "/month",
    bestFor: "Small agencies starting with a handful of client stores.",
    maxStores: "Up to 5 client stores",
    transactionFee: "2.5% on store transactions",
    platformShare: "30% of client subscription payments",
    whiteLabel: false,
    customDomain: false,
    aiCredits: "Not included",
    layoutManager: false,
    marketplaceAccess: false,
    prioritySupport: false,
    ctaLabel: "Contact sales about Starter",
    ctaHref: "/contact",
  },
  {
    name: "Pro",
    price: "€79",
    period: "/month",
    bestFor: "Growing agencies managing up to 20 client stores who need full white-label.",
    maxStores: "Up to 20 client stores",
    transactionFee: "1.5% on store transactions",
    platformShare: "20% of client subscription payments",
    whiteLabel: true,
    customDomain: false,
    aiCredits: "5,000 credits/month",
    layoutManager: false,
    marketplaceAccess: true,
    prioritySupport: false,
    ctaLabel: "Contact sales about Pro",
    ctaHref: "/contact",
    highlight: true,
  },
  {
    name: "Business",
    price: "€199",
    period: "/month",
    bestFor: "Established agencies with large or fast-growing client portfolios.",
    maxStores: "Unlimited client stores",
    transactionFee: "0.5% on store transactions",
    platformShare: "10% of client subscription payments",
    whiteLabel: true,
    customDomain: true,
    aiCredits: "20,000 credits/month",
    layoutManager: true,
    marketplaceAccess: true,
    prioritySupport: true,
    ctaLabel: "Contact sales about Business",
    ctaHref: "/contact",
  },
];

const Check = ({ ok }: { ok: boolean }) =>
  ok ? (
    <span className="text-green-600 font-semibold">✓</span>
  ) : (
    <span className="text-gray-300">—</span>
  );

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50 pb-16">

      {/* ── Header ────────────────────────────────────────────────────────────── */}
      <div className="relative bg-[#343a4D] text-white overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor" />
            <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" fill="currentColor" />
          </svg>
        </div>

        <section className="relative py-16 max-w-4xl mx-auto text-center px-4">
          <div className="inline-flex items-center mb-4 bg-[#ff5758] px-4 py-2 rounded-full text-sm font-semibold">
            <span className="mr-2">⚓</span> Agency pricing
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold mb-5">
            Pricing for agencies and their client portfolios
          </h1>

          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            You pay for your agency&rsquo;s access to the platform. You earn by setting your own subscription
            plans for clients. LinkBayCMS takes a transparent platform share on what your clients pay you —
            the exact percentage is shown per plan below.
          </p>
        </section>
      </div>

      {/* ── How it works callout ─────────────────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-4 pt-12 pb-2">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 grid md:grid-cols-3 gap-6 text-center shadow-sm">
          {[
            { icon: "💳", title: "Your agency pays", body: "A monthly plan fee to LinkBayCMS (€29 – €199) for platform access and infrastructure." },
            { icon: "💰", title: "Your clients pay you", body: "Monthly subscriptions for their stores, priced however you choose." },
            { icon: "🤝", title: "LinkBayCMS takes a share", body: "A transparent platform share on what your clients pay you. Lower on higher plans." },
          ].map((c) => (
            <div key={c.title}>
              <div className="text-3xl mb-2">{c.icon}</div>
              <h3 className="font-bold text-gray-900 mb-1 text-sm">{c.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{c.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Plan cards ───────────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border-2 p-8 shadow-lg transition-all duration-300
                ${plan.highlight
                  ? "border-[#ff5758] bg-gradient-to-b from-white to-red-50 scale-105"
                  : "border-gray-200 bg-white hover:border-red-200"
                }`}
            >
              {plan.highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="bg-[#ff5758] text-white px-5 py-1.5 rounded-full font-bold text-sm">
                    Most popular
                  </div>
                </div>
              )}

              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-[#343a4D] mb-2">{plan.name}</h2>
                <div className="flex items-end justify-center mb-3">
                  <span className="text-4xl font-bold text-[#343a4D]">{plan.price}</span>
                  <span className="text-gray-500 ml-1 text-lg">{plan.period}</span>
                </div>
                <p className="text-gray-600 text-sm">{plan.bestFor}</p>
              </div>

              <div className="space-y-3 mb-8">
                <div className="flex items-start gap-3 py-2 border-b border-gray-100">
                  <span className="text-[#ff5758] text-lg">⚓</span>
                  <span className="text-gray-700 text-sm font-medium">{plan.maxStores}</span>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">White-label</div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Check ok={plan.whiteLabel} />
                    <span>{plan.whiteLabel ? "LinkBayCMS branding hidden" : "LinkBayCMS branding visible"}</span>
                  </div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Custom domain for agency panel</div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Check ok={plan.customDomain} />
                    <span>{plan.customDomain ? "Included" : "Not included"}</span>
                  </div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Platform share on client payments</div>
                  <div className="text-sm font-semibold text-[#343a4D]">{plan.platformShare}</div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Transaction fee on store sales</div>
                  <div className="text-sm text-gray-700">{plan.transactionFee}</div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">AI credits</div>
                  <div className="text-sm text-gray-700">{plan.aiCredits}</div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Layout manager</div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Check ok={plan.layoutManager} />
                    <span>{plan.layoutManager ? "Included" : "Not included"}</span>
                  </div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Marketplace (themes &amp; plugins)</div>
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <Check ok={plan.marketplaceAccess} />
                    <span>{plan.marketplaceAccess ? "Included" : "Not included"}</span>
                  </div>
                </div>

                <div className="py-2">
                  <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Support</div>
                  <div className="text-sm text-gray-700">{plan.prioritySupport ? "Priority support" : "Standard support"}</div>
                </div>
              </div>

              <Link
                href={plan.ctaHref}
                className={`w-full block py-3 px-6 rounded-xl font-bold text-center transition-colors
                  ${plan.highlight
                    ? "bg-[#ff5758] text-white hover:bg-[#e04e4f]"
                    : "bg-[#343a4D] text-white hover:bg-[#ff5758]"
                  }`}
              >
                {plan.ctaLabel}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ── Platform share explainer ─────────────────────────────────────────── */}
      <section className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
          <h2 className="text-xl font-bold text-[#343a4D] mb-4">How the platform share works</h2>
          <p className="text-gray-600 text-sm leading-relaxed mb-4">
            The platform share is LinkBay&rsquo;s cut of the subscription revenue your clients pay you.
            It is calculated on the amount you collect from clients, not on your LinkBayCMS plan fee.
          </p>
          <p className="text-gray-600 text-sm leading-relaxed mb-4">
            Example: on the Pro plan (20% share), if you charge 10 clients €50/month each, you collect €500.
            LinkBayCMS takes €100. You keep €400 — minus the €79 plan fee — netting €321 before your own costs.
          </p>
          <p className="text-gray-600 text-sm leading-relaxed">
            The platform share decreases as you move up in plans. This is intentional: as your agency grows
            and manages more clients, the share you keep increases.
          </p>
          <div className="mt-4 p-4 bg-gray-50 rounded-lg text-xs text-gray-500">
            Transaction fees (2.5% / 1.5% / 0.5%) apply separately on product purchases made by end customers
            inside each store — these are distinct from the subscription platform share.
          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────────────────────────── */}
      <section className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-gradient-to-r from-[#343a4D] to-[#ff5758] rounded-2xl p-10 text-white text-center">
          <h2 className="text-2xl font-bold mb-3">Not sure which plan fits?</h2>
          <p className="mb-6 text-gray-200 max-w-lg mx-auto">
            Tell us about your agency and how many client stores you manage today.
            We&rsquo;ll help you figure out the right starting point.
          </p>
          <Link
            href="/contact"
            className="inline-block px-8 py-3 font-bold rounded-xl bg-white text-[#343a4D] hover:bg-gray-100 transition-colors"
          >
            Talk to our team
          </Link>
        </div>
      </section>
    </main>
  );
}
