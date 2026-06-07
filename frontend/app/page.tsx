import React from "react";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LinkBayCMS — Commerce infrastructure for agencies",
  description:
    "One dashboard to manage all your clients' stores. White-label under your brand, recurring revenue from client subscriptions, reusable layouts and AI assistants.",
  keywords:
    "agency commerce platform, white-label ecommerce, client store management, recurring revenue agency",
  openGraph: {
    title: "LinkBayCMS — Commerce infrastructure for agencies",
    description:
      "One dashboard to manage all your clients' stores. White-label under your brand, recurring revenue from client subscriptions.",
  },
};

const WaveTop = () => (
  <div className="left-0 w-full overflow-hidden">
    <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
      <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" className="fill-red-500" />
      <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" className="fill-red-500" />
      <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-red-600" />
    </svg>
  </div>
);

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden">
      <WaveTop />

      {/* ── Hero ─────────────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">

          <div className="mb-8">
            <span className="inline-block px-4 py-2 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
              Commerce infrastructure for agencies
            </span>
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 mb-6 leading-tight font-linkbay">
            LinkBay<span className="text-red-600">CMS</span><sup aria-label="marchio registrato" className="text-[0.28em] align-super font-normal text-gray-400 ml-1 leading-none">®</sup>
          </h1>

          <p className="text-2xl md:text-3xl text-gray-700 mb-4 font-light">
            One control deck for all your clients&rsquo; stores.
          </p>

          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10 leading-relaxed">
            Manage every client store from a single agency dashboard.
            Deploy under your own brand. Charge clients recurring subscriptions.
            Reuse layouts instead of rebuilding from scratch.
            Let AI handle the repetitive work.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/contact"
              className="px-8 py-4 text-lg font-bold rounded-xl bg-red-600 text-white hover:bg-red-700 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              Talk to our team
            </Link>
            <Link
              href="/pricing"
              className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-gray-300 text-gray-700 hover:border-red-600 hover:text-red-600 transition-all duration-300"
            >
              See plans &amp; pricing
            </Link>
          </div>

          <div className="mt-6 text-gray-400 text-sm italic font-[Electrolize]">
            &ldquo;I dock your dream, then set it sail&rdquo;
          </div>
        </div>
      </section>

      {/* ── Who it&rsquo;s for ─────────────────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Built for the people who build for others
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              LinkBayCMS is designed for agencies and studios that manage commerce on behalf of their clients.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: "🏢",
                title: "Digital & marketing agencies",
                body: "Deliver commerce infrastructure to clients without building or maintaining it yourself. Set up a store, hand it over, and charge monthly.",
              },
              {
                icon: "💻",
                title: "Web & SaaS studios",
                body: "Add commerce capabilities to your service stack. Everything runs under your studio&rsquo;s brand — clients never see the platform underneath.",
              },
              {
                icon: "🏷️",
                title: "Multi-brand operators",
                body: "Run separate store identities for different brands or markets from a single back-office. One login, one overview, full isolation between brands.",
              },
            ].map((c) => (
              <div key={c.title} className="text-center p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
                <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">{c.icon}</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{c.title}</h3>
                <p className="text-gray-600" dangerouslySetInnerHTML={{ __html: c.body }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How agencies earn ─────────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-14 items-center">
            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
                Recurring revenue model
              </span>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Turn every client store into a monthly income stream
              </h2>
              <ul className="space-y-5">
                {[
                  "You configure subscription plans for your clients and charge them monthly — on your own terms.",
                  "Each client pays you for their store. That turns a one-off project into a predictable recurring fee.",
                  "LinkBayCMS takes a transparent platform share on what your clients pay you. The exact percentage is published per plan — no surprises.",
                  "The more clients you grow, the more you earn. Our incentive is directly aligned with yours.",
                ].map((t, i) => (
                  <li key={i} className="flex items-start">
                    <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center mr-3 mt-0.5 shrink-0">
                      <span className="text-red-600 text-sm font-bold">{i + 1}</span>
                    </div>
                    <span className="text-gray-700">{t}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link href="/pricing" className="text-red-600 font-semibold hover:underline">
                  See how platform shares work per plan →
                </Link>
              </div>
            </div>

            <div className="bg-gradient-to-br from-red-50 to-white rounded-2xl p-8 border border-red-100">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Example: an agency on the Pro plan</h3>
              <div className="space-y-4">
                {[
                  { label: "Agency plan", value: "Pro — €79/mo" },
                  { label: "Client stores", value: "10 active clients" },
                  { label: "Agency charges per client", value: "€50/mo (your choice)" },
                  { label: "Monthly client revenue", value: "€500" },
                  { label: "Platform share (20%)", value: "−€100" },
                  { label: "Agency net (before plan fee)", value: "€400/mo" },
                ].map((row) => (
                  <div key={row.label} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                    <span className="text-gray-600 text-sm">{row.label}</span>
                    <span className={`font-semibold text-sm ${row.value.startsWith("−") ? "text-red-500" : row.label.includes("net") ? "text-green-600" : "text-gray-900"}`}>
                      {row.value}
                    </span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-4">
                Illustrative example only. Your pricing to clients is entirely your own.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── White-label & branding ────────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
              White-label & branding
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Your brand. Their experience.
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Clients see your logo and your domain. LinkBayCMS stays invisible if you want it that way.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: "🌐", title: "Custom domains", body: "Deploy each client store on a subdomain or a fully custom domain that belongs to you or your client." },
              { icon: "🎨", title: "Logos & colours", body: "Upload your agency logo, set brand colours, and configure email templates. Every touchpoint reflects your identity." },
              { icon: "👁️", title: "Hidden platform", body: "On Pro and Business plans, LinkBayCMS branding is removed entirely. Your clients see only your brand." },
              { icon: "📧", title: "Branded emails", body: "Transactional emails sent to store owners and end customers go out under your domain and name." },
            ].map((c) => (
              <div key={c.title} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <div className="text-3xl mb-4">{c.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{c.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{c.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Less repetition ───────────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-14 items-center">
            <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-200">
              <div className="space-y-4">
                {[
                  { icon: "📐", text: "Save a layout once, reuse it across any client store." },
                  { icon: "⚡", text: "Clone sections, pages, or entire store structures." },
                  { icon: "🤖", text: "AI drafts product copy, fills collections, and duplicates patterns." },
                  { icon: "✅", text: "You review and approve everything. AI handles the volume." },
                ].map((item) => (
                  <div key={item.text} className="flex items-start gap-4 p-4 bg-white rounded-xl border border-gray-100">
                    <span className="text-2xl">{item.icon}</span>
                    <span className="text-gray-700">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <span className="inline-block px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-4">
                Less repetition
              </span>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Stop rebuilding the same store from scratch
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-4">
                Agencies waste hours reproducing the same layouts, sections, and copy for each new client.
                LinkBayCMS gives you a layer to save those patterns and reuse them — with AI filling in the variable parts.
              </p>
              <p className="text-gray-600 text-lg leading-relaxed">
                Faster delivery per client. Consistent quality across your portfolio. More time for the work that actually requires your expertise.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Why agencies pick LinkBayCMS ─────────────────────────────────────────── */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why agencies pick LinkBay
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                problem: "Scattered tools, no central view",
                solution: "One dashboard for every client store",
                body: "Stop jumping between different platforms, spreadsheets, and login credentials. Every store, every client, every status — in one place.",
              },
              {
                problem: "One-off project revenue",
                solution: "Predictable monthly income",
                body: "Each store you deliver becomes a subscription. The client pays monthly, you build a revenue base instead of chasing new projects.",
              },
              {
                problem: "Rebuilding from zero each time",
                solution: "Reusable layouts + AI assistance",
                body: "Save the patterns that work. Reuse them across clients. AI handles the content work so you spend time on decisions, not data entry.",
              },
            ].map((c) => (
              <div key={c.problem} className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
                <div className="text-sm text-red-500 font-semibold mb-1 uppercase tracking-wide">
                  Before
                </div>
                <p className="text-gray-500 line-through mb-4 text-sm">{c.problem}</p>
                <div className="text-sm text-green-600 font-semibold mb-1 uppercase tracking-wide">
                  With LinkBay
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">{c.solution}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{c.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────────────────────────── */}
      <section className="relative bg-gradient-to-r from-gray-900 to-red-900 text-white py-20">
        <div className="absolute top-0 left-0 w-full overflow-hidden">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
            <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" className="fill-white" />
            <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" className="fill-white" />
            <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-white" />
          </svg>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to run all your client stores from one place?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Talk to us about your agency setup. We&rsquo;ll show you what a white-label rollout looks like.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/contact" className="px-8 py-4 text-lg font-bold rounded-xl bg-white text-red-600 hover:bg-gray-100 shadow-lg transition-all duration-300">
              Talk to our team
            </Link>
            <Link href="/pricing" className="px-8 py-4 text-lg font-bold rounded-xl border-2 border-white text-white hover:bg-white hover:text-red-600 transition-all duration-300">
              See plans &amp; pricing
            </Link>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 w-full overflow-hidden rotate-180">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="relative w-full h-16 md:h-24">
            <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="fill-[#343a4D]" />
          </svg>
        </div>
      </section>
    </main>
  );
}
