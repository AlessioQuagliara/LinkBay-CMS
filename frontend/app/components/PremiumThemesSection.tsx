import Link from "next/link";
import { ThemeCard, type ThemeData } from "./ThemeCard";

// ── Theme data ────────────────────────────────────────────────────────────────
// Palette values mirror the defaultConfig registered in PremiumThemePackServiceProvider
// and CoreThemesServiceProvider on the backend.

const THEMES: ThemeData[] = [
  {
    key: "midnight",
    name: "Midnight",
    tagline: "Dark premium, sharp and contemporary.",
    useCase:
      "Tech brands, high-perception projects, and modern launch pages that want a stronger, more distinct presence.",
    palette: {
      primary: "#818cf8",
      accent: "#c084fc",
      surface: "#0f172a",
      text: "#e2e8f0",
    },
  },
  {
    key: "noir",
    name: "Noir",
    tagline: "Editorial luxury. Gold on black, sophisticated tone.",
    useCase:
      "Fashion, premium branding, and high-perception visual contexts where every detail signals quality.",
    palette: {
      primary: "#d4af37",
      accent: "#f5e6a3",
      surface: "#0a0a0a",
      text: "#f5f5f5",
    },
  },
  {
    key: "atelier",
    name: "Atelier",
    tagline: "Warm and artisanal. Terracotta on cream.",
    useCase:
      "Creative agencies, consultancies, and brands that want a more human, considered tone for their storefront.",
    palette: {
      primary: "#c4704f",
      accent: "#e8a87c",
      surface: "#fdf6f0",
      text: "#2d1b0e",
    },
  },
  {
    key: "meridian",
    name: "Meridian",
    tagline: "Corporate B2B precision. Navy on white, electric blue accent.",
    useCase:
      "SaaS, fintech, and enterprise projects where clarity and trust matter more than visual effect.",
    palette: {
      primary: "#1e3a5f",
      accent: "#3b82f6",
      surface: "#ffffff",
      text: "#1e293b",
    },
  },
];

// ── Supporting data ───────────────────────────────────────────────────────────

const BENEFITS = [
  "Stronger branding from day one of each store delivery.",
  "Faster turnaround when working across multiple tenants or clients.",
  "Consistent experience between agency panel and storefront.",
  "Centralised access control via a single entitlement.",
  "Safe rendering fallback — no broken payloads, no 500 errors.",
];

const HOW_STEPS = [
  {
    step: "1",
    title: "One entitlement, four themes",
    body: "Request access to the pack. All four premium themes become available in the agency panel — no separate SKUs to manage in v1.",
  },
  {
    step: "2",
    title: "Choose and assign",
    body: "Each agency picks the best-fit theme per store. Premium themes only appear in the panel when access is active — no confusing locked states.",
  },
  {
    step: "3",
    title: "Automatic fallback",
    body: "If access is revoked, storefront rendering falls back to a free system theme. Nothing breaks, no manual intervention needed.",
  },
];

// ── Component ─────────────────────────────────────────────────────────────────

export function PremiumThemesSection() {
  return (
    <>
      {/* ── 1. Hero ────────────────────────────────────────────────────────────── */}
      <section id="premium-themes" className="scroll-mt-20 bg-white py-20">
        <div className="mx-auto max-w-4xl px-4 text-center">
          <div className="mb-6">
            <span className="inline-block rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-700">
              <span aria-hidden="true">★</span> Premium Design &amp; Themes
            </span>
          </div>
          <h2 className="mb-5 text-3xl font-bold leading-tight text-gray-900 md:text-4xl">
            Give your tenants a stronger visual identity
            <br className="hidden md:block" /> without rebuilding every storefront from scratch.
          </h2>
          <p className="mx-auto max-w-2xl text-lg leading-relaxed text-gray-600">
            Four premium themes. One entitlement. The same rendering engine.
            More perceived quality for the end client — less repetitive work for your team.
          </p>
        </div>
      </section>

      {/* ── 2. Why it matters ──────────────────────────────────────────────────── */}
      <section className="bg-gray-50 py-20">
        <div className="mx-auto max-w-7xl px-4">
          <div className="grid items-start gap-14 md:grid-cols-2">
            <div>
              <span className="mb-5 inline-block rounded-full bg-red-100 px-3 py-1 text-sm font-semibold text-red-700">
                Why it matters
              </span>
              <h3 className="mb-5 text-2xl font-bold text-gray-900">
                From &ldquo;technically correct&rdquo; to
                <br /> &ldquo;professionally branded.&rdquo;
              </h3>
              <p className="mb-4 leading-relaxed text-gray-600">
                Not every project needs a custom theme built from zero. Most need a credible,
                polished base they can adapt — so the team can deliver faster without dropping
                quality.
              </p>
              <p className="leading-relaxed text-gray-600">
                Premium themes in LinkBay are exactly that: a way to close the gap between
                technical correctness and perceived value, without adding unnecessary complexity to
                your workflow.
              </p>
            </div>

            <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
              <h4 className="mb-5 text-sm font-bold uppercase tracking-wide text-gray-900">
                Concrete benefits
              </h4>
              <ul className="space-y-4">
                {BENEFITS.map((benefit) => (
                  <li key={benefit} className="flex items-start">
                    <div className="mr-3 mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100">
                      <span className="text-xs text-red-600" aria-hidden="true">
                        ✓
                      </span>
                    </div>
                    <span className="text-sm text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ── 3. Theme grid ──────────────────────────────────────────────────────── */}
      <section className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4">
          <div className="mb-14 text-center">
            <h3 className="mb-3 text-2xl font-bold text-gray-900">Available themes</h3>
            <p className="mx-auto max-w-xl text-gray-600">
              Each theme has a distinct personality and intended use case. All share the same
              rendering engine and the same single entitlement.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {THEMES.map((theme) => (
              <ThemeCard key={theme.key} theme={theme} />
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. How it works + soft CTA ─────────────────────────────────────────── */}
      <section className="bg-gray-50 py-20">
        <div className="mx-auto max-w-5xl px-4">
          <div className="mb-12 text-center">
            <h3 className="mb-3 text-2xl font-bold text-gray-900">How it works</h3>
            <p className="mx-auto max-w-xl text-gray-600">
              Access is controlled consistently across panel visibility, operational flow, and
              storefront rendering — with automatic fallback if entitlement changes.
            </p>
          </div>

          <div className="mb-16 grid gap-8 md:grid-cols-3">
            {HOW_STEPS.map((s) => (
              <div
                key={s.step}
                className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm"
              >
                <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-xl bg-red-600 text-sm font-bold text-white">
                  {s.step}
                </div>
                <h4 className="mb-2 font-bold text-gray-900">{s.title}</h4>
                <p className="text-sm leading-relaxed text-gray-600">{s.body}</p>
              </div>
            ))}
          </div>

          {/* Soft CTA */}
          <div className="text-center">
            <p className="mx-auto mb-7 max-w-lg text-sm text-gray-500">
              Built for teams managing multiple projects in parallel. Design as an operational
              asset, not a variable you negotiate on every delivery.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link
                href="/pricing"
                className="rounded-xl bg-red-600 px-7 py-3 text-base font-bold text-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:bg-red-700 hover:shadow-md"
              >
                See plans &amp; pricing
              </Link>
              <Link
                href="/contact"
                className="rounded-xl border-2 border-gray-300 px-7 py-3 text-base font-bold text-gray-700 transition-all duration-200 hover:border-red-600 hover:text-red-600"
              >
                Talk to our team
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
